"""PrivacyLens Step 4: informational DPDP review checklist.

This is a keyword-assisted issue-spotting aid, not a legal compliance engine.
It does not decide whether an organization complies with the DPDP Act or Rules.
"""
from __future__ import annotations
import re
from report import build_report

CHECKLIST = [
    {
        "id": "notice_purpose",
        "title": "Personal data and purposes are explained",
        "reference": "DPDP Act, 2023 — Section 5 (Notice); DPDP Rules, 2025 — Rule 3",
        "why": "A notice should explain what personal data is involved and the purposes for processing in clear, understandable terms.",
        "terms": [
            "we collect", "personal data", "personal information", "we use", "purpose",
            "information we collect", "data we collect", "collect the following"
        ],
        "categories": ["First Party Collection/Use"],
    },
    {
        "id": "consent_choices",
        "title": "Consent and choices are explained",
        "reference": "DPDP Act, 2023 — Section 6",
        "why": "Where consent is the basis for processing, the Act describes consent standards and a right to withdraw consent.",
        "terms": ["consent", "withdraw consent", "opt out", "opt-out", "preferences", "permission"],
        "categories": ["User Choice/Control", "First Party Collection/Use"],
    },
    {
        "id": "rights_contact",
        "title": "How to exercise rights or raise a grievance is explained",
        "reference": "DPDP Act, 2023 — Sections 11–13; DPDP Rules, 2025 — relevant notice and grievance provisions",
        "why": "The framework includes rights relating to information, correction/erasure, grievance redressal and nomination, subject to applicable provisions.",
        "terms": ["access your", "correct", "correction", "delete your", "erase", "grievance", "complaint", "contact us", "data protection officer", "rights"],
        "categories": ["User Access, Edit and Deletion", "User Choice/Control"],
    },
    {
        "id": "security_safeguards",
        "title": "Security safeguards are described",
        "reference": "DPDP Act, 2023 — Section 8; DPDP Rules, 2025 — Rule 6",
        "why": "The Act and Rules address reasonable security safeguards for personal data; policy text may describe some safeguards but cannot prove that controls work in practice.",
        "terms": ["security", "safeguard", "encrypt", "encryption", "unauthorised access", "unauthorized access", "protect", "breach"],
        "categories": ["Data Security"],
    },
    {
        "id": "retention_erasure",
        "title": "Retention and deletion practices are described",
        "reference": "DPDP Act, 2023 — Section 8 and applicable Rules",
        "why": "The framework includes obligations concerning retention and erasure in applicable circumstances; a policy may state retention periods or deletion conditions.",
        "terms": ["retain", "retention", "delete", "deletion", "erase", "as long as necessary", "period necessary", "dispose"],
        "categories": ["Data Retention", "User Access, Edit and Deletion"],
    },
    {
        "id": "third_party_processing",
        "title": "Third-party sharing or processing is explained",
        "reference": "DPDP Act, 2023 — Section 8 and applicable provisions",
        "why": "Review what the policy says about service providers, processors, disclosures and sharing. A mention alone does not establish that all required disclosures are present.",
        "terms": ["third party", "third-party", "service provider", "processor", "share", "disclose", "partners", "vendors"],
        "categories": ["Third Party Sharing/Collection"],
    },
    {
        "id": "children",
        "title": "Children's data is addressed where relevant",
        "reference": "DPDP Act, 2023 — Section 9; applicable Rules",
        "why": "The framework has specific provisions concerning children's personal data. Whether they apply depends on the service, users, exemptions and applicable commencement.",
        "terms": ["child", "children", "minor", "parental consent", "guardian", "under the age"],
        "categories": ["International and Specific Audiences"],
    },
    {
        "id": "international_transfer",
        "title": "International processing or transfers are explained where relevant",
        "reference": "DPDP Act, 2023 — Section 16; applicable government restrictions and Rules",
        "why": "The Act addresses processing of personal data outside India. Policy text may mention locations or international transfers, but a mention alone cannot establish legal permissibility.",
        "terms": ["outside india", "outside of india", "international transfer", "transfer abroad", "other countries", "global", "country where", "located in"],
        "categories": ["International and Specific Audiences", "Third Party Sharing/Collection"],
    },
    {
        "id": "policy_updates",
        "title": "Policy update communication is described",
        "reference": "Privacy transparency review; check applicable legal and contractual obligations",
        "why": "An update section helps users understand how policy changes are communicated. This is a useful transparency check, not a standalone DPDP compliance test.",
        "terms": [
    "change this policy",
    "changes to this policy",
    "update this policy",
    "update this privacy policy",
    "updated privacy policy",
    "last updated",
    "last modified",
    "publish the revised version",
    "notify you",
    "notification of changes",
],
        "categories": ["Policy Change"],
    },
]

def _matching_excerpts(text: str, terms: list[str], limit: int = 3) -> list[str]:
    """Return original sentences/lines containing one or more search terms."""
    pieces = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", text) if p.strip()]
    hits = []
    seen = set()
    for piece in pieces:
        low = piece.casefold()
        if any(term.casefold() in low for term in terms):
            normalized = re.sub(r"\s+", " ", piece)
            if normalized not in seen:
                seen.add(normalized)
                hits.append(normalized[:500] + ("…" if len(normalized) > 500 else ""))
        if len(hits) >= limit:
            break
    return hits

def build_dpdp_checklist(policy_text: str, include_model_report: bool = True) -> dict:
    """Create checklist statuses and evidence excerpts from the supplied policy text."""
    if not isinstance(policy_text, str) or not policy_text.strip():
        raise ValueError("Paste some privacy-policy text before creating the checklist.")

    results = []
    for item in CHECKLIST:
        excerpts = _matching_excerpts(policy_text, item["terms"])
        if excerpts:
            status = "Potential evidence found"
            explanation = "The supplied text contains wording related to this topic. Review the excerpts and their surrounding context."
        else:
            status = "No matching text found"
            explanation = "This simple search did not find a matching excerpt. The topic may be described using different wording, elsewhere in the full policy, or outside the supplied text."
        results.append({
            "id": item["id"],
            "title": item["title"],
            "reference": item["reference"],
            "why_it_matters": item["why"],
            "status": status,
            "explanation": explanation,
            "evidence": excerpts,
            "related_model_categories": item["categories"],
            "manual_review_required": True,
        })

    report = None
    if include_model_report:
        report = build_report(policy_text)
    return {
        "product": "PrivacyLens India",
        "checklist_type": "informational_issue_spotting",
        "disclaimer": (
            "This checklist is an educational aid, not legal advice, a compliance audit, "
            "or a determination that an organization complies with or violates the DPDP Act or Rules."
        ),
        "commencement_note": (
            "The DPDP Act and Rules have staged commencement. As of 29 October 2026, many substantive "
            "obligations are scheduled to commence 18 months after the 13 November 2025 notification "
            "(13 May 2027). Confirm the current official commencement notifications and any corrigenda "
            "before relying on a legal timeline."
        ),
        "checklist": results,
        "model_report": report,
        "limitations": [
            "A keyword match is not proof that a requirement is satisfied.",
            "No matching text is not proof of non-compliance; the excerpt may be incomplete or use different wording.",
            "A privacy policy alone cannot establish operational practices, valid consent flows, security effectiveness, or legal applicability.",
            "The OPP-115 model categories are not DPDP compliance labels.",
            "Every checklist item requires human review against the full context and current official law.",
        ],
    }

if __name__ == "__main__":
    sample = """We collect your email address to create your account. We use encryption to protect personal information.
You may request deletion by contacting support. We may share data with service providers."""
    result = build_dpdp_checklist(sample, include_model_report=False)
    for item in result["checklist"]:
        print(f'{item["status"]}: {item["title"]}')
        for excerpt in item["evidence"]:
            print("  Evidence:", excerpt)
