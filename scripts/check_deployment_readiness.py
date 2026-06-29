"""Check private web deployment readiness without overstating production status."""

from __future__ import annotations

import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(ROOT, "src")
sys.path.append(SRC_DIR)

from operational_status import build_operational_status


REQUIRED_FILES = [
    "Dockerfile",
    ".dockerignore",
    ".env.example",
    ".streamlit/config.toml",
    "requirements.txt",
    "src/app.py",
]

REQUIRED_ENV_EXAMPLE_KEYS = [
    "SERENOVA_API_TOKEN",
    "SERENOVA_ADMIN_TOKEN",
    "SERENOVA_ENCRYPTION_KEY",
    "SERENOVA_PSEUDONYM_KEY",
    "SERENOVA_SESSION_RETENTION_DAYS",
]

REQUIRED_DOCKERIGNORE_PATTERNS = [
    "data/sessions/*.json",
    "data/sessions/*.json.enc",
    "data/audit/*.jsonl",
    "data/feedback/*.jsonl",
]


def build_deployment_readiness() -> dict:
    operational_status = build_operational_status()
    file_checks = {
        path: os.path.exists(os.path.join(ROOT, path))
        for path in REQUIRED_FILES
    }
    env_example_keys = _load_env_example_keys()
    dockerignore_patterns = _load_dockerignore_patterns()
    checks = {
        "required_files_present": all(file_checks.values()),
        "env_template_documents_required_secrets": all(
            key in env_example_keys
            for key in REQUIRED_ENV_EXAMPLE_KEYS
        ),
        "docker_excludes_sensitive_runtime_data": all(
            pattern in dockerignore_patterns
            for pattern in REQUIRED_DOCKERIGNORE_PATTERNS
        ),
        "streamlit_config_present": file_checks[".streamlit/config.toml"],
        "automated_tests_available": os.path.isdir(
            os.path.join(ROOT, "tests")
        ),
    }
    return {
        "deployable_for_private_pilot": all(checks.values()),
        "paid_production_ready": operational_status["production_ready"],
        "checks": checks,
        "file_checks": file_checks,
        "remaining_release_gates": [
            item["label"]
            for item in operational_status["blocking_items"]
        ],
        "note": (
            "Private web deployment readiness means the app can be packaged "
            "and hosted for controlled pilot use. Paid production still "
            "requires the release evidence gates to pass."
        ),
    }


def render_deployment_readiness_markdown(result: dict) -> str:
    pilot_status = (
        "ready"
        if result["deployable_for_private_pilot"]
        else "blocked"
    )
    production_status = (
        "ready"
        if result["paid_production_ready"]
        else "blocked"
    )
    lines = [
        "# Serenova Deployment Readiness",
        "",
        f"- Private web pilot deployment: {pilot_status}",
        f"- Paid production deployment: {production_status}",
        "",
        "## Technical Checks",
        "",
    ]
    for check, passed in result["checks"].items():
        marker = "PASS" if passed else "BLOCKED"
        lines.append(f"- {marker}: {check}")

    lines.extend([
        "",
        "## Remaining Release Gates",
        "",
    ])
    if result["remaining_release_gates"]:
        for gate in result["remaining_release_gates"]:
            lines.append(f"- {gate}")
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Note",
        "",
        result["note"],
    ])
    return "\n".join(lines)


def _load_env_example_keys() -> set[str]:
    path = os.path.join(ROOT, ".env.example")
    if not os.path.exists(path):
        return set()
    keys = set()
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            keys.add(line.split("=", 1)[0])
    return keys


def _load_dockerignore_patterns() -> set[str]:
    path = os.path.join(ROOT, ".dockerignore")
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as file:
        return {
            line.strip()
            for line in file
            if line.strip() and not line.strip().startswith("#")
        }


def main() -> None:
    print(render_deployment_readiness_markdown(build_deployment_readiness()))


if __name__ == "__main__":
    main()
