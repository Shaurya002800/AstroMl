"""Run versioned deterministic model-output evaluations."""

import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from evaluation.model_outputs import run_model_output_evaluation


if __name__ == "__main__":
    result = run_model_output_evaluation()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
