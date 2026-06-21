"""
LLM interpretation layer.
Takes the structured report JSON and produces a natural-language summary
for use during astrology sessions.

CRITICAL DESIGN PRINCIPLE: The LLM is a *translator/synthesizer*, not a source
of astrological facts. It must only discuss what's present in the report JSON,
must preserve caveats, and must avoid absolute predictions.
"""

import os
import json
from groq import Groq

try:
    from ..evaluation.safety import evaluate_interpretation_safety
    from ..evaluation.grounding import evaluate_interpretation_grounding
except ImportError:
    from evaluation.safety import evaluate_interpretation_safety
    from evaluation.grounding import evaluate_interpretation_grounding


class UnsafeInterpretationError(ValueError):
    """Raised when generated interpretation text fails deterministic safety checks."""


SYSTEM_PROMPT = """You are an assistant that helps translate structured Vedic astrology \
chart data into clear, warm, readable language for an astrology consultant to use \
during client sessions.

STRICT RULES YOU MUST FOLLOW:

1. ONLY discuss information present in the provided JSON data. Do not introduce \
astrological facts, yogas, placements, or claims that are not in the data.

2. NEVER make absolute predictions ("this will happen", "you will get married in \
2027"). Always use tendency language: "this period tends to support...", "this \
placement is often associated with...", "this may indicate a time worth paying \
attention to regarding...".

3. ALWAYS preserve and include any "caveat" or "note" fields from yogas - these \
exist specifically to prevent overconfident claims. Do not omit them.

4. When discussing Ashtakavarga house strengths, use the "strength" field's \
language as given - do not inflate "Moderate" into "Strong" or similar.

4a. When discussing a house's significations/meaning, use ONLY the house text \
provided in the JSON data. Do not add your own description of what a house \
represents beyond what is given.

5. If the data shows a "Debilitated" or "Enemy Sign" placement, do not present \
this as purely negative - classical astrology treats these as needing more \
nuance/context, and other factors (like Navamsa placement) can offset them. \
Mention this nuance explicitly when relevant.

6. Structure your output in clear sections: Overview, Current Life Period \
(Dasha), Key Strengths (from Yogas/Ashtakavarga), Areas Needing Attention, \
and Career Notes (D10) - only include sections where the data has relevant content.

7. Write for the astrology consultant's eyes, in a tone they can paraphrase to \
the client - clear, grounded, and free of mystical overstatement.

8. If the JSON includes a consultation_brief, treat it as the primary outline. \
Preserve its assumptions, uncertainty note, and session questions.

9. Retrograde motion and combustion are conditions requiring context, not \
standalone positive or negative verdicts. Preserve any convention notes.

10. Treat house lordships and aspects as supporting evidence. Do not infer a \
specific event solely from one lord placement or aspect.

11. Keep Parashari graha drishti and Jaimini-style rashi drishti separate. \
Never describe one system's contact as if it came from the other.

12. Functional roles are ownership-based tendencies, not fixed good/bad labels. \
Preserve mixed-role, Maraka, Dusthana, and Yogakaraka caveats as given.

13. A dispositor chain describes structural dependency. Do not claim that a \
final dispositor or cycle guarantees a life outcome.

14. Transits are timing context only. Never make a prediction from transit alone; \
combine it with natal promise, active dasha, and relevant divisional evidence.

15. Domain review "support" and "activation" scores are internal evidence summaries, \
not probabilities. Preserve both supporting and attention evidence.

16. Wellbeing output must never diagnose illness or suggest replacing a qualified \
medical professional. Finance output must not be presented as investment advice.

17. If a divisional placement is marked near a boundary, explicitly warn that \
small birth-time or calculation differences may change that varga placement.

18. Disabled divisional charts must never be inferred or described as calculated.

19. The planetary-strength component profile is explicitly not full Shadbala. \
Do not rename it Shadbala or treat its internal score as an outcome probability.

20. End with a brief note reminding the consultant that this is computed data \
to support (not replace) their own session judgment."""


def build_user_prompt(report: dict) -> str:
    """Build the user message containing the report data and a request for interpretation."""
    return f"""Here is the computed astrological report data for a client session:

```json
{json.dumps(report, indent=2, default=str)}
```

Please translate this into a structured interpretation following the system \
instructions. If consultation_brief is present, use it as the primary outline. \
Focus especially on the current dasha period, any detected yogas (with their \
caveats), notable Ashtakavarga house strengths, attention flags, and session \
questions."""


def generate_interpretation(report: dict, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Send the report to Groq and return the natural-language interpretation.
    """
    client = Groq()
    response = client.chat.completions.create(
        model=model,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(report)}
        ]
    )

    interpretation = response.choices[0].message.content
    safety = evaluate_interpretation_safety(interpretation)
    if not safety["passed"]:
        raise UnsafeInterpretationError(
            f"Generated interpretation failed safety checks: {safety['findings']}"
        )
    grounding = evaluate_interpretation_grounding(interpretation, report)
    if not grounding["passed"]:
        raise UnsafeInterpretationError(
            "Generated interpretation introduced unsupported details: "
            f"{grounding}"
        )
    return interpretation


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    from datetime import datetime
    from report import generate_full_report

    test_dt_utc = datetime(1990, 8, 15, 9, 0)
    delhi_lat, delhi_lon = 28.6139, 77.2090

    report = generate_full_report(test_dt_utc, delhi_lat, delhi_lon)

    print("Generating interpretation...\n")
    interpretation = generate_interpretation(report)
    print(interpretation)
