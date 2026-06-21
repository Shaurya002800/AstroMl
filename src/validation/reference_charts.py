"""Load and compare normalized reference chart fixtures."""

from __future__ import annotations

import json
import os
from datetime import datetime

try:
    from ..calculations.chart import compute_chart
    from ..calculations.extended_divisional_charts import (
        build_extended_divisional_charts,
    )
except ImportError:
    from calculations.chart import compute_chart
    from calculations.extended_divisional_charts import (
        build_extended_divisional_charts,
    )


FIXTURE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data",
    "golden_charts",
)
INTERNAL_STATUS = "internal_regression_only"
INDEPENDENT_STATUSES = {
    "external_software_verified",
    "expert_reviewed",
}
ALLOWED_VERIFICATION_STATUSES = {
    INTERNAL_STATUS,
    *INDEPENDENT_STATUSES,
}


def load_reference_fixtures() -> list[dict]:
    fixtures = []
    for filename in sorted(os.listdir(FIXTURE_DIR)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(FIXTURE_DIR, filename)
        with open(path, "r", encoding="utf-8") as file:
            fixture = json.load(file)
        validate_reference_fixture(fixture)
        fixtures.append(fixture)
    return fixtures


def compare_reference_fixture(fixture: dict) -> dict:
    input_data = fixture["input"]
    chart = compute_chart(
        datetime.fromisoformat(input_data["birth_datetime_utc"]),
        input_data["latitude"],
        input_data["longitude"],
    )
    extended_vargas = build_extended_divisional_charts(chart)
    tolerance = fixture["tolerances_degrees"]
    findings = []

    expected_ascendant = fixture["expected"]["ascendant"]
    ascendant_delta = angular_delta(
        chart["ascendant"]["longitude"],
        expected_ascendant["longitude"],
    )
    findings.append({
        "field": "ascendant",
        "expected_sign": expected_ascendant["sign"],
        "actual_sign": chart["ascendant"]["sign"],
        "delta_degrees": ascendant_delta,
        "passed": (
            chart["ascendant"]["sign"] == expected_ascendant["sign"]
            and ascendant_delta <= tolerance["ascendant"]
        ),
    })

    for planet, expected in fixture["expected"]["planets"].items():
        actual = chart["planets"][planet]
        delta = angular_delta(actual["longitude"], expected["longitude"])
        findings.append({
            "field": f"planet.{planet}",
            "expected_sign": expected["sign"],
            "actual_sign": actual["sign"],
            "delta_degrees": delta,
            "passed": (
                actual["sign"] == expected["sign"]
                and delta <= tolerance["planets"]
                and (
                    "is_retrograde" not in expected
                    or actual["is_retrograde"]
                    == expected["is_retrograde"]
                )
            ),
        })

    for varga, expected in fixture["expected"].get(
        "extended_vargas", {}
    ).items():
        actual = extended_vargas["implemented"][varga]
        expected_boundary = expected.get("ascendant_near_boundary")
        actual_boundary = actual[
            "ascendant_boundary_sensitivity"
        ]["near_boundary"]
        findings.append({
            "field": f"varga.{varga}.ascendant",
            "expected_sign": expected["ascendant_sign"],
            "actual_sign": actual["ascendant_sign"],
            "expected_near_boundary": expected_boundary,
            "actual_near_boundary": actual_boundary,
            "passed": (
                actual["ascendant_sign"] == expected["ascendant_sign"]
                and (
                    expected_boundary is None
                    or expected_boundary == actual_boundary
                )
            ),
        })

    return {
        "fixture_id": fixture["fixture_id"],
        "verification_status": fixture["verification_status"],
        "reference_source": fixture["reference_source"],
        "passed": all(finding["passed"] for finding in findings),
        "findings": findings,
    }


def run_reference_validation() -> dict:
    results = [
        compare_reference_fixture(fixture)
        for fixture in load_reference_fixtures()
    ]
    independently_verified = [
        result
        for result in results
        if result["verification_status"] in INDEPENDENT_STATUSES
    ]
    return {
        "passed": all(result["passed"] for result in results),
        "fixture_count": len(results),
        "independently_verified_fixture_count": len(independently_verified),
        "results": results,
        "note": (
            "Internal regression fixtures detect software changes but do not "
            "constitute independent accuracy validation."
        ),
    }


def angular_delta(longitude_a: float, longitude_b: float) -> float:
    difference = abs(longitude_a - longitude_b) % 360
    return min(difference, 360 - difference)


def validate_reference_fixture(fixture: dict) -> None:
    required = {
        "fixture_id",
        "verification_status",
        "reference_source",
        "settings",
        "input",
        "tolerances_degrees",
        "expected",
    }
    missing = required - set(fixture)
    if missing:
        raise ValueError(
            f"Reference fixture is missing fields: {sorted(missing)}"
        )
    verification_status = fixture["verification_status"]
    if verification_status not in ALLOWED_VERIFICATION_STATUSES:
        raise ValueError(
            "Unsupported verification_status: "
            f"{verification_status!r}"
        )
    if verification_status in INDEPENDENT_STATUSES:
        evidence = fixture.get("verification_evidence", {})
        required_evidence = {
            "reviewer_or_software",
            "version_or_credential",
            "verified_at",
            "artifact_reference",
        }
        missing_evidence = required_evidence - set(evidence)
        if missing_evidence:
            raise ValueError(
                "Independent fixture is missing verification evidence: "
                f"{sorted(missing_evidence)}"
            )
        datetime.fromisoformat(evidence["verified_at"])

    settings = fixture["settings"]
    required_settings = {
        "ayanamsa",
        "node_mode",
        "coordinate_frame",
    }
    missing_settings = required_settings - set(settings)
    if missing_settings:
        raise ValueError(
            f"Reference fixture is missing settings: {sorted(missing_settings)}"
        )

    input_data = fixture["input"]
    datetime.fromisoformat(input_data["birth_datetime_utc"])
    if not -90 <= input_data["latitude"] <= 90:
        raise ValueError("Fixture latitude must be between -90 and 90.")
    if not -180 <= input_data["longitude"] <= 180:
        raise ValueError("Fixture longitude must be between -180 and 180.")

    tolerances = fixture["tolerances_degrees"]
    for field in ("ascendant", "planets"):
        tolerance = tolerances[field]
        if tolerance <= 0 or tolerance > 1:
            raise ValueError(
                f"Fixture {field} tolerance must be > 0 and <= 1 degree."
            )
