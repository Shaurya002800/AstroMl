from datetime import datetime, timedelta
from datetime import timezone


# Vimshottari Dasha sequence and durations (in years) - total 120 years
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

TOTAL_YEARS = sum(DASHA_YEARS.values())  # 120

# Nakshatra lord mapping (each nakshatra ruled by a planet, cyclically repeating the sequence)
NAKSHATRA_LORDS = []
for i in range(27):
    NAKSHATRA_LORDS.append(DASHA_SEQUENCE[i % 9])


def get_dasha_balance_at_birth(moon_longitude: float):
    """
    Determine which dasha is running at birth and how much of it remains.
    Based on Moon's position within its nakshatra.
    """
    nak_span = 360 / 27  # 13.3333 degrees per nakshatra
    nak_index = int(moon_longitude // nak_span)
    position_in_nakshatra = moon_longitude % nak_span  # how far moon has traveled into this nakshatra

    starting_lord = NAKSHATRA_LORDS[nak_index]
    full_dasha_years = DASHA_YEARS[starting_lord]

    # Fraction of nakshatra already elapsed = fraction of dasha already elapsed
    fraction_elapsed = position_in_nakshatra / nak_span
    years_elapsed = fraction_elapsed * full_dasha_years
    years_remaining = full_dasha_years - years_elapsed

    return starting_lord, years_remaining


def get_dasha_elapsed_at_birth(moon_longitude: float):
    """Return the starting dasha lord and elapsed years at birth."""
    starting_lord, years_remaining = get_dasha_balance_at_birth(moon_longitude)
    return starting_lord, DASHA_YEARS[starting_lord] - years_remaining


def years_to_timedelta(years: float) -> timedelta:
    """Convert fractional years to a timedelta (approximation: 365.25 days/year)."""
    return timedelta(days=years * 365.25)


def compute_mahadasha_timeline(birth_datetime, moon_longitude: float):
    """
    Return a full sequence of mahadasha periods with start/end dates,
    starting from birth and covering 120 years.
    """
    starting_lord, years_elapsed = get_dasha_elapsed_at_birth(moon_longitude)

    timeline = []
    current_start = birth_datetime - years_to_timedelta(years_elapsed)
    start_index = DASHA_SEQUENCE.index(starting_lord)

    # Keep the true pre-birth start so nested periods do not restart at birth.
    full_years = DASHA_YEARS[starting_lord]
    current_end = current_start + years_to_timedelta(full_years)
    timeline.append({
        "lord": starting_lord,
        "start": current_start,
        "end": current_end,
        "duration_years": full_years,
        "birth_occurs_within_period": True,
    })
    current_start = current_end

    # Subsequent full dashas, cycling through sequence
    for i in range(1, 9):
        lord = DASHA_SEQUENCE[(start_index + i) % 9]
        full_years = DASHA_YEARS[lord]
        current_end = current_start + years_to_timedelta(full_years)
        timeline.append({
            "lord": lord,
            "start": current_start,
            "end": current_end,
            "duration_years": full_years,
            "birth_occurs_within_period": False,
        })
        current_start = current_end

    return timeline


def compute_antardasha(mahadasha_lord: str, mahadasha_start, mahadasha_duration_years: float):
    """
    Compute antardasha (sub-period) breakdown within a mahadasha.
    Antardasha sequence starts from the mahadasha lord itself, cycling through DASHA_SEQUENCE,
    with each sub-period proportional to (antardasha_lord_years / 120) * mahadasha_duration.
    """
    start_index = DASHA_SEQUENCE.index(mahadasha_lord)
    antardashas = []
    current_start = mahadasha_start

    for i in range(9):
        sub_lord = DASHA_SEQUENCE[(start_index + i) % 9]
        sub_years = (DASHA_YEARS[sub_lord] / TOTAL_YEARS) * mahadasha_duration_years
        current_end = current_start + years_to_timedelta(sub_years)
        antardashas.append({
            "lord": sub_lord,
            "start": current_start,
            "end": current_end,
            "duration_years": sub_years,
        })
        current_start = current_end

    return antardashas


def compute_pratyantar_dasha(
    antardasha_lord: str,
    antardasha_start,
    antardasha_duration_years: float,
):
    """
    Compute Pratyantar dasha periods within an Antardasha.

    The sequence begins with the Antardasha lord and each duration is
    proportional to the Vimshottari years of the Pratyantar lord.
    """
    start_index = DASHA_SEQUENCE.index(antardasha_lord)
    periods = []
    current_start = antardasha_start

    for i in range(9):
        lord = DASHA_SEQUENCE[(start_index + i) % 9]
        duration_years = (
            DASHA_YEARS[lord] / TOTAL_YEARS
        ) * antardasha_duration_years
        current_end = current_start + years_to_timedelta(duration_years)
        periods.append({
            "lord": lord,
            "start": current_start,
            "end": current_end,
            "duration_years": duration_years,
        })
        current_start = current_end

    return periods


def get_current_dasha(birth_datetime, moon_longitude: float, query_datetime=None):
    """
    Given birth details and a query date (default: now),
    return the currently active mahadasha and antardasha.
    """
    if query_datetime is None:
        query_datetime = datetime.now(timezone.utc).replace(tzinfo=None)


    timeline = compute_mahadasha_timeline(birth_datetime, moon_longitude)

    current_maha = None
    for period in timeline:
        if period["start"] <= query_datetime < period["end"]:
            current_maha = period
            break

    if current_maha is None:
        return {"error": "Query date outside computed 120-year timeline"}

    antardashas = compute_antardasha(
        current_maha["lord"], current_maha["start"], current_maha["duration_years"]
    )

    current_antar = None
    for sub in antardashas:
        if sub["start"] <= query_datetime < sub["end"]:
            current_antar = sub
            break

    current_pratyantar = None
    pratyantar_periods = []
    if current_antar:
        pratyantar_periods = compute_pratyantar_dasha(
            current_antar["lord"],
            current_antar["start"],
            current_antar["duration_years"],
        )
        for period in pratyantar_periods:
            if period["start"] <= query_datetime < period["end"]:
                current_pratyantar = period
                break

    return {
        "mahadasha": current_maha,
        "antardasha": current_antar,
        "pratyantar": current_pratyantar,
        "current_antardasha_pratyantar_timeline": pratyantar_periods,
        "full_mahadasha_timeline": timeline
    }


if __name__ == "__main__":
    from chart import compute_chart

    # Same test case: 15 Aug 1990, 14:30 IST, New Delhi
    test_dt_utc = datetime(1990, 8, 15, 9, 0)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    chart = compute_chart(test_dt_utc, delhi_lat, delhi_lon)
    moon_lon = chart["planets"]["Moon"]["longitude"]

    result = get_current_dasha(test_dt_utc, moon_lon)

    print(f"Current Mahadasha: {result['mahadasha']['lord']}")
    print(f"  From: {result['mahadasha']['start'].date()} To: {result['mahadasha']['end'].date()}")
    print(f"\nCurrent Antardasha: {result['antardasha']['lord']}")
    print(f"  From: {result['antardasha']['start'].date()} To: {result['antardasha']['end'].date()}")

    print("\nFull Mahadasha Timeline:")
    for period in result["full_mahadasha_timeline"]:
        print(f"  {period['lord']}: {period['start'].date()} → {period['end'].date()} "
              f"({period['duration_years']} years)")
