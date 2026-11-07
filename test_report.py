import unittest
from report import extractive_summary

class TestExtractiveSummary(unittest.TestCase):
    def test_selects_original_sentences(self):
        text = "Welcome to our app. We collect your email address to create an account. We may share data with service providers."
        result = extractive_summary(text, max_sentences=2)
        self.assertLessEqual(len(result), 2)
        for sentence in result:
            self.assertIn(sentence, text)

    def test_empty_input(self):
        self.assertEqual(extractive_summary("   "), [])

if __name__ == "__main__":
    unittest.main()
