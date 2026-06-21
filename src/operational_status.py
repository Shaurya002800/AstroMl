"""Non-secret operational readiness checks."""

from __future__ import annotations

import os

try:
    from .release import ENGINE_VERSION
    from .secure_storage import encryption_enabled
    from .session_log import LOG_DIR
    from .validation.reference_charts import run_reference_validation
except ImportError:
    from release import ENGINE_VERSION
    from secure_storage import encryption_enabled
    from session_log import LOG_DIR
    from validation.reference_charts import run_reference_validation


def build_operational_status() -> dict:
    validation = run_reference_validation()
    independent_fixture_count = validation[
        "independently_verified_fixture_count"
    ]
    checks = {
        "api_authentication_configured": bool(
            os.getenv("SERENOVA_API_TOKEN")
        ),
        "admin_authentication_configured": bool(
            os.getenv("SERENOVA_ADMIN_TOKEN")
        ),
        "session_encryption_configured": encryption_enabled(),
        "llm_provider_configured": bool(os.getenv("GROQ_API_KEY")),
        "independent_reference_fixtures_present": (
            independent_fixture_count > 0
        ),
        "independent_reference_fixture_target_met": (
            independent_fixture_count >= 25
        ),
        "reference_fixtures_passing": validation["passed"],
        "no_plaintext_sessions_present": not any(
            filename.endswith(".json")
            for filename in os.listdir(LOG_DIR)
        ),
        "expert_rule_review_approved": _approved(
            "SERENOVA_EXPERT_REVIEW_APPROVED"
        ),
        "consultant_pilot_approved": _approved(
            "SERENOVA_PILOT_APPROVED"
        ),
        "privacy_review_approved": _approved(
            "SERENOVA_PRIVACY_REVIEW_APPROVED"
        ),
        "backup_recovery_drill_completed": _approved(
            "SERENOVA_BACKUP_DRILL_COMPLETED"
        ),
    }
    return {
        "engine_version": ENGINE_VERSION,
        "production_ready": all(checks.values()),
        "independent_reference_fixture_count": independent_fixture_count,
        "required_independent_reference_fixtures": 25,
        "checks": checks,
        "note": (
            "Approval environment flags are release records, not substitutes "
            "for signed review evidence and retained test artifacts."
        ),
    }


def _approved(environment_variable: str) -> bool:
    return os.getenv(environment_variable, "false").lower() == "true"
