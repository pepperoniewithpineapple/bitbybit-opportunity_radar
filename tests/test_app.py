import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import intelligence


def sample_opportunities():
    return [
        core.Opportunity(
            "opp-001",
            "Cyber AI Workshop",
            "workshop",
            ["cybersecurity", "AI", "coding"],
            ["JC", "Poly"],
            "free",
            True,
            "2026-08-01",
            "https://example.com/cyber",
            "Tech Lab",
        ),
        core.Opportunity(
            "opp-002",
            "Paid Fashion Showcase",
            "competition",
            ["design", "marketing"],
            ["JC"],
            "paid",
            False,
            "2026-08-12",
            "https://example.com/design",
            "Style Org",
        ),
        core.Opportunity(
            "opp-003",
            "Research Attachment",
            "research",
            ["research", "AI", "data science"],
            ["JC", "University"],
            "free",
            False,
            "2026-09-01",
            "https://example.com/research",
            "University Lab",
        ),
    ]


class OpportunityRadarTests(unittest.TestCase):
    def setUp(self):
        self.student = core.Student("Asha", "JC", ["AI", "coding", "cybersecurity"])
        self.opportunities = sample_opportunities()

    def test_ranked_discovery_is_transparent(self):
        results = core.rank_opportunities(self.opportunities, self.student)
        self.assertEqual(results[0]["opportunity"].title, "Cyber AI Workshop")
        self.assertGreater(results[0]["breakdown"]["interest_score"], 0)
        self.assertIn("total", results[0]["breakdown"])

    def test_submission_review_catches_spam_and_can_learn(self):
        spammy = core.Opportunity(
            "draft",
            "Guaranteed Crypto Prize Scholarship",
            "scholarship",
            ["finance"],
            ["JC"],
            "paid",
            False,
            "2026-08-01",
            "http://claim-prize.example",
            "Fast Money Club",
        )
        submissions = []
        risk = intelligence.predict_spam(spammy, submissions)
        flags = intelligence.review_flags(spammy, self.opportunities, submissions)
        self.assertIn(risk["risk"], {"MEDIUM", "HIGH"})
        self.assertTrue(any(flag["label"] == "ML spam risk" for flag in flags))

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "submissions.json"
            with patch.object(core, "SUBMISSIONS_PATH", temp_path):
                submission = core.create_submission(submissions, spammy)
                self.assertEqual(submission["submission_id"], "sub-001")
                self.assertTrue(temp_path.exists())

    def test_review_approval_publishes_opportunity(self):
        draft = core.Opportunity(
            "draft",
            "Community Coding Sprint",
            "hackathon",
            ["coding", "public good"],
            ["JC"],
            "free",
            True,
            "2026-08-15",
            "https://example.com/sprint",
            "Civic Tech",
        )
        submissions = [{"submission_id": "sub-001", "status": "pending", "opportunity": core.opportunity_to_record(draft)}]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            with patch.object(core, "SUBMISSIONS_PATH", temp_dir / "submissions.json"), patch.object(
                core, "OPPORTUNITIES_PATH", temp_dir / "opportunities.json"
            ):
                self.assertTrue(core.approve_submission(submissions, self.opportunities, "sub-001"))
        self.assertEqual(submissions[0]["status"], "approved")
        self.assertTrue(any(opportunity.title == "Community Coding Sprint" for opportunity in self.opportunities))

    def test_career_graph_and_pathway_layers(self):
        impact = intelligence.career_impact("cybersecurity analyst", self.student, self.opportunities[0])
        self.assertEqual(impact["label"], "INCREASE")

        graph_rows = intelligence.graph_rank(self.opportunities, self.student, "cybersecurity analyst")
        self.assertTrue(graph_rows)
        self.assertIn("->", graph_rows[0]["path"])

        plan = intelligence.career_pathway("cybersecurity analyst", self.student, self.opportunities)
        self.assertEqual([step["stage"] for step in plan["steps"]], ["Foundation", "Practice", "Proof", "Launch"])
        self.assertIn("readiness", plan)

    def test_search_falls_back_to_python_tfidf(self):
        rows = intelligence.search_opportunities(self.opportunities, "cyber AI", force_fallback=True)
        self.assertTrue(rows)
        self.assertEqual(rows[0]["engine"], "Python TF-IDF")
        self.assertEqual(rows[0]["opportunity"].title, "Cyber AI Workshop")


if __name__ == "__main__":
    unittest.main()
