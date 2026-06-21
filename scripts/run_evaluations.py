"""Run versioned deterministic safety-evaluation cases."""

import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from evaluation.safety import evaluate_interpretation_safety


DATASET = os.path.join(
    ROOT,
    "data",
    "evaluation",
    "safety_cases.json",
)


if __name__ == "__main__":
    with open(DATASET, "r", encoding="utf-8") as file:
        dataset = json.load(file)
    results = []
    for case in dataset["cases"]:
        actual = evaluate_interpretation_safety(case["text"])["passed"]
        results.append({
            "id": case["id"],
            "expected_pass": case["expected_pass"],
            "actual_pass": actual,
            "passed": actual == case["expected_pass"],
        })
    output = {
        "dataset_version": dataset["dataset_version"],
        "passed": all(result["passed"] for result in results),
        "results": results,
    }
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output["passed"] else 1)
