"""Print a non-secret production-readiness report."""

from __future__ import annotations

import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(ROOT, "src")
sys.path.append(SRC_DIR)

from operational_status import build_operational_status


def render_readiness_markdown(status: dict) -> str:
    production_label = (
        "Ready for paid production"
        if status["production_ready"]
        else "Pilot only"
    )
    lines = [
        "# Serenova Readiness Report",
        "",
        f"- Engine version: {status['engine_version']}",
        f"- Production status: {production_label}",
        (
            "- Independent reference fixtures: "
            f"{status['independent_reference_fixture_count']}/"
            f"{status['required_independent_reference_fixtures']}"
        ),
        f"- Remaining release gates: {len(status['blocking_items'])}",
        "",
        "## Remaining Gates",
        "",
        "| Gate | Category | Next action | Evidence |",
        "| --- | --- | --- | --- |",
    ]

    blocking_items = status["blocking_items"]
    if not blocking_items:
        lines.append("| All release gates are passing | - | - | - |")
    for item in blocking_items:
        lines.append(
            "| "
            f"{item['label']} | "
            f"{item['category']} | "
            f"{item['next_step']} | "
            f"{item['evidence']} |"
        )

    lines.extend([
        "",
        "## Note",
        "",
        status["note"],
    ])
    return "\n".join(lines)


def main() -> None:
    print(render_readiness_markdown(build_operational_status()))


if __name__ == "__main__":
    main()
