
"""Step 3: user-friendly policy summary and evidence presentation.

This module deliberately uses extractive summaries: it selects sentences from the
user's own text instead of inventing new claims. Category descriptions explain
OPP-115 labels; they do not determine legal compliance.
"""

from __future__ import annotations

import re
import time
from analyzer import PrivacyPolicyAnalyzer, split_policy


CATEGORY_INFO = {
    'First Party Collection/Use': {
        'plain_english': 'How the organization collects personal information and uses it for its own purposes.',
        'questions': [
            'What information is collected?',
            'Why is it used?',
            'Is the purpose clearly explained?'
        ]
    },
    'Third Party Sharing/Collection': {
        'plain_english': 'Whether information is shared with, or collected by, other organizations.',
        'questions': [
            'Who may receive the information?',
            'Are service providers or other third parties mentioned?'
        ]
    },
    'User Choice/Control': {
        'plain_english': 'Choices a person may have about how their information is used or shared.',
        'questions': [
            'Can the person opt out or change preferences?',
            'Are choices and consent options explained?'
        ]
    },
    'Data Security': {
        'plain_english': 'Statements about safeguards intended to protect personal information.',
        'questions': [
            'Does the policy describe security measures?',
            'Does it explain how data is protected?'
        ]
    },
    'User Access, Edit and Deletion': {
        'plain_english': 'Whether people can access, correct, update, or delete information about them.',
        'questions': [
            'Can a person request access or correction?',
            'Does the policy explain deletion requests?'
        ]
    },
    'Data Retention': {
        'plain_english': 'How long information is kept and when it may be deleted.',
        'questions': [
            'Is a retention period stated?',
            'Does the policy explain when information is deleted?'
        ]
    },
    'Policy Change': {
        'plain_english': 'How changes to the privacy policy are communicated.',
        'questions': [
            'How are policy updates announced?',
            'Does the policy explain how users will be notified?'
        ]
    },
    'International and Specific Audiences': {
        'plain_english': 'Statements about international users, children, or other specific audiences.',
        'questions': [
            'Are children or other specific groups discussed?',
            'Is international data handling mentioned?'
        ]
    },
    'Do Not Track': {
        'plain_english': 'Whether the policy discusses Do Not Track browser signals.',
        'questions': [
            'Does the policy address Do Not Track signals?'
        ]
    },
    'Other': {
        'plain_english': 'Privacy-related content that does not fit neatly into the other OPP-115 categories.',
        'questions': [
            'Review the excerpt to understand the specific privacy topic.'
        ]
    }
}


def _sentences(text: str) -> list[str]:
    text = re.sub(r"[ \t]+", " ", text.strip())

    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [part.strip() for part in parts if part.strip()]



def extractive_summary(policy_text: str, max_sentences: int = 5) -> list[str]:
    """Select concise, representative original sentences from the policy."""

    # Split on sentence endings and line breaks.
    raw_sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        policy_text.strip()
    )

    sentences = []

    for sentence in raw_sentences:
        sentence = re.sub(r"^\s*[-*•]+\s*", "", sentence).strip()
        sentence = re.sub(r"\s+", " ", sentence)

        if len(sentence) < 45:
            continue

        if sentence not in sentences:
            sentences.append(sentence)

    if not sentences:
        return []

    topics = {
        "collection": ["collect", "gather", "obtain"],
        "usage": ["use", "process", "purpose"],
        "sharing": ["share", "third party", "disclose"],
        "security": ["security", "protect", "safeguard", "encrypt"],
        "retention": ["retain", "retention", "erase", "delete"],
        "rights": ["access", "correct", "withdraw", "right", "consent"]
    }

    selected = []
    covered_topics = set()

    for topic, keywords in topics.items():
        candidates = [
            sentence for sentence in sentences
            if any(word in sentence.lower() for word in keywords)
            and sentence not in selected
        ]

        if candidates:
            best = max(
                candidates,
                key=lambda sentence: (
                    sum(word in sentence.lower() for word in keywords),
                    -abs(len(sentence) - 180)
                )
            )
            selected.append(best)
            covered_topics.add(topic)

        if len(selected) >= max_sentences:
            break

    return selected



def build_report(
    policy_text: str,
    analyzer: PrivacyPolicyAnalyzer | None = None,
    max_summary_sentences: int = 5
) -> dict:
    """Return a report combining original-text summary and model findings."""

    print("\n========== PRIVACYLENS DEBUG ==========", flush=True)
    print(
        f"Input policy length: {len(policy_text)} characters",
        flush=True
    )

    analyzer = analyzer or PrivacyPolicyAnalyzer()

    # Step 1: ML analysis
    print("DEBUG: Starting ML analysis...", flush=True)

    ml_start = time.time()

    analysis = analyzer.analyze(policy_text)

    ml_time = time.time() - ml_start

    print(
        f"DEBUG: ML analysis completed in {ml_time:.2f} seconds",
        flush=True
    )

    print(
        f"DEBUG: Sections processed: {analysis['section_count']}",
        flush=True
    )

    # Step 2: Extractive summary
    print("DEBUG: Starting summary extraction...", flush=True)

    summary_start = time.time()

    summary = extractive_summary(
        policy_text,
        max_summary_sentences
    )

    summary_time = time.time() - summary_start

    print(
        f"DEBUG: Summary completed in {summary_time:.2f} seconds",
        flush=True
    )

    print(
        f"DEBUG: Summary sentences selected: {len(summary)}",
        flush=True
    )

    for index, sentence in enumerate(summary, 1):
        print(
            f"DEBUG: Sentence {index} ({len(sentence)} characters): {sentence}",
            flush=True
        )

    print("========== DEBUG COMPLETE ==========\n", flush=True)

    # Step 3: Prepare ML findings
    findings = []

    for finding in analysis["findings"]:

        info = CATEGORY_INFO.get(
            finding["category"],
            {
                "plain_english": "A privacy-practice category predicted by the model.",
                "questions": [
                    "Review the excerpt and surrounding policy context."
                ]
            }
        )

        findings.append({
            **finding,
            "plain_english": info["plain_english"],
            "review_questions": info["questions"],
            "evidence": [
                {
                    **ev,
                    "excerpt": ev["text"][:500] + (
                        "…" if len(ev["text"]) > 500 else ""
                    )
                }
                for ev in finding["evidence"]
            ],
        })

    return {
        "summary_type": "extractive",
        "summary_note": (
            "These are selected sentences copied from the supplied policy, "
            "not newly generated claims."
        ),
        "summary_sentences": summary,
        "finding_count": len(findings),
        "findings": findings,
        "sections": analysis["sections"],
        "section_count": analysis["section_count"],
        "threshold": analysis["threshold"],
        "limitations": analysis["limitations"] + [
            "A predicted category is a prompt for review, not proof that a practice is present or absent.",
            "This report is informational and does not provide a legal compliance determination."
        ],
    }
