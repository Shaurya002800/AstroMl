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

client = Groq()  # reads GROQ_API_KEY from environment


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

4a. When discussing a house's significations/meaning, use ONLY the "house_significations" \
text provided for that house in the data. Do not add your own description of what a \
house represents beyond what is given.

5. If the data shows a "Debilitated" or "Enemy Sign" placement, do not present \
this as purely negative - classical astrology treats these as needing more \
nuance/context, and other factors (like Navamsa placement) can offset them. \
Mention this nuance explicitly when relevant.

6. Structure your output in clear sections: Overview, Current Life Period \
(Dasha), Key Strengths (from Yogas/Ashtakavarga), Areas Needing Attention, \
and Career Notes (D10) - only include sections where the data has relevant content.

7. Write for the astrology consultant's eyes, in a tone they can paraphrase to \
the client - clear, grounded, and free of mystical overstatement.

8. End with a brief note reminding the consultant that this is computed data \
to support (not replace) their own session judgment."""


def build_user_prompt(report: dict) -> str:
    """Build the user message containing the report data and a request for interpretation."""
    return f"""Here is the computed astrological report data for a client session:

```json
{json.dumps(report, indent=2, default=str)}
```

Please translate this into a structured interpretation following the system \
instructions. Focus especially on the current dasha period, any detected yogas \
(with their caveats), and notable Ashtakavarga house strengths (very strong or \
very weak houses)."""


def generate_interpretation(report: dict, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Send the report to Groq and return the natural-language interpretation.
    """
    response = client.chat.completions.create(
        model=model,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(report)}
        ]
    )

    return response.choices[0].message.content


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