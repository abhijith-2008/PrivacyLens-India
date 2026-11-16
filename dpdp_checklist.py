"""PrivacyLens: informational DPDP issue-spotting checklist.

Keyword-assisted only. This module does not determine legal compliance.
"""
from __future__ import annotations

import re
from typing import Any

from report import build_report

# Six primary checklist items requested for the project.
# Specific phrases help reduce broad-keyword false positives.
CHECKLIST = [
    {
        "id": "notice",
        "title": "Notice",
        "reference": "DPDP Act, 2023 — Section 5; applicable Rules",
        "why": "Look for a notice explaining the personal data involved and relevant information given to the Data Principal.",
        "terms": [
            "privacy notice", "notice to the data principal",
            "notice to data principals", "we notify you", "we inform you",
            "information provided to you", "notice describing",
        ],
    },
    {
        "id": "consent",
        "title": "Consent",
        "reference": "DPDP Act, 2023 — Section 6; applicable Rules",
        "why": "Look for statements explaining how consent is obtained, managed, or withdrawn.",
        "terms": [
            "your consent", "obtain your consent", "consent is obtained",
            "give your consent", "withdraw your consent", "withdraw consent",
            "consent manager", "you may refuse consent",
        ],
    },
    {
        "id": "purpose",
        "title": "Purpose",
        "reference": "DPDP Act, 2023 — Section 4 and applicable provisions",
        "why": "Look for an explanation of the specific purposes for which personal data is processed.",
        "terms": [
            "for the purpose of", "for the purposes of",
            "we use your information to", "we use your personal data to",
            "we process your personal data to", "used to provide", "used for",
            "to provide our services", "to create and manage your account",
        ],
    },
    {
        "id": "rights",
        "title": "Rights",
        "reference": "DPDP Act, 2023 — Sections 11–14; applicable Rules",
        "why": "Look for information about how a person may exercise applicable rights, such as access to information, correction, erasure, or nomination.",
       "terms": [
            # Access
            "request access to your personal data",
            "access your personal data",
            "request access to your personal information",
            "access to your personal information",
            "right to access",

            # Correction
            "request correction",
            "correct your personal data",
            "correction of your personal data",
            "correction of your personal information",
            "request correction of your personal information",
            "right to correction",

            # Erasure / deletion
            "request erasure",
            "request deletion of your personal data",
            "delete your personal data",
            "deletion of your personal information",
            "deletion of your personal data",
            "right to erasure",

            # General rights
            "exercise your rights",
            "rights of the data principal",

        ],
    },
    {
        "id": "grievance_contact",
        "title": "Grievance contact",
        "reference": "DPDP Act, 2023 — Section 13; applicable Rules",
        "why": "Look for an identified grievance mechanism or grievance contact. A generic support email or 'contact us' phrase alone is not enough.",
        "terms": [
            "grievance officer", "grievance redressal",
            "grievance redressal mechanism", "raise a grievance",
            "submit a grievance", "lodge a complaint", "file a complaint",
            "complaint regarding your personal data",
            "complaints relating to personal data", "data protection grievance",
        ],
    },
    {
        "id": "children_data",
        "title": "Children's data",
        "reference": "DPDP Act, 2023 — Section 9; applicable Rules",
        "why": "Look for statements addressing children's personal data, parental or guardian involvement, or age-related handling where relevant.",
        "terms": [
            "children's personal data", "personal data of children",
            "child's personal data", "personal information of children",
            "parental consent", "consent of a parent",
            "verifiable consent of a parent", "legal guardian",
            "under the age of 18", "under 18 years of age",
        ],
    },
]


def _split_sentences(text: str) -> list[str]:
    """Split text into readable sentence/line excerpts."""
    return [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+|\n+", text)
        if part.strip()
    ]


def _matching_excerpts(text: str, terms: list[str], limit: int = 3) -> list[str]:
    """Return only original sentences/lines that contain specific phrases."""
    patterns = [
        re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        for term in terms
    ]
    hits: list[str] = []
    seen: set[str] = set()

    for piece in _split_sentences(text):
        if any(pattern.search(piece) for pattern in patterns):
            normalized = re.sub(r"\s+", " ", piece).strip()
            if normalized not in seen:
                seen.add(normalized)
                hits.append(normalized[:500] + ("…" if len(normalized) > 500 else ""))
        if len(hits) >= limit:
            break
    return hits


def build_dpdp_checklist(
    policy_text: str, include_model_report: bool = True
) -> dict[str, Any]:
    """Create six informational checklist items and their matching excerpts."""
    if not isinstance(policy_text, str) or not policy_text.strip():
        raise ValueError("Paste some privacy-policy text before creating the checklist.")

    results = []
    for item in CHECKLIST:
        excerpts = _matching_excerpts(policy_text, item["terms"])
        if excerpts:
            status = "Potential evidence found"
            explanation = (
                "The supplied text contains wording related to this topic. "
                "Review the excerpts and their surrounding context."
            )
        else:
            status = "No matching text found"
            explanation = (
                "This keyword-assisted check did not find a matching excerpt. "
                "The topic may be described using different wording, elsewhere "
                "in the full policy, or outside the supplied text."
            )
        results.append(
            {
                "id": item["id"],
                "title": item["title"],
                "reference": item["reference"],
                "why_it_matters": item["why"],
                "status": status,
                "explanation": explanation,
                "evidence": excerpts,
                "manual_review_required": True,
            }
        )

    report = build_report(policy_text) if include_model_report else None
    return {
        "product": "PrivacyLens India",
        "checklist_type": "informational_issue_spotting",
        "disclaimer": (
            "This checklist is an educational aid, not legal advice, a compliance "
            "audit, or a determination that an organization complies with or "
            "violates the DPDP Act or Rules."
        ),
        "checklist": results,
        "model_report": report,
        "limitations": [
            "A keyword match is not proof that a requirement is satisfied.",
            "No matching text is not proof of non-compliance; the excerpt may be "
            "incomplete or use different wording.",
            "A privacy policy alone cannot establish operational practices, valid "
            "consent flows, security effectiveness, or legal applicability.",
            "The OPP-115 model categories are not DPDP compliance labels.",
            "Every checklist item requires human review against the full context "
            "and current official law.",
        ],
    }


if __name__ == "__main__":
    sample = (
        "We collect your email address to create your account. "
        "We use your email to provide our services. "
        "You may withdraw your consent at any time. "
        "You can request correction of your personal data. "
        "If you have a complaint regarding your personal data, contact our "
        "Grievance Officer at grievance@example.com. "
        "We use encryption to protect personal information. "
        "We retain account information for as long as necessary."
    )
    result = build_dpdp_checklist(sample, include_model_report=False)
    for item in result["checklist"]:
        print(f'{item["status"]}: {item["title"]}')
        for excerpt in item["evidence"]:
            print("  Evidence:", excerpt)
