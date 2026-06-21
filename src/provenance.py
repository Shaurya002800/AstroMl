"""Machine-readable source and rule provenance."""

from __future__ import annotations

import json
import os
from functools import lru_cache


KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "knowledge",
)


@lru_cache(maxsize=1)
def load_provenance_registry() -> dict:
    sources = _load_json("sources.json")["sources"]
    rules = _load_json("rules.json")["rules"]
    _validate_registry(sources, rules)
    return {
        "sources": sources,
        "rules": rules,
    }


def build_report_provenance() -> dict:
    registry = load_provenance_registry()
    return {
        "registry_version": "0.1.0",
        "rules": registry["rules"],
        "sources": registry["sources"],
        "note": (
            "Validation status distinguishes tested implementation from "
            "independent software comparison and expert review."
        ),
    }


def _load_json(filename: str) -> dict:
    path = os.path.join(KNOWLEDGE_DIR, filename)
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _validate_registry(sources: dict, rules: dict) -> None:
    for rule_id, rule in rules.items():
        required = {"module", "sources", "convention", "validation_status"}
        missing = required - set(rule)
        if missing:
            raise ValueError(
                f"Rule {rule_id} is missing provenance fields: {sorted(missing)}"
            )
        unknown_sources = set(rule["sources"]) - set(sources)
        if unknown_sources:
            raise ValueError(
                f"Rule {rule_id} references unknown sources: "
                f"{sorted(unknown_sources)}"
            )
