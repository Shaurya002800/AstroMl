"""Run normalized reference-chart comparisons from the command line."""

import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from validation.reference_charts import run_reference_validation


if __name__ == "__main__":
    result = run_reference_validation()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
