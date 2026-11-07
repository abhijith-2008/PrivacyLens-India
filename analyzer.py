"""PrivacyLens text-analysis pipeline for pasted privacy policies.

Predictions identify likely OPP-115 privacy-practice categories. They are not
legal advice and do not establish compliance or non-compliance with Indian law.
"""
from __future__ import annotations
from pathlib import Path
import re
import joblib

DEFAULT_MODEL = Path(__file__).resolve().parent / "privacylens_model.joblib"


def split_policy(text: str, max_chars: int = 1200) -> list[str]:
    """Split policy text into paragraph/sentence chunks while preserving text."""
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\t\u00a0 ]+", " ", text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", paragraph)
        current = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            # Very long individual sentences are hard-split to bound memory/use.
            pieces = [sentence[i:i + max_chars] for i in range(0, len(sentence), max_chars)]
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
    def __init__(self, model_path: str | Path = DEFAULT_MODEL, threshold: float | None = None):
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {model_path}. Run `python train_model.py` first."
            )
        self.bundle = joblib.load(model_path)
        self.features = self.bundle["features"]
        self.classifier = self.bundle["classifier"]
        self.labels = list(self.bundle["categories"])
        self.threshold = float(threshold if threshold is not None else self.bundle.get("threshold", 0.5))

    def analyze(self, policy_text: str, top_k: int = 3) -> dict:
        """Return section-level predictions plus a combined category overview."""
        if not isinstance(policy_text, str) or not policy_text.strip():
            raise ValueError("Paste some privacy-policy text before analyzing.")
        sections = split_policy(policy_text)
        matrix = self.features.transform(sections)
        probabilities = self.classifier.predict_proba(matrix)
        results = []
        category_hits = {label: [] for label in self.labels}
        category_max = {label: 0.0 for label in self.labels}

        for section_id, (section, row) in enumerate(zip(sections, probabilities), start=1):
            ranked = sorted(
                [(label, float(score)) for label, score in zip(self.labels, row)],
                key=lambda item: item[1], reverse=True
            )
            predicted = [(label, score) for label, score in ranked if score >= self.threshold]
            # Keep a small ranked suggestion list even when no score crosses threshold.
            shown = predicted if predicted else ranked[:max(1, top_k)]
            results.append({
                "section_id": section_id,
                "text": section,
                "predicted_categories": [
                    {"category": label, "score": round(score, 4)} for label, score in predicted
                ],
                "suggested_categories": [
                    {"category": label, "score": round(score, 4)} for label, score in shown[:max(1, top_k)]
                ],
                "needs_review": len(predicted) == 0,
            })
            for label, score in predicted:
                category_hits[label].append({"section_id": section_id, "score": round(score, 4), "text": section})
                category_max[label] = max(category_max[label], score)

        findings = []
        for label in self.labels:
            hits = category_hits[label]
            if hits:
                findings.append({
                    "category": label,
                    "sections_found": len(hits),
                    "max_score": round(category_max[label], 4),
                    "evidence": hits[:3],
                })
        findings.sort(key=lambda item: (-item["sections_found"], -item["max_score"], item["category"]))
        return {
            "section_count": len(sections),
            "threshold": self.threshold,
            "findings": findings,
            "sections": results,
            "limitations": [
                "Categories are predicted from OPP-115 privacy-practice annotations, not DPDP compliance labels.",
                "A category not detected does not prove the policy omits that practice.",
                "Scores are model outputs, not calibrated legal-risk probabilities.",
                "Review the highlighted policy text before drawing conclusions.",
            ],
        }


def analyze_policy(policy_text: str, model_path: str | Path = DEFAULT_MODEL) -> dict:
    """Convenience wrapper for simple scripts and Streamlit apps."""
    return PrivacyPolicyAnalyzer(model_path=model_path).analyze(policy_text)
