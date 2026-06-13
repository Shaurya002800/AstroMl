"""
Main report generator - consolidates all computed astrological data
into a single structured JSON output.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "calculations"))
sys.path.append(os.path.join(os.path.dirname(__file__), "knowledge_base"))

from datetime import datetime
from chart import compute_chart
from dignity import annotate_chart_with_dignity_and_navamsa, ZODIAC_SIGNS
from divisional_charts import annotate_chart_with_divisional_charts, get_dasamsa_lagna_and_houses
from dasha import get_current_dasha
from ashtakavarga import compute_sarvashtakavarga, interpret_house_strength
from yogas import detect_all_yogas
from house_significations import get_house_signification

def generate_full_report(birth_datetime_utc: datetime, lat: float, lon: float,
                          query_datetime: datetime = None) -> dict:
    """
    Generate a complete structured astrological report.

    Args:
        birth_datetime_utc: birth date/time converted to UTC
        lat, lon: birth place coordinates
        query_datetime: date for which dasha should be evaluated (default: now)

    Returns:
        A dict containing all computed chart data, ready to be passed to
        the LLM interpretation layer.
    """

    # Layer 1: Core chart
    chart = compute_chart(birth_datetime_utc, lat, lon)

    # Layer 1b: Dignity + Navamsa (D9)
    chart = annotate_chart_with_dignity_and_navamsa(chart)

    # Layer 1c: Divisional charts (D10, D7)
    chart = annotate_chart_with_divisional_charts(chart)

    ascendant_sign = chart["ascendant"]["sign"]

    # Layer 1d: Dasha timeline
    moon_longitude = chart["planets"]["Moon"]["longitude"]
    dasha_info = get_current_dasha(birth_datetime_utc, moon_longitude, query_datetime)

    # Layer 1e: Ashtakavarga
    ashtakavarga = compute_sarvashtakavarga(chart, ascendant_sign)

    # Layer 2: Yogas (rules engine)
    yogas = detect_all_yogas(chart, ascendant_sign, ZODIAC_SIGNS)

    # D10 house placements (career)
    d10_houses = get_dasamsa_lagna_and_houses(chart)

    # --- Build the consolidated report ---

    report = {
        "meta": {
            "birth_datetime_utc": birth_datetime_utc.isoformat(),
            "birth_location": {"latitude": lat, "longitude": lon},
            "query_date": (query_datetime or datetime.now()).isoformat()
        },

        "ascendant": {
            "sign": chart["ascendant"]["sign"],
            "degree": chart["ascendant"]["degree"],
            "nakshatra": chart["ascendant"]["nakshatra"],
            "pada": chart["ascendant"]["pada"],
        },

        "planets": {},

        "current_dasha": {
            "mahadasha": {
                "lord": dasha_info["mahadasha"]["lord"],
                "start": dasha_info["mahadasha"]["start"].isoformat(),
                "end": dasha_info["mahadasha"]["end"].isoformat(),
            },
            "antardasha": {
                "lord": dasha_info["antardasha"]["lord"],
                "start": dasha_info["antardasha"]["start"].isoformat(),
                "end": dasha_info["antardasha"]["end"].isoformat(),
            } if dasha_info.get("antardasha") else None
        },

        "ashtakavarga": {
            "sarva_by_house": {
                str(house): {
                    "sign": data["sign"],
                    "bindus": data["total_bindus"],
                    "strength": interpret_house_strength(data["total_bindus"]),
                    "house_name": get_house_signification(house)["name"],
                    "house_significations": get_house_signification(house)["significations"]
                }
                for house, data in ashtakavarga["sarva_by_house"].items()
            },
            "validation_total": ashtakavarga["total_sum"]  # should be 337
        },

        "yogas": yogas,

        "d10_career_chart": {
            "ascendant_sign": d10_houses["d10_ascendant_sign"],
            "planets_by_house": {
                str(h): planets for h, planets in d10_houses["planets_by_house"].items()
            }
        }
    }

    # Populate planet details
    for planet, data in chart["planets"].items():
        report["planets"][planet] = {
            "sign": data["sign"],
            "degree": round(data["degree"], 2),
            "nakshatra": data["nakshatra"],
            "pada": data["pada"],
            "dignity": data["dignity"]["status"],
            "dignity_note": data["dignity"]["note"],
            "navamsa_sign": data["navamsa_sign"],
            "dasamsa_sign": data["dasamsa_sign"],
            "saptamsa_sign": data["saptamsa_sign"],
        }

    return report


if __name__ == "__main__":
    import json

    test_dt_utc = datetime(1990, 8, 15, 9, 0)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    report = generate_full_report(test_dt_utc, delhi_lat, delhi_lon)

    print(json.dumps(report, indent=2, default=str))