"""Step 3: user-friendly policy summary and evidence presentation.

This module deliberately uses extractive summaries: it selects sentences from the
user's own text instead of inventing new claims. Category descriptions explain
OPP-115 labels; they do not determine legal compliance.
"""
from __future__ import annotations
import re
from collections import Counter
from analyzer import PrivacyPolicyAnalyzer, split_policy

CATEGORY_INFO = {'First Party Collection/Use': {'plain_english': 'How the organization collects personal information and uses it for its own purposes.', 'questions': ['What information is collected?', 'Why is it used?', 'Is the purpose clearly explained?']}, 'Third Party Sharing/Collection': {'plain_english': 'Whether information is shared with, or collected by, other organizations.', 'questions': ['Who may receive the information?', 'Are service providers or other third parties mentioned?']}, 'User Choice/Control': {'plain_english': 'Choices a person may have about how their information is used or shared.', 'questions': ['Can the person opt out or change preferences?', 'Are choices and consent options explained?']}, 'Data Security': {'plain_english': 'Statements about safeguards intended to protect personal information.', 'questions': ['Does the policy describe security measures?', 'Does it explain how data is protected?']}, 'User Access, Edit and Deletion': {'plain_english': 'Whether people can access, correct, update, or delete information about them.', 'questions': ['Can a person request access or correction?', 'Does the policy explain deletion requests?']}, 'Data Retention': {'plain_english': 'How long information is kept and when it may be deleted.', 'questions': ['Is a retention period stated?', 'Does the policy explain when information is deleted?']}, 'Policy Change': {'plain_english': 'How changes to the privacy policy are communicated.', 'questions': ['How are policy updates announced?', 'Does the policy explain how users will be notified?']}, 'International and Specific Audiences': {'plain_english': 'Statements about international users, children, or other specific audiences.', 'questions': ['Are children or other specific groups discussed?', 'Is international data handling mentioned?']}, 'Do Not Track': {'plain_english': 'Whether the policy discusses Do Not Track browser signals.', 'questions': ['Does the policy address Do Not Track signals?']}, 'Other': {'plain_english': 'Privacy-related content that does not fit neatly into the other OPP-115 categories.', 'questions': ['Review the excerpt to understand the specific privacy topic.']}}

def _sentences(text: str) -> list[str]:
    # Lightweight sentence splitter; preserves the original sentence wording.
    return [s.strip() for s in re.split(r"(?<=[.!?])\\s+(?=[A-Z0-9\\\"'])", text.strip()) if s.strip()]

def extractive_summary(policy_text: str, max_sentences: int = 5) -> list[str]:
    """Select representative original sentences; this is not abstractive generation."""
    sentences = _sentences(re.sub(r"\\s+", " ", policy_text))
    if not sentences:
        return []
    # Give priority to informative sentences with privacy-related terms, while
    # avoiding a result dominated by very short headings or boilerplate.
    terms = {
        "collect", "personal information", "share", "third party", "retain",
        "delete", "security", "consent", "opt out", "access", "correct",
        "child", "update", "purpose", "service provider", "cookie"
    }
    scored = []
    for idx, sentence in enumerate(sentences):
        lower = sentence.lower()
        hits = sum(1 for term in terms if term in lower)
        length_bonus = min(len(sentence), 240) / 240
        score = hits + length_bonus
        if len(sentence) < 35:
            score -= 0.75
        scored.append((score, idx, sentence))
    chosen = sorted(sorted(scored, key=lambda x: (-x[0], x[1]))[:max_sentences], key=lambda x: x[1])
    return [item[2] for item in chosen]

def build_report(policy_text: str, analyzer: PrivacyPolicyAnalyzer | None = None,
                 max_summary_sentences: int = 5) -> dict:
    """Return a report combining original-text summary and model findings."""
    analyzer = analyzer or PrivacyPolicyAnalyzer()
    analysis = analyzer.analyze(policy_text)
    summary = extractive_summary(policy_text, max_summary_sentences)
    findings = []
    for finding in analysis["findings"]:
        info = CATEGORY_INFO.get(finding["category"], {
            "plain_english": "A privacy-practice category predicted by the model.",
            "questions": ["Review the excerpt and surrounding policy context."]
        })
        findings.append({
            **finding,
            "plain_english": info["plain_english"],
            "review_questions": info["questions"],
            "evidence": [
                {**ev, "excerpt": ev["text"][:500] + ("…" if len(ev["text"]) > 500 else "")}
                for ev in finding["evidence"]
            ],
        })
    return {
        "summary_type": "extractive",
        "summary_note": "These are selected sentences copied from the supplied policy, not newly generated claims.",
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
