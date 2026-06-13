"""
Classical house (bhava) significations - Vedic astrology.
These are well-established across traditions (BPHS and general Jyotish consensus)
and serve as grounded reference data for the interpretation layer.
"""

HOUSE_SIGNIFICATIONS = {
    1: {
        "name": "Tanu Bhava (House of Self)",
        "significations": "Physical body, personality, overall vitality, general life approach, "
                          "self-image, and how one presents to the world."
    },
    2: {
        "name": "Dhana Bhava (House of Wealth)",
        "significations": "Accumulated wealth, family values, speech, food habits, "
                          "and material resources/possessions."
    },
    3: {
        "name": "Sahaja Bhava (House of Siblings)",
        "significations": "Siblings, courage, short journeys, communication skills, "
                          "and self-effort/initiative."
    },
    4: {
        "name": "Sukha Bhava (House of Happiness)",
        "significations": "Home, mother, domestic comfort, emotional foundation, "
                          "property, and education (early schooling)."
    },
    5: {
        "name": "Putra Bhava (House of Children)",
        "significations": "Children, creativity, intelligence, learning, romance, "
                          "and accumulated merit (purva punya)."
    },
    6: {
        "name": "Ripu Bhava (House of Obstacles)",
        "significations": "Health challenges, daily routine, competitors, debts, "
                          "service to others, and effort needed to overcome difficulties."
    },
    7: {
        "name": "Kalatra Bhava (House of Partnerships)",
        "significations": "Marriage, business partnerships, significant relationships, "
                          "and how one relates to others one-on-one."
    },
    8: {
        "name": "Ayur Bhava (House of Transformation)",
        "significations": "Longevity, deep transformation, inheritance, hidden matters, "
                          "and major life changes/crises."
    },
    9: {
        "name": "Dharma Bhava (House of Higher Purpose)",
        "significations": "Father, higher learning, philosophy, long journeys, "
                          "spiritual practice, and one's sense of purpose/belief system."
    },
    10: {
        "name": "Karma Bhava (House of Career)",
        "significations": "Career, public reputation, professional achievements, "
                          "authority figures, and one's role/status in society."
    },
    11: {
        "name": "Labha Bhava (House of Gains)",
        "significations": "Income, social networks, friendships, communities, "
                          "and fulfillment of desires/aspirations."
    },
    12: {
        "name": "Vyaya Bhava (House of Loss/Liberation)",
        "significations": "Expenses, foreign connections, solitude, spiritual liberation, "
                          "and matters that involve letting go or stepping back."
    },
}


def get_house_signification(house_num: int) -> dict:
    """Return the name and significations for a given house number (1-12)."""
    return HOUSE_SIGNIFICATIONS.get(house_num, {
        "name": "Unknown",
        "significations": "No data available"
    })