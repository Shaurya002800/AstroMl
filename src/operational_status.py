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


REQUIREMENT_DETAILS = {
    "api_authentication_configured": {
        "label": "Consultant API token configured",
        "category": "security",
        "why": "The report API must not be callable without a configured consultant token.",
        "next_step": "Set SERENOVA_API_TOKEN in the private runtime environment.",
        "evidence": "Environment configuration record",
    },
    "admin_authentication_configured": {
        "label": "Admin API token configured",
        "category": "security",
        "why": "Status, validation, session export, and deletion endpoints are administrative.",
        "next_step": "Set SERENOVA_ADMIN_TOKEN separately from the consultant token.",
        "evidence": "Environment configuration record",
    },
    "session_encryption_configured": {
        "label": "Encrypted session storage configured",
        "category": "privacy",
        "why": "Birth details and interpretations are sensitive consultation data.",
        "next_step": "Generate and store SERENOVA_ENCRYPTION_KEY outside the repo.",
        "evidence": "Key-management note or secret-manager entry",
    },
    "llm_provider_configured": {
        "label": "Optional LLM provider configured",
        "category": "workflow",
        "why": "The deterministic report works without an LLM, but reviewed synthesis requires a provider key.",
        "next_step": "Set GROQ_API_KEY only in the private consultant runtime.",
        "evidence": "Runtime configuration record",
    },
    "independent_reference_fixtures_present": {
        "label": "Independent reference fixtures started",
        "category": "validation",
        "why": "Internal regression fixtures catch software drift but do not prove external calculation accuracy.",
        "next_step": "Add at least one trusted-software or expert-reviewed fixture.",
        "evidence": "data/golden_charts fixture with verification_evidence",
    },
    "independent_reference_fixture_target_met": {
        "label": "25 independent reference fixtures",
        "category": "validation",
        "why": "A broad fixture set is needed across boundaries, nodes, retrogrades, vargas, and difficult time zones.",
        "next_step": "Collect and normalize 25 independently verified chart fixtures.",
        "evidence": "validate_references.py passing with 25 independent fixtures",
    },
    "reference_fixtures_passing": {
        "label": "Reference fixtures passing",
        "category": "validation",
        "why": "Every retained fixture must pass before trusting calculated chart facts.",
        "next_step": "Run python3 scripts/validate_references.py and resolve every discrepancy.",
        "evidence": "Dated validation output",
    },
    "no_plaintext_sessions_present": {
        "label": "No plaintext session files",
        "category": "privacy",
        "why": "Legacy plaintext session records can expose sensitive birth and consultation data.",
        "next_step": "Run the migration script, verify encrypted replacements, then delete plaintext sources.",
        "evidence": "Migration log and clean data/sessions directory",
    },
    "expert_rule_review_approved": {
        "label": "Expert Jyotish rule review approved",
        "category": "expert review",
        "why": "Classical rules, disputed conventions, and interpretation wording need practitioner review.",
        "next_step": "Complete docs/EXPERT_REVIEW_PROTOCOL.md with a qualified reviewer.",
        "evidence": "Signed expert review artifact",
    },
    "consultant_pilot_approved": {
        "label": "Consultant pilot approved",
        "category": "pilot",
        "why": "Real sessions reveal confusing wording, false positives, and workflow gaps.",
        "next_step": "Run the pilot in docs/PILOT_PROTOCOL.md and summarize feedback.",
        "evidence": "Signed pilot report and feedback summary",
    },
    "privacy_review_approved": {
        "label": "Privacy review approved",
        "category": "privacy",
        "why": "Sensitive client data requires a retained data-handling and risk review.",
        "next_step": "Review docs/THREAT_MODEL.md and retain privacy approval evidence.",
        "evidence": "Approved privacy/data-handling review",
    },
    "backup_recovery_drill_completed": {
        "label": "Backup recovery drill completed",
        "category": "operations",
        "why": "Encrypted backups are useful only if restore has been tested.",
        "next_step": "Run backup creation and restore verification using docs/ROLLBACK_AND_RECOVERY.md.",
        "evidence": "Dated backup and restore-verification record",
    },
}


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
        "no_plaintext_sessions_present": (
            not _plaintext_session_files_present()
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
    readiness_items = _build_readiness_items(
        checks,
        independent_fixture_count,
    )
    blocking_items = [
        item for item in readiness_items
        if item["status"] != "passed"
    ]
    return {
        "engine_version": ENGINE_VERSION,
        "production_ready": all(checks.values()),
        "production_readiness": (
            "ready_for_paid_production"
            if all(checks.values())
            else "pilot_only"
        ),
        "independent_reference_fixture_count": independent_fixture_count,
        "required_independent_reference_fixtures": 25,
        "checks": checks,
        "readiness_items": readiness_items,
        "blocking_items": blocking_items,
        "next_required_actions": [
            item["next_step"]
            for item in blocking_items[:5]
        ],
        "note": (
            "Approval environment flags are release records, not substitutes "
            "for signed review evidence and retained test artifacts."
        ),
    }


def _approved(environment_variable: str) -> bool:
    return os.getenv(environment_variable, "false").lower() == "true"


def _plaintext_session_files_present() -> bool:
    if not os.path.isdir(LOG_DIR):
        return False
    return any(
        filename.endswith(".json")
        for filename in os.listdir(LOG_DIR)
    )


def _build_readiness_items(
    checks: dict[str, bool],
    independent_fixture_count: int,
) -> list[dict]:
    readiness_items = []
    for check_name, passed in checks.items():
        details = REQUIREMENT_DETAILS[check_name]
        item = {
            "check": check_name,
            "label": details["label"],
            "category": details["category"],
            "status": "passed" if passed else "blocked",
            "why": details["why"],
            "next_step": details["next_step"],
            "evidence": details["evidence"],
        }
        if check_name == "independent_reference_fixture_target_met":
            item["progress"] = {
                "current": independent_fixture_count,
                "required": 25,
            }
        readiness_items.append(item)
    return readiness_items
