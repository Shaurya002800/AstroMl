"""Versioned end-to-end evaluation for deterministic consultation outputs."""

from __future__ import annotations

import json
import os
from datetime import datetime

try:
    from ..astrology_model import build_consultation_brief
    from ..interpretation.deterministic import (
        generate_deterministic_interpretation,
    )
    from ..report import generate_full_report
    from ..validation.reference_charts import load_reference_fixtures
    from .grounding import evaluate_interpretation_grounding
    from .safety import evaluate_interpretation_safety
except ImportError:
    from astrology_model import build_consultation_brief
    from interpretation.deterministic import (
        generate_deterministic_interpretation,
    )
    from report import generate_full_report
    from validation.reference_charts import load_reference_fixtures
    from evaluation.grounding import evaluate_interpretation_grounding
    from evaluation.safety import evaluate_interpretation_safety


DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data",
    "evaluation",
    "model_output_cases.json",
)


def run_model_output_evaluation(path: str = DATASET_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        dataset = json.load(file)
    fixtures = {
        fixture["fixture_id"]: fixture
        for fixture in load_reference_fixtures()
    }
    results = [
        _evaluate_case(case, fixtures)
        for case in dataset["cases"]
    ]
    return {
        "dataset_version": dataset["dataset_version"],
        "output_type": "deterministic_fallback",
        "passed": all(result["passed"] for result in results),
        "results": results,
        "note": (
            "This dataset evaluates deterministic report-to-text behavior. "
            "Representative external-LLM outputs still require separate review."
        ),
    }


def _evaluate_case(case: dict, fixtures: dict[str, dict]) -> dict:
    fixture = fixtures[case["fixture_id"]]
    input_data = fixture["input"]
    report = generate_full_report(
        datetime.fromisoformat(input_data["birth_datetime_utc"]),
        input_data["latitude"],
        input_data["longitude"],
        query_datetime=datetime.fromisoformat(
            case["query_datetime_utc"]
        ),
    )
    brief = build_consultation_brief(
        report,
        time_precision=case["time_precision"],
    )
    payload = {
        "report": report,
        "consultation_brief": brief,
    }
    output = generate_deterministic_interpretation(payload)
    safety = evaluate_interpretation_safety(output)
    grounding = evaluate_interpretation_grounding(output, payload)
    checks = {
        "report_quality": report["quality_checks"]["passed"],
        "safety": safety["passed"],
        "grounding": grounding["passed"],
        "uncertainty_note_present": (
            brief["uncertainty_note"] in output
        ),
        "consultant_note_present": "Consultant Note" in output,
    }
    return {
        "id": case["id"],
        "fixture_id": case["fixture_id"],
        "passed": all(checks.values()),
        "checks": checks,
    }
