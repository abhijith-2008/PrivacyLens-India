
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
        "why": (
            "Look for a notice explaining the personal data involved "
            "and relevant information given to the Data Principal."
        ),
      
        "terms": [
            # Explicit privacy policy or notice descriptions
            "this privacy policy explains",
            "this privacy policy describes",
            "this privacy notice explains",
            "this privacy notice describes",
            "this notice explains",
            "this notice describes",
            "this privacy statement outlines",
            "this privacy statement describes",
            "this privacy statement explains",
            "this privacy and cookies policy explains",
            "this privacy and cookies policy describes",
            "this policy explains how we collect",
            "this policy describes how we collect",
            "this policy sets out how we process",
            "this policy explains what personal data",
            "personal data we process and the purposes",
            "categories of information collected",
            "how your personal information is collected and used",
            # Specific notice language identified in the Eternal/Zomato policy
            "types of information that eternal may collect from you",
            "practices for collecting, using, maintaining, protecting and disclosing",
            "this privacy policy outlines eternal and its affiliates",
            "processing of personal information concerning individuals",
            "information we collect and how we use it",
            "information you provide to us",
            "information we collect through automatic data collection technologies",
            "information from third parties",

            # Personal data and collection information
            "personal data we collect",
            "personal information we collect",
            "what personal data we collect",
            "categories of personal data we collect",
            "information we collect from you",
            "details of personal data collected",

            # How personal data is processed
            "how we collect and use your personal data",
            "how we use your personal data",
            "how we process your personal data",
            "how we collect and process your personal information",
            "outlines how paytm collects",
            "how paytm collects, uses, shares",

            # Notice-specific language
            "notice to the data principal",
            "notice to data principals",
            "collection, use, disclosure and protection of your information",
            "please read this policy before using",
        ],

        "exclude_terms": [
            # References to unrelated or separate notices
            "read the phonepe ai connectors privacy notice",

            # Policy-update wording alone is not substantive notice evidence
            "modify this privacy notice",
            "update this privacy notice",
            "changes to this privacy notice",
            "revise this privacy notice",

            # Sharing notification alone is not a complete privacy notice
            "notify you and you consent to the sharing",
        ],
    },

    {
        "id": "consent",
        "title": "Consent",
        "reference": "DPDP Act, 2023 — Section 6; applicable Rules",
        "why": (
            "Look for statements explaining how consent is obtained, "
            "managed, or withdrawn."
        ),
        "terms": [
            # How consent is obtained
            "we process your personal information with consent",
            "we process your personal data with consent",
            "you consent to the processing of your personal information",
            "you consent to the processing of your personal data",
            "by using our services, you consent",
            "by providing your personal information, you consent",
            "obtain your consent",
            "consent is obtained",
            "give your consent",
            "provide your consent",

            # Consent withdrawal
            "you may withdraw your consent",
            "you may at any time revoke consent",
            "withdraw your consent",
            "withdraw consent",
            "revoke your consent",
            "revoke consent",
            # Explicit consent statements
            "you provide your informed consent",
            "you provide your consent to the collection",
            "you expressly consent to our collection",
            "you explicitly consent to its collection",
            "you give your explicit consent",
            "you have such individual's consent",
            "you consent to providing us with such information",
            "by accessing or using our services",
            # Consent management
            "consent manager",
            "manage your consent",
            "manage consent",
            "you may refuse consent",
            "you can refuse consent",
        ],
    },

    {
        "id": "purpose",
        "title": "Purpose",
        "reference": "DPDP Act, 2023 — Section 4 and applicable provisions",
        "why": (
            "Look for an explanation of the specific purposes "
            "for which personal data is processed."
        ),
      "terms": [
            # Explicit purpose statements
            "for the purpose of",
            "for the purposes of",
            "for a variety of regulatory and business purposes",
            "for regulatory and business purposes",
            "for the purposes detailed in this privacy policy",
            "we use your personal data to provide our services",
            # Service and business purposes
            "verify your identity",
            "complete transactions effectively",
            "respond to your request for service or assistance",
            "perform market analysis",
            "market research",
            "enhance customer experience",
            "improve upon service delivery",
            "provide, maintain, personalise and improve",
            "research, develop and market new products",
            "anticipate and resolve issues",
            "promote, market, and facilitate products",
            "ensure adherence to legal and regulatory requirements",
            "prevention and detection of frauds and crimes",

            # Other processing purposes
            "for internal assessments",
            "for analytical purposes",
            "for analysis of the availability",
            "to provide you with a better experience",
            "for security purposes",
            "for the purpose of verification of identity",
            # Specific processing activities
            "we primarily collect your data to provide you the services",
            "administer our services",
            "process and complete your transactions",
            "process and respond to your queries and complaints",
            "detect and prevent fraud",
            "understand our users",
            "improve the content and features of our service",
            "personalize your experience",
            "conduct data analysis",
            "manage the recruitment process",
            "facilitate the requested service",
        ],
    },

    {
        "id": "rights",
        "title": "Rights",
        "reference": "DPDP Act, 2023 — Sections 11–14; applicable Rules",
        "why": (
            "Look for information about how a person may exercise "
            "applicable rights, such as access to information, "
            "correction, erasure, or nomination."
        ),
        "terms": [
            # Access
            "request access to your personal data",
            "access your personal data",
            "request access to your personal information",
            "access to your personal information",
            "right to access",
            "access and review your personal information",
            "access and review your personal data",
            "you want your data to be deleted",
            "your data to be deleted",
            "withdraw your consent for the use and disclosure",
            "please write to us at",
            # Additional deletion and erasure wording
            "you can delete your account",
            "you can delete your account through",
            "right to erasure of your personal data",
            "exercise the right to erasure",
            "until you exercise the right to erasure",

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
            "delete your account or personal information",
            "delete your account or personal data",
            # Account deletion
            "permanently delete your account",
            "requested for deletion of the data associated with your account",
            "your right to review, update, correct, and delete your information",
            "right to review",
            "right to update",
            "right to correct",
            "right to delete your information",
            # Consent withdrawal
            "revoke consent given to us",

            # General rights
            "exercise your rights",
            "rights of the data principal",
        ],
    },

    {
        "id": "grievance_contact",
        "title": "Grievance contact",
        "reference": "DPDP Act, 2023 — Section 13; applicable Rules",
        "why": (
            "Look for an identified grievance mechanism or grievance "
            "contact. A generic support email or 'contact us' phrase "
            "alone is not enough."
        ),
        
        "terms": [
            # Explicitly identified grievance officers
            "grievance officer at",
            "grievance redressal officer",
            "designated grievance officer",
            "appointed grievance officer",
            "contact our grievance officer",
            "contact the grievance officer",
            "write to our grievance officer",
            "email our grievance officer",
            # Privacy grievance contact
            "for any grievance with respect to your personal data",
            "for any grievances with respect to your personal data",
            "privacy grievance officer",
            "privacy.grievanceofficer",

            # Data protection officer / privacy contact
            "data protection officer at",
            "contact our data protection officer",
            "contact the data protection officer",
            "write to our data protection officer",

            # Explicit grievance submission mechanisms
            "submit a grievance to",
            "raise a grievance with",
            "lodge a complaint with",
            "file a complaint with",
            "grievance contact details",
            "grievance officer contact details",
            # Named grievance contact
            "grievance officer",
            "feedback or concern regarding protection of your personal information",
            "address your grievance",
            "address your grievance complaint",
            "grievance complaint",
            # Data Protection Officer contact
            "email the data protection officer",
            "data protection officer (dpo)",
            "data protection officer",
            "privacy@zomato.com",
            "queries relating to the processing",
            "regarding eternal's privacy policy",
        ],

    },

    {
        "id": "children_data",
        "title": "Children's data",
        "reference": "DPDP Act, 2023 — Section 9; applicable Rules",
        "why": (
            "Look for statements addressing children's personal data, "
            "parental or guardian involvement, or age-related handling "
            "where relevant."
        ),
        "terms": [
            "children's personal data",
            "personal data of children",
            "child's personal data",
            "personal information of children",
            "personal data relating to children",
            "personal data concerning children",

            # Parental / guardian consent
            "parental consent",
            "consent of a parent",
            "verifiable consent of a parent",
            "parental or guardian consent",
            "consent of a parent or guardian",
            "parent or guardian consent",
            "parental or legal guardian consent",

            # Age-related processing
            "under the age of 18",
            "under 18 years of age",
            "below the age of 18",
            "below a relevant age threshold",
            "child below a relevant age threshold",

            # Online services involving children
            "online services to children",
            "providing online services to children",
            "where we are providing online services to children",
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


def _matching_excerpts(
    text: str,
    terms: list[str],
    limit: int = 3,
    exclude_terms: list[str] | None = None,
) -> list[str]:
    """Return original sentences matching phrases, excluding weak matches."""

    patterns = [
        re.compile(
            r"(?<!\w)" + re.escape(term) + r"(?!\w)",
            re.IGNORECASE,
        )
        for term in terms
    ]

    exclusions = [
        re.compile(
            r"(?<!\w)" + re.escape(term) + r"(?!\w)",
            re.IGNORECASE,
        )
        for term in (exclude_terms or [])
    ]

    hits: list[str] = []
    seen: set[str] = set()

    for piece in _split_sentences(text):

        # Skip sentences containing a known irrelevant phrase.
        if any(pattern.search(piece) for pattern in exclusions):
            continue

        if any(pattern.search(piece) for pattern in patterns):
            normalized = re.sub(r"\s+", " ", piece).strip()

            if normalized not in seen:
                seen.add(normalized)
                hits.append(
                    normalized[:500] + ("…" if len(normalized) > 500 else "")
                )

        if len(hits) >= limit:
            break

    return hits


def build_dpdp_checklist(
    policy_text: str,
    include_model_report: bool = True,
) -> dict[str, Any]:
    """Create six informational checklist items and their matching excerpts."""

    if not isinstance(policy_text, str) or not policy_text.strip():
        raise ValueError(
            "Paste some privacy-policy text before creating the checklist."
        )

    results = []

    for item in CHECKLIST:
        excerpts = _matching_excerpts(
            policy_text,
            item["terms"],
            exclude_terms=item.get("exclude_terms", []),
        )

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

    report = (
        build_report(policy_text)
        if include_model_report
        else None
    )

    return {
        "product": "PrivacyLens India",
        "checklist_type": "informational_issue_spotting",
        "disclaimer": (
            "This checklist is an educational aid, not legal advice, "
            "a compliance audit, or a determination that an organization "
            "complies with or violates the DPDP Act or Rules."
        ),
        "checklist": results,
        "model_report": report,
        "limitations": [
            "A keyword match is not proof that a requirement is satisfied.",
            "No matching text is not proof of non-compliance; the excerpt may be "
            "incomplete or use different wording.",
            "A privacy policy alone cannot establish operational practices, "
            "valid consent flows, security effectiveness, or legal applicability.",
            "The OPP-115 model categories are not DPDP compliance labels.",
            "Every checklist item requires human review against the full context "
            "and current official law.",
        ],
    }


if __name__ == "__main__":
    sample = (
        "This Privacy Policy describes the personal data we collect. "
        "We collect your email address to create your account. "
        "We use your email to provide our services. "
        "You may withdraw your consent at any time. "
        "You can request correction of your personal data. "
        "If you have a complaint regarding your personal data, contact our "
        "Grievance Officer at grievance@example.com. "
        "We use encryption to protect personal information. "
        "We retain account information for as long as necessary."
    )

    result = build_dpdp_checklist(
        sample,
        include_model_report=False,
    )

    for item in result["checklist"]:
        print(f'{item["status"]}: {item["title"]}')

        for excerpt in item["evidence"]:
            print("  Evidence:", excerpt)
