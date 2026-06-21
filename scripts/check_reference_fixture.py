"""Validate and compare one proposed reference-chart fixture."""

import argparse
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "src"))

from validation.reference_charts import (
    compare_reference_fixture,
    validate_reference_fixture,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture")
    arguments = parser.parse_args()

    with open(arguments.fixture, "r", encoding="utf-8") as file:
        fixture = json.load(file)
    validate_reference_fixture(fixture)
    result = compare_reference_fixture(fixture)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
