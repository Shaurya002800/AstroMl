"""
Yoga detection engine.
Each yoga is defined as a condition-checking function + metadata.
Detected yogas are returned with classical source references and effect descriptions.
"""

from planetary_conditions import angular_separation

KENDRA_HOUSES = [1, 4, 7, 10]  # Quadrant houses - most important for yogas
TRIKONA_HOUSES = [1, 5, 9]     # Trinal houses


def get_house_of_planet(planet_sign: str, ascendant_sign: str, zodiac_signs: list) -> int:
    """
    Whole Sign house system: house number = position of planet's sign
    relative to ascendant's sign, counted 1-12.
    """
    asc_index = zodiac_signs.index(ascendant_sign)
    planet_index = zodiac_signs.index(planet_sign)
    house = ((planet_index - asc_index) % 12) + 1
    return house


def check_gajakesari_yoga(chart: dict, ascendant_sign: str, zodiac_signs: list) -> dict:
    """
    Gajakesari Yoga: Moon and Jupiter in mutual Kendra (1,4,7,10 from each other).
    Classical source: BPHS Ch. 36
    """
    moon_house = get_house_of_planet(chart["planets"]["Moon"]["sign"], ascendant_sign, zodiac_signs)
    jupiter_house = get_house_of_planet(chart["planets"]["Jupiter"]["sign"], ascendant_sign, zodiac_signs)

    diff = abs(moon_house - jupiter_house)
    # Mutual kendra means difference is 0, 3, 6, or 9 (i.e. 1,4,7,10 apart in either direction)
    is_kendra = diff % 3 == 0

    if is_kendra:
        return {
            "name": "Gajakesari Yoga",
            "present": True,
            "involved_planets": ["Moon", "Jupiter"],
            "simplified": False,
            "source": "Brihat Parashara Hora Shastra, Ch. 36",
            "condition_met": f"Moon (House {moon_house}) and Jupiter (House {jupiter_house}) are in mutual Kendra",
            "effect": "Associated with intelligence, good reputation, and respect in society. "
                      "Strength of this yoga depends on the dignity of Moon and Jupiter — "
                      "check their individual dignity for how strongly this manifests.",
            "caveat": "This yoga is very common (occurs in roughly 1 in 4 charts) and its effects "
                      "are moderated heavily by planetary dignity and other yogas present."
        }
    return {"name": "Gajakesari Yoga", "present": False}


def check_budhaditya_yoga(chart: dict) -> dict:
    """
    Budhaditya Yoga: Sun and Mercury in the same sign (conjunction).
    Classical source: commonly cited, associated with intelligence/communication.
    """
    sun_sign = chart["planets"]["Sun"]["sign"]
    mercury_sign = chart["planets"]["Mercury"]["sign"]

    if sun_sign == mercury_sign:
        # Check combustion - Mercury too close to Sun can be 'combust' (weakened)
        sun_lon = chart["planets"]["Sun"]["longitude"]
        mercury_lon = chart["planets"]["Mercury"]["longitude"]
        degree_diff = angular_separation(sun_lon, mercury_lon)
        is_combust = chart["planets"]["Mercury"].get(
            "combustion", {}
        ).get("is_combust", degree_diff < 12)

        return {
            "name": "Budhaditya Yoga",
            "present": True,
            "involved_planets": ["Sun", "Mercury"],
            "simplified": False,
            "source": "Commonly referenced in classical and traditional texts",
            "condition_met": f"Sun and Mercury both in {sun_sign}",
            "effect": "Associated with sharp intellect, communication skills, and analytical ability.",
            "caveat": (
                "Mercury is combust under the configured orb, so this yoga "
                "requires substantial contextual review."
                if is_combust else
                "Mercury is not combust under the configured orb, which removes "
                "one common weakening condition."
            ),
            "combust": is_combust
        }
    return {"name": "Budhaditya Yoga", "present": False}


def check_kendra_trikona_raj_yoga(chart: dict, ascendant_sign: str, zodiac_signs: list) -> dict:
    """
    A simplified Raja Yoga check: lord of a Kendra house and lord of a Trikona house
    (1,5,9) are conjunct or in mutual aspect (same sign = conjunction, simplified here).
    This is a SIMPLIFIED version - full Raja Yoga analysis requires house lordship
    mapping based on ascendant, which we compute here.
    """
    # House lordships based on ascendant (whole sign)
    sign_rulers = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

    asc_index = zodiac_signs.index(ascendant_sign)

    def sign_of_house(house_num):
        return zodiac_signs[(asc_index + house_num - 1) % 12]

    kendra_lords = set()
    for h in KENDRA_HOUSES:
        kendra_lords.add(sign_rulers[sign_of_house(h)])

    trikona_lords = set()
    for h in TRIKONA_HOUSES:
        trikona_lords.add(sign_rulers[sign_of_house(h)])

    # Check if any kendra lord and trikona lord are conjunct (same sign in the chart)
    detected = []
    for k_lord in kendra_lords:
        for t_lord in trikona_lords:
            if k_lord == t_lord:
                continue  # same planet, not a yoga between two lords
            if k_lord in chart["planets"] and t_lord in chart["planets"]:
                if chart["planets"][k_lord]["sign"] == chart["planets"][t_lord]["sign"]:
                    detected.append((k_lord, t_lord, chart["planets"][k_lord]["sign"]))

    if detected:
        pairs_str = ", ".join([f"{a} (Kendra lord) + {b} (Trikona lord) in {sign}" for a, b, sign in detected])
        return {
            "name": "Raja Yoga (Kendra-Trikona Lord Conjunction)",
            "present": True,
            "involved_planets": sorted({
                planet
                for first, second, _ in detected
                for planet in (first, second)
            }),
            "simplified": True,
            "source": "General Raja Yoga principle, BPHS",
            "condition_met": pairs_str,
            "effect": "Indicates potential for rise in status, authority, and success — "
                      "particularly relevant during the dasha periods of these planets.",
            "caveat": "This is a foundational Raja Yoga indicator. Its actual strength depends "
                      "heavily on the dignity of the involved planets and the houses they occupy. "
                      "A debilitated planet forming this yoga gives much weaker results."
        }
    return {"name": "Raja Yoga (Kendra-Trikona Lord Conjunction)", "present": False}


def check_chandra_mangal_yoga(chart: dict) -> dict:
    """
    Chandra-Mangal Yoga: Moon and Mars conjunct (same sign).
    Classical source: commonly cited, associated with financial resourcefulness.
    """
    moon_sign = chart["planets"]["Moon"]["sign"]
    mars_sign = chart["planets"]["Mars"]["sign"]

    if moon_sign == mars_sign:
        return {
            "name": "Chandra-Mangal Yoga",
            "present": True,
            "involved_planets": ["Moon", "Mars"],
            "simplified": False,
            "source": "Commonly referenced in traditional texts",
            "condition_met": f"Moon and Mars both in {moon_sign}",
            "effect": "Associated with financial resourcefulness, business acumen, "
                      "and the ability to generate wealth through effort and initiative.",
            "caveat": "The expression of this yoga depends significantly on the dignity "
                      "of both Moon and Mars, and the house they occupy. Afflicted placements "
                      "may channel this energy into impulsiveness around finances rather than "
                      "steady accumulation."
        }
    return {"name": "Chandra-Mangal Yoga", "present": False}


def check_neecha_bhanga_raja_yoga(chart: dict, ascendant_sign: str, zodiac_signs: list) -> dict:
    """
    Neecha Bhanga Raja Yoga (simplified): A debilitated planet's debilitation is
    'cancelled' if the lord of the sign it's debilitated in is placed in a Kendra
    from the Ascendant or Moon, OR if the dispositor of the debilitated planet
    is also in a Kendra. This is a SIMPLIFIED check covering one common condition:
    the lord of the debilitation sign is in a Kendra house from the ascendant.

    Classical source: BPHS, various chapters on planetary strength
    """
    sign_rulers = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

    asc_index = zodiac_signs.index(ascendant_sign)
    detected = []

    for planet, data in chart["planets"].items():
        if data.get("dignity", {}).get("status") == "Debilitated":
            debilitation_sign = data["sign"]
            dispositor = sign_rulers[debilitation_sign]

            if dispositor in chart["planets"]:
                dispositor_sign = chart["planets"][dispositor]["sign"]
                dispositor_index = zodiac_signs.index(dispositor_sign)
                house_from_asc = ((dispositor_index - asc_index) % 12) + 1

                if house_from_asc in [1, 4, 7, 10]:
                    detected.append((planet, debilitation_sign, dispositor, house_from_asc))

    if detected:
        details = ", ".join([
            f"{p} debilitated in {sign}, but its dispositor {disp} is in Kendra (house {h})"
            for p, sign, disp, h in detected
        ])
        return {
            "name": "Neecha Bhanga Raja Yoga (Debilitation Cancellation)",
            "present": True,
            "involved_planets": sorted({
                planet
                for debilitated, _, dispositor, _ in detected
                for planet in (debilitated, dispositor)
            }),
            "simplified": True,
            "source": "BPHS - planetary strength principles",
            "condition_met": details,
            "effect": "A planet's debilitation may be substantially 'cancelled' or even "
                      "transformed into a source of strength, often associated with "
                      "unexpected rises in fortune, particularly during that planet's dasha.",
            "caveat": "This is a SIMPLIFIED check based on one classical condition for "
                      "debilitation cancellation (dispositor in Kendra). Full assessment "
                      "requires checking multiple cancellation conditions (e.g. exalted "
                      "planet aspecting, debilitated planet in Kendra from Moon, etc.). "
                      "Treat this as a flag for further manual review, not a final verdict."
        }
    return {"name": "Neecha Bhanga Raja Yoga (Debilitation Cancellation)", "present": False}


def check_pancha_mahapurusha_yogas(chart: dict, ascendant_sign: str, zodiac_signs: list) -> dict:
    """
    Pancha Mahapurusha Yogas: A planet (Mars, Mercury, Jupiter, Venus, or Saturn)
    is exalted or in its own sign AND placed in a Kendra house from the Ascendant.
    Each planet has its own named yoga: Ruchaka (Mars), Bhadra (Mercury),
    Hamsa (Jupiter), Malavya (Venus), Sasa (Saturn).

    Classical source: BPHS Ch. 75
    """
    yoga_names = {
        "Mars": "Ruchaka Yoga",
        "Mercury": "Bhadra Yoga",
        "Jupiter": "Hamsa Yoga",
        "Venus": "Malavya Yoga",
        "Saturn": "Sasa Yoga"
    }

    asc_index = zodiac_signs.index(ascendant_sign)
    detected = []

    for planet, yoga_name in yoga_names.items():
        data = chart["planets"][planet]
        dignity_status = data.get("dignity", {}).get("status")

        if dignity_status in ["Exalted", "Own Sign (Swakshetra)"]:
            planet_sign_index = zodiac_signs.index(data["sign"])
            house_from_asc = ((planet_sign_index - asc_index) % 12) + 1

            if house_from_asc in [1, 4, 7, 10]:
                detected.append((planet, yoga_name, dignity_status, house_from_asc))

    if detected:
        names = ", ".join([f"{yn} ({p}, {ds} in House {h})" for p, yn, ds, h in detected])
        return {
            "name": "Pancha Mahapurusha Yoga(s)",
            "present": True,
            "involved_planets": sorted({planet for planet, _, _, _ in detected}),
            "simplified": False,
            "source": "Brihat Parashara Hora Shastra, Ch. 75",
            "condition_met": names,
            "effect": "These yogas are associated with exceptional strength in the "
                      "significations of the planet involved - e.g. Ruchaka (Mars) with "
                      "courage and leadership, Hamsa (Jupiter) with wisdom and prosperity, "
                      "Malavya (Venus) with comfort and artistic refinement, Bhadra (Mercury) "
                      "with intelligence and communication, Sasa (Saturn) with discipline "
                      "and authority.",
            "caveat": "These are considered powerful yogas, but their full expression still "
                      "depends on the planet's relationship with the dasha periods, aspects "
                      "from other planets, and the overall chart context. Presence of the "
                      "yoga indicates potential, not a guarantee of outcome."
        }
    return {"name": "Pancha Mahapurusha Yoga(s)", "present": False}


def check_kemadruma_yoga(chart: dict, ascendant_sign: str, zodiac_signs: list) -> dict:
    """
    Kemadruma Yoga (simplified): Moon has no planets in the houses immediately
    before or after it (2nd and 12th from Moon), and no planets conjunct it.
    This is traditionally considered a challenging yoga, though many classical
    cancellation conditions exist.

    Classical source: BPHS - commonly cited challenging yoga
    """
    moon_sign = chart["planets"]["Moon"]["sign"]
    moon_sign_index = zodiac_signs.index(moon_sign)

    # Houses 2nd and 12th from Moon (adjacent signs)
    adjacent_signs = [
        zodiac_signs[(moon_sign_index + 1) % 12],  # 2nd from Moon
        zodiac_signs[(moon_sign_index - 1) % 12],  # 12th from Moon
    ]

    other_planets = [p for p in chart["planets"] if p != "Moon"]

    # Check if any planet is conjunct Moon or in adjacent signs
    has_support = False
    for planet in other_planets:
        planet_sign = chart["planets"][planet]["sign"]
        if planet_sign == moon_sign or planet_sign in adjacent_signs:
            has_support = True
            break

    if not has_support:
        moon_house = get_house_of_planet(
            moon_sign, ascendant_sign, zodiac_signs
        )
        cancellations = []
        if moon_house in KENDRA_HOUSES:
            cancellations.append(
                f"Moon is in Kendra house {moon_house} from the Ascendant"
            )

        planets_in_kendra_from_moon = []
        for planet in other_planets:
            planet_sign = chart["planets"][planet]["sign"]
            relative_house = (
                (
                    zodiac_signs.index(planet_sign)
                    - moon_sign_index
                ) % 12
            ) + 1
            if relative_house in [4, 7, 10]:
                planets_in_kendra_from_moon.append(planet)
        if planets_in_kendra_from_moon:
            cancellations.append(
                "Planets in Kendra from Moon: "
                + ", ".join(sorted(planets_in_kendra_from_moon))
            )

        return {
            "name": "Kemadruma Yoga",
            "present": True,
            "involved_planets": ["Moon"],
            "simplified": True,
            "source": "BPHS - classical challenging yoga",
            "condition_met": f"No planets conjunct Moon (in {moon_sign}) or in the signs "
                            f"immediately before/after it",
            "effect": "Traditionally associated with periods of struggle, feeling unsupported, "
                      "or having to be self-reliant - particularly during Moon's dasha periods.",
            "caveat": "IMPORTANT: Classical texts describe MANY cancellation conditions for "
                      "this yoga (e.g. Moon in a Kendra, Moon aspected by Jupiter, strong "
                      "benefics in Kendras from ascendant, etc.) which are NOT checked by "
                      "this simplified detection. A 'present: true' result here should be "
                      "treated as a preliminary flag only, NOT a confirmed reading. Many "
                      "charts that technically meet this base condition have the yoga fully "
                      "cancelled by other factors.",
            "cancellation_status": (
                "cancellation_indicated"
                if cancellations
                else "no_checked_cancellation_found"
            ),
            "cancellation_evidence": cancellations,
        }
    return {"name": "Kemadruma Yoga", "present": False}



def detect_all_yogas(chart: dict, ascendant_sign: str, zodiac_signs: list) -> list:
    """
    Run all yoga checks and return only those that are present.
    """
    checks = [
        check_gajakesari_yoga(chart, ascendant_sign, zodiac_signs),
        check_budhaditya_yoga(chart),
        check_kendra_trikona_raj_yoga(chart, ascendant_sign, zodiac_signs),
        check_chandra_mangal_yoga(chart),
        check_neecha_bhanga_raja_yoga(chart, ascendant_sign, zodiac_signs),
        check_pancha_mahapurusha_yogas(chart, ascendant_sign, zodiac_signs),
        check_kemadruma_yoga(chart, ascendant_sign, zodiac_signs),
    ]

    detected = [yoga for yoga in checks if yoga.get("present")]
    for yoga in detected:
        yoga["strength_assessment"] = assess_yoga_strength(yoga, chart)
    return detected


def assess_yoga_strength(yoga: dict, chart: dict) -> dict:
    """Build a transparent preliminary strength assessment for a detected yoga."""
    score = 0
    evidence = []

    for planet in yoga.get("involved_planets", []):
        data = chart["planets"].get(planet)
        if not data:
            continue
        dignity = data.get("dignity", {}).get("status", "Unknown")
        dignity_score = {
            "Exalted": 2,
            "Own Sign (Swakshetra)": 2,
            "Friendly Sign": 1,
            "Enemy Sign": -1,
            "Debilitated": -2,
        }.get(dignity, 0)
        combust = data.get("combustion", {}).get("is_combust", False)
        score += dignity_score
        if combust:
            score -= 1
        evidence.append({
            "planet": planet,
            "dignity": dignity,
            "combust": combust,
            "score_contribution": dignity_score - (1 if combust else 0),
        })

    if yoga.get("cancellation_status") == "cancellation_indicated":
        score -= 3
        label = "Cancellation indicated; treat as strongly mitigated"
    elif yoga.get("simplified"):
        label = "Preliminary flag requiring manual review"
    elif score >= 3:
        label = "Strong supporting conditions"
    elif score >= 1:
        label = "Moderate supporting conditions"
    else:
        label = "Limited or mixed supporting conditions"

    return {
        "score": score,
        "label": label,
        "planetary_evidence": evidence,
        "note": (
            "This score is an internal evidence summary, not a classical numeric "
            "measure or outcome probability."
        ),
    }


if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "calculations"))

    from datetime import datetime
    from chart import compute_chart
    from dignity import annotate_chart_with_dignity_and_navamsa, ZODIAC_SIGNS

    test_dt_utc = datetime(1990, 8, 15, 9, 0)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    chart = compute_chart(test_dt_utc, delhi_lat, delhi_lon)
    chart = annotate_chart_with_dignity_and_navamsa(chart)
    ascendant_sign = chart["ascendant"]["sign"]

    yogas = detect_all_yogas(chart, ascendant_sign, ZODIAC_SIGNS)

    print(f"Ascendant: {ascendant_sign}\n")
    print(f"Detected Yogas ({len(yogas)}):\n")
    for yoga in yogas:
        print(f"• {yoga['name']}")
        print(f"  Source: {yoga['source']}")
        print(f"  Condition: {yoga['condition_met']}")
        print(f"  Effect: {yoga['effect']}")
        if "caveat" in yoga:
            print(f"  Note: {yoga['caveat']}")
        print()
