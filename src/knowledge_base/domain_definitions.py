"""
Bounded consultation domains and the chart factors used to review them.

These definitions select evidence; they do not define guaranteed outcomes.
"""

DOMAIN_DEFINITIONS = {
    "career": {
        "label": "Career and Public Role",
        "houses": [2, 6, 10, 11],
        "planets": ["Sun", "Mercury", "Jupiter", "Saturn"],
        "divisional_chart": "D10",
        "consultant_prompt": (
            "Ask about current responsibilities, professional direction, "
            "recognition, workload, and income from work."
        ),
    },
    "relationships": {
        "label": "Relationships and Partnership",
        "houses": [2, 5, 7, 8, 11],
        "planets": ["Moon", "Mars", "Jupiter", "Venus"],
        "divisional_chart": "D9",
        "consultant_prompt": (
            "Ask about partnership expectations, communication, family context, "
            "and whether the client is discussing an existing or future relationship."
        ),
    },
    "finance": {
        "label": "Finances and Resources",
        "houses": [2, 5, 9, 11],
        "planets": ["Mercury", "Jupiter", "Venus"],
        "divisional_chart": None,
        "consultant_prompt": (
            "Ask about income, savings, obligations, risk tolerance, and the "
            "difference between expected gains and current cash flow."
        ),
    },
    "education": {
        "label": "Education and Learning",
        "houses": [2, 4, 5, 9],
        "planets": ["Moon", "Mercury", "Jupiter"],
        "divisional_chart": "D24 (not implemented)",
        "consultant_prompt": (
            "Ask about the type of study, examination timeline, consistency, "
            "mentorship, and practical obstacles."
        ),
    },
    "wellbeing": {
        "label": "Wellbeing and Daily Balance",
        "houses": [1, 6, 8, 12],
        "planets": ["Sun", "Moon", "Mars", "Saturn"],
        "divisional_chart": None,
        "consultant_prompt": (
            "Ask about routines, energy, stress, sleep, and support. Do not make "
            "medical diagnoses or advise replacing professional care."
        ),
    },
}
