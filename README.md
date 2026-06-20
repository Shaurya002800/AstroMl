# Serenova Astrology Session Tool

Internal astrology consultation assistant for generating structured Vedic chart data and a guarded session interpretation.

This is not the public website. The intended user is the consultant during a live session.

## Current Architecture

1. Birth details are entered in Streamlit.
2. Swiss Ephemeris computes sidereal planetary positions using Lahiri ayanamsa.
3. Deterministic modules calculate chart features: D1, D9, D10, D7, Vimshottari dasha through Pratyantar, dignity, motion, combustion, whole-sign house lordships, functional roles, dispositors, Parashari aspects, query-date transits, Ashtakavarga, and selected yogas.
4. `astrology_model.py` converts computed facts into a consultation brief with caveats, confidence notes, and suggested follow-up questions.
5. The LLM layer translates only the structured facts into natural language for the consultant.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
streamlit run src/app.py
```

Set `GROQ_API_KEY` in your environment before generating LLM interpretations.

## Design Principle

The AI should not invent astrology. The trusted source of astrological facts is the deterministic calculation and rule engine. The LLM is only a translator and session-writing assistant.

Astrology should be presented as interpretive guidance, not guaranteed prediction. The tool must avoid absolute claims, medical/legal/financial certainty, and fear-based language.

## Current Conventions

- Lahiri ayanamsa.
- Whole-sign houses for lordships, yogas, and Parashari aspects.
- Mean lunar node for Rahu; Ketu is derived at 180 degrees.
- Node aspects are excluded because Jyotish traditions differ.
- Combustion thresholds are explicit working conventions and are returned with the computed result.
- Functional roles are ownership-based tendencies, not unconditional benefic/malefic verdicts.
- Transits are mapped from natal Ascendant and Moon and must be combined with natal and dasha evidence.

## Development Checks

```bash
python3 -m unittest discover -s tests
python3 src/report.py
```
