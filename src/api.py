"""Authenticated internal API for deterministic astrology reports."""

from __future__ import annotations

import os
import secrets
import sys
import uuid
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(__file__))

from astrology_model import build_consultation_brief
from audit_log import record_audit_event
from feedback import ALLOWED_RATINGS, ALLOWED_TAGS, save_feedback
from report import generate_full_report
from operational_status import build_operational_status
from release import ENGINE_VERSION
from session_log import delete_session, list_sessions, load_session
from validation.reference_charts import run_reference_validation


app = FastAPI(
    title="Serenova Astrology Engine",
    version=ENGINE_VERSION,
    description="Private deterministic Jyotish calculation and consultation API.",
)


class ReportRequest(BaseModel):
    birth_datetime_utc: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    query_datetime_utc: datetime | None = None
    time_precision: str = Field(
        default="exact",
        pattern="^(exact|within_15_min|within_1_hour|unknown)$",
    )


class FeedbackRequest(BaseModel):
    session_identifier: str = Field(min_length=1, max_length=200)
    rating: str
    tags: list[str] = Field(default_factory=list)
    note: str = Field(default="", max_length=2000)


def require_consultant_key(x_api_key: str | None = Header(default=None)) -> None:
    configured_key = os.getenv("SERENOVA_API_TOKEN")
    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )
    if not x_api_key or not secrets.compare_digest(x_api_key, configured_key):
        raise HTTPException(status_code=401, detail="Invalid API key.")


def require_admin_key(x_api_key: str | None = Header(default=None)) -> None:
    configured_key = os.getenv("SERENOVA_ADMIN_TOKEN")
    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail="Admin authentication is not configured.",
        )
    if not x_api_key or not secrets.compare_digest(x_api_key, configured_key):
        raise HTTPException(status_code=401, detail="Invalid admin API key.")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "serenova-astrology-engine",
        "version": app.version,
    }


@app.get("/status", dependencies=[Depends(require_admin_key)])
def status() -> dict:
    return build_operational_status()


@app.post("/v1/report", dependencies=[Depends(require_consultant_key)])
def create_report(request: ReportRequest) -> dict:
    request_id = uuid.uuid4().hex
    query_datetime = (
        request.query_datetime_utc
        or datetime.now(timezone.utc)
    )
    birth_datetime = _naive_utc(request.birth_datetime_utc)
    query_datetime = _naive_utc(query_datetime)

    try:
        report = generate_full_report(
            birth_datetime,
            request.latitude,
            request.longitude,
            query_datetime=query_datetime,
        )
        consultation_brief = build_consultation_brief(
            report,
            time_precision=request.time_precision,
        )
        record_audit_event(
            event="report_generated",
            request_id=request_id,
            outcome="success",
            metadata={
                "model_version": consultation_brief["model_version"],
                "time_precision": request.time_precision,
            },
        )
        return {
            "request_id": request_id,
            "report": report,
            "consultation_brief": consultation_brief,
        }
    except Exception:
        record_audit_event(
            event="report_generated",
            request_id=request_id,
            outcome="error",
        )
        raise


@app.get("/v1/validation", dependencies=[Depends(require_admin_key)])
def validation_status() -> dict:
    return run_reference_validation()


@app.post("/v1/feedback", dependencies=[Depends(require_consultant_key)])
def create_feedback(request: FeedbackRequest) -> dict:
    if request.rating not in ALLOWED_RATINGS:
        raise HTTPException(status_code=422, detail="Unsupported rating.")
    if set(request.tags) - ALLOWED_TAGS:
        raise HTTPException(status_code=422, detail="Unsupported feedback tag.")
    return save_feedback(
        session_identifier=request.session_identifier,
        rating=request.rating,
        tags=request.tags,
        note=request.note,
    )


@app.get("/v1/sessions", dependencies=[Depends(require_admin_key)])
def sessions() -> dict:
    return {"sessions": list_sessions()}


@app.get(
    "/v1/sessions/{filename}",
    dependencies=[Depends(require_admin_key)],
)
def export_session(filename: str) -> dict:
    try:
        return load_session(filename)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=404, detail="Session not found.") from error


@app.delete(
    "/v1/sessions/{filename}",
    dependencies=[Depends(require_admin_key)],
)
def remove_session(filename: str) -> dict:
    try:
        delete_session(filename)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=404, detail="Session not found.") from error
    return {"deleted": True}


def _naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
