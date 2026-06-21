"""Explicit local-time to UTC conversion with DST ambiguity handling."""

from __future__ import annotations

from datetime import timedelta

import pytz


ALLOWED_TIME_POLICIES = {
    "raise",
    "earlier",
    "later",
    "shift_forward",
}


def local_datetime_to_utc(
    local_datetime,
    timezone_name: str,
    policy: str = "raise",
):
    """
    Convert a naive local datetime to naive UTC.

    Policies:
    - raise: reject ambiguous/nonexistent local times.
    - earlier: choose the earlier UTC instant for an ambiguous time.
    - later: choose the later UTC instant for an ambiguous time.
    - shift_forward: advance nonexistent times until valid.
    """
    if policy not in ALLOWED_TIME_POLICIES:
        raise ValueError(f"Unsupported local-time policy: {policy}")

    timezone = pytz.timezone(timezone_name)
    try:
        localized = timezone.localize(local_datetime, is_dst=None)
    except pytz.AmbiguousTimeError:
        if policy == "raise" or policy == "shift_forward":
            raise
        candidates = [
            timezone.localize(local_datetime, is_dst=True),
            timezone.localize(local_datetime, is_dst=False),
        ]
        localized = (
            min(candidates, key=lambda value: value.astimezone(pytz.utc))
            if policy == "earlier"
            else max(candidates, key=lambda value: value.astimezone(pytz.utc))
        )
    except pytz.NonExistentTimeError:
        if policy != "shift_forward":
            raise
        localized = _shift_forward_to_valid(
            local_datetime,
            timezone,
        )

    return localized.astimezone(pytz.utc).replace(tzinfo=None)


def _shift_forward_to_valid(local_datetime, timezone):
    candidate = local_datetime
    for _ in range(180):
        candidate += timedelta(minutes=1)
        try:
            return timezone.localize(candidate, is_dst=None)
        except pytz.NonExistentTimeError:
            continue
    raise pytz.NonExistentTimeError(
        f"Could not resolve nonexistent local time: {local_datetime}"
    )
