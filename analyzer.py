
"""
PrivacyLens text-analysis pipeline for pasted privacy policies.

Predictions identify likely OPP-115 privacy-practice categories.
They are not legal advice and do not establish compliance or
non-compliance with Indian law.
"""

from __future__ import annotations

from pathlib import Path
import re
import joblib


DEFAULT_MODEL = (
    Path(__file__).resolve().parent / "privacylens_model.joblib"
)


def split_evidence_sentences(text: str) -> list[str]:
    """Split policy text into cleaner sentence-level evidence candidates."""

    text = re.sub(r"\s+", " ", text.strip())

    # Restore missing spaces after sentence-ending punctuation.
    text = re.sub(r"(?<=[.!?])(?=[A-Z])", " ", text)

    sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z0-9\"'])",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 30
    ]


def split_policy(
    text: str,
    max_chars: int = 1200
) -> list[str]:
    """Split policy text into paragraph/sentence chunks while preserving text."""

    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\t\u00a0 ]+", " ", text)

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n+", text)
        if p.strip()
    ]

    if not paragraphs:
        paragraphs = [
            p.strip()
            for p in text.split("\n")
            if p.strip()
        ]

    chunks: list[str] = []

    for paragraph in paragraphs:

        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue

        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9\"'])",
            paragraph
        )

        current = ""

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            # Split very long individual sentences.
            pieces = [
                sentence[i:i + max_chars]
                for i in range(0, len(sentence), max_chars)
            ]

            for piece in pieces:

                if current and len(current) + 1 + len(piece) > max_chars:
                    chunks.append(current)
                    current = piece

                else:
                    current = f"{current} {piece}".strip()

        if current:
            chunks.append(current)

    return chunks


class PrivacyPolicyAnalyzer:

    def __init__(
        self,
        model_path: str | Path = DEFAULT_MODEL,
        threshold: float | None = None
    ):

        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {model_path}. "
                "Run `python train_model.py` first."
            )

        self.bundle = joblib.load(model_path)

        self.features = self.bundle["features"]
        self.classifier = self.bundle["classifier"]
        self.labels = list(self.bundle["categories"])

        self.threshold = float(
            threshold
            if threshold is not None
            else self.bundle.get("threshold", 0.5)
        )

    def analyze(
        self,
        policy_text: str,
        top_k: int = 3
    ) -> dict:
        """Return section-level predictions and a combined category overview."""

        if not isinstance(policy_text, str) or not policy_text.strip():
            raise ValueError(
                "Paste some privacy-policy text before analyzing."
            )

        # --------------------------------------------------
        # STEP 1: Split policy into sections
        # --------------------------------------------------

        sections = split_policy(policy_text)

        matrix = self.features.transform(sections)

        probabilities = self.classifier.predict_proba(matrix)

        results = []

        category_hits = {
            label: [] for label in self.labels
        }

        category_max = {
            label: 0.0 for label in self.labels
        }

        # --------------------------------------------------
        # STEP 2: Section-level ML predictions
        # --------------------------------------------------

        for section_id, (section, row) in enumerate(
            zip(sections, probabilities),
            start=1
        ):

            ranked = sorted(
                [
                    (label, float(score))
                    for label, score in zip(self.labels, row)
                ],
                key=lambda item: item[1],
                reverse=True
            )

            predicted = [
                (label, score)
                for label, score in ranked
                if score >= self.threshold
            ]

            # Suggestions are shown when no category crosses threshold.
            shown = (
                predicted
                if predicted
                else ranked[:max(1, top_k)]
            )

            results.append({
                "section_id": section_id,

                "text": section,

                "predicted_categories": [
                    {
                        "category": label,
                        "score": round(score, 4)
                    }
                    for label, score in predicted
                ],

                "suggested_categories": [
                    {
                        "category": label,
                        "score": round(score, 4)
                    }
                    for label, score in shown[:max(1, top_k)]
                ],

                "needs_review": len(predicted) == 0,
            })

            # Store paragraph-level predictions.
            for label, score in predicted:

                category_hits[label].append({
                    "section_id": section_id,
                    "score": round(score, 4),
                    "text": section
                })

                category_max[label] = max(
                    category_max[label],
                    score
                )

        # --------------------------------------------------
        # STEP 3: Sentence-level evidence extraction
        # --------------------------------------------------

        findings = []

        for label in self.labels:

            hits = category_hits[label]

            if not hits:
                continue

            evidence_candidates = []

            label_index = self.labels.index(label)

            # Extract and score sentences from predicted sections.
            for hit in hits:

                sentences = split_evidence_sentences(
                    hit["text"]
                )

                if not sentences:
                    continue

                sentence_matrix = self.features.transform(
                    sentences
                )

                sentence_probabilities = (
                    self.classifier.predict_proba(
                        sentence_matrix
                    )
                )

                for sentence, scores in zip(
                    sentences,
                    sentence_probabilities
                ):

                    score = float(scores[label_index])

                    if score >= self.threshold:

                        evidence_candidates.append({
                            "section_id": hit["section_id"],
                            "score": round(score, 4),
                            "text": sentence
                        })

            # --------------------------------------------------
            # STEP 4: Remove duplicate evidence
            # --------------------------------------------------

            unique_evidence = {}

            for item in evidence_candidates:

                normalized_text = " ".join(
                    item["text"].casefold().split()
                )

                if (
                    normalized_text not in unique_evidence
                    or item["score"]
                    > unique_evidence[normalized_text]["score"]
                ):

                    unique_evidence[normalized_text] = item

            # --------------------------------------------------
            # STEP 5: Select top three unique sentences
            # --------------------------------------------------

            best_evidence = sorted(
                unique_evidence.values(),
                key=lambda item: item["score"],
                reverse=True
            )[:3]

            findings.append({
                "category": label,

                "sections_found": len(hits),

                "max_score": round(
                    category_max[label],
                    4
                ),

                "evidence": best_evidence
            })

        # --------------------------------------------------
        # STEP 6: Sort category findings
        # --------------------------------------------------

        findings.sort(
            key=lambda item: (
                -item["sections_found"],
                -item["max_score"],
                item["category"]
            )
        )

        # --------------------------------------------------
        # STEP 7: Return analysis report
        # --------------------------------------------------

        return {
            "section_count": len(sections),

            "threshold": self.threshold,

            "findings": findings,

            "sections": results,

            "limitations": [
                "Categories are predicted from OPP-115 privacy-practice annotations, not DPDP compliance labels.",

                "A category not detected does not prove the policy omits that practice.",

                "Scores are model outputs, not calibrated legal-risk probabilities.",

                "Sentence-level evidence scores are model estimates, not proof of semantic relevance.",

                "Review the highlighted policy text before drawing conclusions.",
            ],
        }


def analyze_policy(
    policy_text: str,
    model_path: str | Path = DEFAULT_MODEL
) -> dict:
    """Convenience wrapper for simple scripts and Streamlit apps."""

    return PrivacyPolicyAnalyzer(
        model_path=model_path
    ).analyze(policy_text)
