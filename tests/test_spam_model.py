"""Tests for the trainable spam-risk model."""

import unittest

import spam_model
from models import Opportunity


def make_opportunity(title, organizer="Example Org", interests=None,
                     url="https://example.com/info"):
    """Build an Opportunity fixture for spam-model tests."""
    if interests is None:
        interests = ["AI", "coding"]

    return Opportunity(
        "draft-001",
        title,
        "workshop",
        interests,
        ["JC"],
        "free",
        True,
        "2099-12-31",
        url,
        organizer,
    )


class TestSpamModel(unittest.TestCase):
    """Check model training, scoring, and explainability."""

    def test_tokenize_normalizes_text(self):
        tokens = spam_model.tokenize("WIN $$$ Money, now! 2026")

        self.assertEqual(tokens, ["win", "money", "now"])

    def test_train_default_model_has_both_classes(self):
        model = spam_model.train_default_model()

        self.assertGreater(model["label_counts"][spam_model.SPAM], 0)
        self.assertGreater(model["label_counts"][spam_model.LEGIT], 0)
        self.assertGreater(len(model["vocabulary"]), 0)

    def test_legitimate_opportunity_scores_low_risk(self):
        model = spam_model.train_default_model()
        opportunity = make_opportunity(
            "JC AI for Public Good Sprint",
            "Demo School Innovation Lab",
            ["AI", "coding", "public good"],
        )

        assessment = spam_model.assess_opportunity(opportunity, model)

        self.assertEqual(assessment["risk_level"], "LOW")
        self.assertLess(assessment["spam_probability"], 0.2)

    def test_spammy_opportunity_scores_high_risk(self):
        model = spam_model.train_default_model()
        opportunity = make_opportunity(
            "Guaranteed Scholarship Prize Click Now",
            "Crypto Winners Club",
            ["crypto", "cash"],
            "http://bit.ly/prize",
        )

        assessment = spam_model.assess_opportunity(opportunity, model)

        self.assertEqual(assessment["risk_level"], "HIGH")
        self.assertGreater(assessment["spam_probability"], 0.9)

    def test_signal_tokens_explain_spam_prediction(self):
        model = spam_model.train_default_model()

        signals = spam_model.spam_signal_tokens(
            model,
            "guaranteed crypto prize click now",
        )

        signal_tokens = [signal["token"] for signal in signals]
        self.assertIn("guaranteed", signal_tokens)
        self.assertIn("crypto", signal_tokens)

    def test_leave_one_out_accuracy_is_strong_on_seed_training(self):
        accuracy = spam_model.leave_one_out_accuracy(
            spam_model.DEFAULT_TRAINING_EXAMPLES
        )

        self.assertGreaterEqual(accuracy, 0.85)


if __name__ == "__main__":
    unittest.main()
