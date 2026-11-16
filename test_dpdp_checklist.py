
import unittest
from dpdp_checklist import build_dpdp_checklist


class TestDPDPChecklist(unittest.TestCase):

    def test_matches_evidence_but_not_compliance(self):
        text = (
            "We use your personal data to provide our services. "
            "You may withdraw your consent at any time. "
            "If you have a complaint regarding your personal data, "
            "contact our Grievance Officer at grievance@example.com."
        )

        result = build_dpdp_checklist(
            text, include_model_report=False
        )
        by_id = {item["id"]: item for item in result["checklist"]}

        self.assertEqual(len(by_id), 6)
        self.assertEqual(
            by_id["purpose"]["status"],
            "Potential evidence found"
        )
        self.assertEqual(
            by_id["consent"]["status"],
            "Potential evidence found"
        )
        self.assertEqual(
            by_id["grievance_contact"]["status"],
            "Potential evidence found"
        )
        self.assertEqual(
            by_id["notice"]["status"],
            "No matching text found"
        )
        self.assertIn("not legal advice", result["disclaimer"].lower())
        self.assertTrue(
            all(item["manual_review_required"] for item in result["checklist"])
        )

    def test_security_false_positive_prevented(self):
        text = (
            "You can request correction of your personal data "
            "by emailing our Data Protection Officer."
        )

        result = build_dpdp_checklist(
            text, include_model_report=False
        )
        by_id = {item["id"]: item for item in result["checklist"]}

        self.assertEqual(
            by_id["rights"]["status"],
            "Potential evidence found"
        )
        self.assertEqual(
            len(result["checklist"]), 6
        )

    def test_empty_policy_rejected(self):
        with self.assertRaises(ValueError):
            build_dpdp_checklist(
                " ", include_model_report=False
            )


if __name__ == "__main__":
    unittest.main()
