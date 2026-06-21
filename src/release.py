"""Version and known-limitations metadata included in every report."""

ENGINE_VERSION = "0.5.1"

KNOWN_LIMITATIONS = [
    "Astrology is interpretive and is not scientifically validated as a method for predicting life events.",
    "D16, D24, and D60 are disabled pending convention selection and independent validation.",
    "The planetary-strength profile is not full Shadbala.",
    "The yoga catalogue is incomplete and several rules remain simplified.",
    "Only internal regression fixtures exist; independent software-verified fixtures are still required.",
    "Birth-time sensitivity is not birth-time rectification.",
    "Domain support and activation scores are internal evidence summaries, not probabilities.",
]


def build_release_metadata() -> dict:
    return {
        "engine_version": ENGINE_VERSION,
        "production_readiness": "pilot_only",
        "known_limitations": KNOWN_LIMITATIONS,
    }
