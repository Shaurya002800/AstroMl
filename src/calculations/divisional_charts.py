"""
Divisional chart (Varga) calculations beyond D9.
D10 (Dasamsa) - career, profession, public status
D7 (Saptamsa) - children, creativity, legacy
"""

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def get_dasamsa_sign(longitude: float) -> str:
    """
    D10 Dasamsa: each sign (30°) divided into 10 parts of 3° each.

    Classical rule (Parashara):
    - For odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius):
      the 10 divisions start counting from the sign itself.
    - For even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces):
      the 10 divisions start counting from the 9th sign from it.
    """
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    part = int(degree_in_sign // 3)  # 0-9

    is_odd_sign = (sign_index % 2 == 0)  # Aries=0 (odd in classical numbering), so index%2==0 means odd sign

    if is_odd_sign:
        start = sign_index
    else:
        start = (sign_index + 8) % 12  # 9th sign from current (1-indexed) = +8 in 0-indexed

    dasamsa_index = (start + part) % 12
    return ZODIAC_SIGNS[dasamsa_index]


def get_saptamsa_sign(longitude: float) -> str:
    """
    D7 Saptamsa: each sign (30°) divided into 7 parts of ~4°17'8" each.

    Classical rule (Parashara):
    - For odd signs: counting starts from the sign itself.
    - For even signs: counting starts from the 7th sign from it (i.e. its own
      opposite sign in some traditions) — Parashara specifies starting from
      the sign itself for odd signs and from the 7th house sign for even signs.
    """
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    part_size = 30 / 7
    part = int(degree_in_sign // part_size)  # 0-6

    is_odd_sign = (sign_index % 2 == 0)

    if is_odd_sign:
        start = sign_index
    else:
        start = (sign_index + 6) % 12  # 7th sign from current

    saptamsa_index = (start + part) % 12
    return ZODIAC_SIGNS[saptamsa_index]


def annotate_chart_with_divisional_charts(chart: dict) -> dict:
    """
    Add D10 (career) and D7 (children) sign placements to each planet,
    and to the ascendant.
    """
    chart["ascendant"]["dasamsa_sign"] = get_dasamsa_sign(chart["ascendant"]["longitude"])
    chart["ascendant"]["saptamsa_sign"] = get_saptamsa_sign(chart["ascendant"]["longitude"])

    for planet, data in chart["planets"].items():
        data["dasamsa_sign"] = get_dasamsa_sign(data["longitude"])
        data["saptamsa_sign"] = get_saptamsa_sign(data["longitude"])

    return chart


def get_dasamsa_lagna_and_houses(chart: dict) -> dict:
    """
    Build a simplified D10 chart view: where each planet falls relative to
    the D10 ascendant (Dasamsa Lagna), using Whole Sign houses.
    """
    d10_asc_sign = chart["ascendant"]["dasamsa_sign"]
    asc_index = ZODIAC_SIGNS.index(d10_asc_sign)

    houses = {}
    for planet, data in chart["planets"].items():
        planet_d10_sign = data["dasamsa_sign"]
        planet_index = ZODIAC_SIGNS.index(planet_d10_sign)
        house_num = ((planet_index - asc_index) % 12) + 1
        houses.setdefault(house_num, []).append(planet)

    return {
        "d10_ascendant_sign": d10_asc_sign,
        "planets_by_house": houses
    }


if __name__ == "__main__":
    from datetime import datetime
    from chart import compute_chart
    from dignity import annotate_chart_with_dignity_and_navamsa

    test_dt_utc = datetime(1990, 8, 15, 9, 0)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    chart = compute_chart(test_dt_utc, delhi_lat, delhi_lon)
    chart = annotate_chart_with_dignity_and_navamsa(chart)
    chart = annotate_chart_with_divisional_charts(chart)

    print(f"D1 Ascendant: {chart['ascendant']['sign']}")
    print(f"D10 (Dasamsa) Ascendant: {chart['ascendant']['dasamsa_sign']}")
    print(f"D7 (Saptamsa) Ascendant: {chart['ascendant']['saptamsa_sign']}\n")

    print("Planet placements (D1 -> D9 -> D10 -> D7):")
    for planet, data in chart["planets"].items():
        print(f"  {planet}: {data['sign']} -> {data['navamsa_sign']} -> "
              f"{data['dasamsa_sign']} -> {data['saptamsa_sign']}")

    print("\nD10 Chart - Planets by House (Whole Sign from D10 Ascendant):")
    d10 = get_dasamsa_lagna_and_houses(chart)
    print(f"  D10 Ascendant Sign: {d10['d10_ascendant_sign']}")
    for house_num in sorted(d10["planets_by_house"].keys()):
        planets = ", ".join(d10["planets_by_house"][house_num])
        print(f"  House {house_num}: {planets}")