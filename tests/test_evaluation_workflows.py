import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from evaluation.feedback_metrics import summarize_feedback
from evaluation.model_outputs import run_model_output_evaluation


class EvaluationWorkflowTests(unittest.TestCase):
    def test_versioned_deterministic_model_outputs_pass(self):
        result = run_model_output_evaluation()

        self.assertTrue(result["passed"])
        self.assertEqual(result["output_type"], "deterministic_fallback")
        self.assertGreaterEqual(len(result["results"]), 3)

    def test_feedback_metrics_are_session_based(self):
        result = summarize_feedback([
            {
                "rating": "useful",
                "tags": ["accurate_calculation"],
            },
            {
                "rating": "mixed",
                "tags": ["false_positive", "timing_mismatch"],
            },
            {
                "rating": "not_useful",
                "tags": ["false_positive", "overstated"],
            },
        ])

        self.assertEqual(result["session_count"], 3)
        self.assertEqual(result["useful_or_mixed_rate"], 0.6667)
        self.assertEqual(result["false_positive_rate"], 0.6667)
        self.assertEqual(result["overstatement_rate"], 0.3333)
