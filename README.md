# PrivacyLens India — Step 4: DPDP informational checklist

Adds `dpdp_checklist.py` to the Step 3 package.

## Run
```python
from dpdp_checklist import build_dpdp_checklist

policy_text = """
We collect your email address to create your account.
We use encryption to protect personal information.
You may request deletion by contacting support.
"""

result = build_dpdp_checklist(policy_text)
for item in result["checklist"]:
    print(item["status"], "-", item["title"])
    for excerpt in item["evidence"]:
        print("  Evidence:", excerpt)
```

Set `include_model_report=False` if you only want the checklist without running the ML model.

## Status meanings
- **Potential evidence found**: a keyword-assisted search found an excerpt related to the topic. This is not a pass.
- **No matching text found**: the search did not find a matching excerpt. This is not a fail; wording may differ or the pasted text may be incomplete.

## Scope and law references
The checklist is an educational issue-spotting aid based on selected topics in the Digital Personal Data Protection Act, 2023 and Digital Personal Data Protection Rules, 2025. It is not a legal audit, legal advice, or a DPDP compliance score. References in the code identify topics for review and do not assert that every provision is currently in force or applicable to every organization.

Official sources to verify before relying on the checklist:
- DPDP Act, 2023 — India Code: https://www.indiacode.nic.in/bitstream/123456789/22037/2/a2023-22.pdf
- DPDP Rules, 2025 — MeitY: https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025
- Commencement timeline — MeitY/PIB: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190655&lang=2&reg=48

The commencement notification provides staged dates. The 18-month date from 13 November 2025 is 13 May 2027 for the specified provisions; verify the latest official notification and corrigenda.

## Limitations
- Keyword matching is deliberately transparent but can miss paraphrases and can match irrelevant passages.
- A privacy policy cannot prove that the actual product behavior, consent UI, deletion handling, or security controls meet legal requirements.
- OPP-115 classifier predictions are not DPDP labels.
- Review the full policy, applicability, exemptions and current law with a qualified professional before making legal decisions.
