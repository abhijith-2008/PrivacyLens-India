import unittest
from dpdp_checklist import build_dpdp_checklist

class TestDPDPChecklist(unittest.TestCase):
    def test_matches_evidence_but_not_compliance(self):
        text = "We collect your email address. We use encryption to protect information."
        result = build_dpdp_checklist(text, include_model_report=False)
        by_id = {item["id"]: item for item in result["checklist"]}
        self.assertEqual(by_id["notice_purpose"]["status"], "Potential evidence found")
        self.assertEqual(by_id["security_safeguards"]["status"], "Potential evidence found")
        self.assertIn("not legal advice", result["disclaimer"].lower())
        self.assertTrue(all(item["manual_review_required"] for item in result["checklist"]))

    def test_empty_policy_rejected(self):
        with self.assertRaises(ValueError):
            build_dpdp_checklist("  ", include_model_report=False)

if __name__ == "__main__":
    unittest.main()
