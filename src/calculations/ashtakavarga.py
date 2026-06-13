"""
Ashtakavarga calculation engine.
Based on Parashara's classical bindu tables (Brihat Parashara Hora Shastra).

For each of the 8 "contributors" (Ascendant, Sun, Moon, Mars, Mercury, Jupiter,
Venus, Saturn), and for each of the 7 "target" planets, classical texts specify
which house-positions (counted from the contributor) receive a bindu (point).

Rahu/Ketu are traditionally excluded from standard Ashtakavarga (Parashari system).
"""

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

CONTRIBUTORS = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
TARGETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Bindu tables: for each target planet, a dict mapping each contributor to a list
# of house-positions (1-12, counted inclusively from the contributor's position)
# that receive a bindu. These are the standard Parashari tables.

BINDU_TABLES = {
    "Sun": {
        "Ascendant": [3, 4, 6, 10, 11, 12],
        "Sun":       [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":      [3, 6, 10, 11],
        "Mars":      [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury":   [3, 5, 6, 9, 10, 11, 12],
        "Jupiter":   [5, 6, 9, 11],
        "Venus":     [6, 7, 12],
        "Saturn":    [1, 2, 4, 7, 8, 9, 10, 11],
    },
    "Moon": {
        "Ascendant": [3, 6, 10, 11],
        "Sun":       [3, 6, 7, 8, 10, 11],
        "Moon":      [1, 3, 6, 7, 10, 11],
        "Mars":      [2, 3, 5, 6, 9, 10, 11],
        "Mercury":   [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter":   [1, 4, 7, 8, 10, 11, 12],
        "Venus":     [3, 4, 5, 7, 9, 10, 11],
        "Saturn":    [3, 5, 6, 11],
    },
    "Mars": {
        "Ascendant": [1, 3, 6, 10, 11],
        "Sun":       [3, 5, 6, 10, 11],
        "Moon":      [3, 6, 11],
        "Mars":      [1, 2, 4, 7, 8, 10, 11],
        "Mercury":   [3, 5, 6, 11],
        "Jupiter":   [6, 10, 11, 12],
        "Venus":     [6, 8, 11, 12],
        "Saturn":    [1, 4, 7, 8, 9, 10, 11],
    },
    "Mercury": {
        "Ascendant": [1, 2, 4, 6, 8, 10, 11],
        "Sun":       [5, 6, 9, 11, 12],
        "Moon":      [2, 4, 6, 8, 10, 11],
        "Mars":      [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury":   [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter":   [6, 8, 11, 12],
        "Venus":     [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn":    [1, 2, 4, 7, 8, 9, 10, 11],
    },
    "Jupiter": {
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11],
        "Sun":       [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":      [2, 5, 7, 9, 11],
        "Mars":      [1, 2, 4, 7, 8, 10, 11],
        "Mercury":   [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter":   [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":     [2, 5, 6, 9, 10, 11],
        "Saturn":    [3, 5, 6, 12],
    },
    "Venus": {
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11],
        "Sun":       [8, 11, 12],
        "Moon":      [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 11, 12],
        "Mercury":   [3, 5, 9, 6, 9, 11],
        "Jupiter":   [5, 8, 9, 10, 11],
        "Venus":     [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn":    [3, 4, 5, 8, 9, 10, 11],
    },
    "Saturn": {
        "Ascendant": [1, 3, 4, 6, 10, 11],
        "Sun":       [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":      [3, 6, 11],
        "Mars":      [3, 5, 6, 11, 12],
        "Mercury":   [6, 8, 9, 10, 11, 12],
        "Jupiter":   [5, 6, 11, 12],
        "Venus":     [6, 11, 12],
        "Saturn":    [3, 5, 6, 11],
    },
}


def get_sign_index(sign: str) -> int:
    return ZODIAC_SIGNS.index(sign)


def compute_planet_ashtakavarga(target_planet: str, chart: dict, ascendant_sign: str) -> dict:
    """
    Compute the Ashtakavarga (bindu count per sign/house) for a single target planet.

    Returns a dict mapping each zodiac sign -> total bindu count contributed
    by all 8 contributors, plus a house-wise breakdown (house 1 = ascendant sign).
    """
    bindu_table = BINDU_TABLES[target_planet]

    # Initialize bindu count per absolute sign (0-11)
    sign_bindus = [0] * 12

    for contributor in CONTRIBUTORS:
        if contributor == "Ascendant":
            contributor_sign_index = get_sign_index(ascendant_sign)
        else:
            contributor_sign_index = get_sign_index(chart["planets"][contributor]["sign"])

        house_positions = bindu_table[contributor]

        for house_pos in house_positions:
            # house_pos is 1-12 counted from contributor's sign (inclusive)
            target_sign_index = (contributor_sign_index + house_pos - 1) % 12
            sign_bindus[target_sign_index] += 1

    # Build sign-wise result
    sign_result = {ZODIAC_SIGNS[i]: sign_bindus[i] for i in range(12)}

    # Build house-wise result (house 1 = ascendant sign, counting forward)
    asc_index = get_sign_index(ascendant_sign)
    house_result = {}
    for house_num in range(1, 13):
        sign_index = (asc_index + house_num - 1) % 12
        house_result[house_num] = {
            "sign": ZODIAC_SIGNS[sign_index],
            "bindus": sign_bindus[sign_index]
        }

    return {
        "planet": target_planet,
        "total_bindus": sum(sign_bindus),  # should equal a fixed total per planet
        "by_sign": sign_result,
        "by_house": house_result
    }


def compute_sarvashtakavarga(chart: dict, ascendant_sign: str) -> dict:
    """
    Compute Sarvashtakavarga: sum of bindus from all 7 planets, per house/sign.
    This is the most commonly referenced overall strength indicator per house.
    """
    asc_index = get_sign_index(ascendant_sign)
    sign_totals = [0] * 12
    individual_results = {}

    for target_planet in TARGETS:
        result = compute_planet_ashtakavarga(target_planet, chart, ascendant_sign)
        individual_results[target_planet] = result
        for i, sign in enumerate(ZODIAC_SIGNS):
            sign_totals[i] += result["by_sign"][sign]

    house_result = {}
    for house_num in range(1, 13):
        sign_index = (asc_index + house_num - 1) % 12
        house_result[house_num] = {
            "sign": ZODIAC_SIGNS[sign_index],
            "total_bindus": sign_totals[sign_index]
        }

    return {
        "individual_planets": individual_results,
        "sarva_by_house": house_result,
        "total_sum": sum(sign_totals)  # classically should sum to 337
    }


def interpret_house_strength(bindus: int) -> str:
    """
    General classical guideline for interpreting Sarvashtakavarga bindu counts per house.
    These thresholds are commonly cited approximations, not rigid rules.
    """
    if bindus >= 30:
        return "Very strong — favorable for matters of this house"
    elif bindus >= 25:
        return "Strong — generally supportive"
    elif bindus >= 20:
        return "Moderate — average results, context-dependent"
    elif bindus >= 15:
        return "Weak — may require effort or additional support from other yogas"
    else:
        return "Very weak — significant effort needed; check other charts (D9) and dasha for mitigating factors"


if __name__ == "__main__":
    from datetime import datetime
    from chart import compute_chart
    from dignity import annotate_chart_with_dignity_and_navamsa

    test_dt_utc = datetime(1990, 8, 15, 9, 0)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    chart = compute_chart(test_dt_utc, delhi_lat, delhi_lon)
    chart = annotate_chart_with_dignity_and_navamsa(chart)
    ascendant_sign = chart["ascendant"]["sign"]

    sav = compute_sarvashtakavarga(chart, ascendant_sign)

    print(f"Ascendant: {ascendant_sign}")
    print(f"\nTotal Sarvashtakavarga sum (should be 337): {sav['total_sum']}\n")

    print("Sarvashtakavarga by House:")
    for house_num, data in sav["sarva_by_house"].items():
        interpretation = interpret_house_strength(data["total_bindus"])
        print(f"  House {house_num} ({data['sign']}): {data['total_bindus']} bindus — {interpretation}")

    print("\nIndividual Planet Ashtakavarga totals (should each be a fixed classical total):")
    expected_totals = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56, "Venus": 52, "Saturn": 39}
    for planet, result in sav["individual_planets"].items():
        status = "✓" if result["total_bindus"] == expected_totals[planet] else "✗ MISMATCH"
        print(f"  {planet}: {result['total_bindus']} (expected {expected_totals[planet]}) {status}")