"""
Streamlit interface for the astrology report tool.
Run with: streamlit run app.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "calculations"))
sys.path.append(os.path.join(os.path.dirname(__file__), "knowledge_base"))
sys.path.append(os.path.join(os.path.dirname(__file__), "interpretation"))

import streamlit as st
from datetime import datetime, date, time
from timezonefinder import TimezoneFinder
import pytz

from report import generate_full_report
from session_log import save_session, list_sessions, load_session
from interpret import generate_interpretation
from cities import INDIAN_CITIES, get_city_list
from astrology_model import build_consultation_brief


st.set_page_config(page_title="Serenova Astrology Tool", page_icon="🪔", layout="centered")

st.title("🪔 Serenova — Astrology Session Tool")
st.caption("Internal tool · Enter client birth details to generate a chart report")

st.divider()

# --- Input form ---
with st.form("birth_details"):
    st.subheader("Client Birth Details")

    name = st.text_input("Client Name (optional)")

    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input(
            "Date of Birth",
            value=date(1990, 1, 1),
            min_value=date(1920, 1, 1),
            max_value=date.today()
        )
    with col2:
        birth_time = st.time_input("Time of Birth", value=time(12, 0))

    time_precision = st.selectbox(
        "Birth Time Accuracy",
        [
            ("exact", "Exact"),
            ("within_15_min", "Approx. within 15 minutes"),
            ("within_1_hour", "Approx. within 1 hour"),
            ("unknown", "Unknown / needs rectification"),
        ],
        format_func=lambda option: option[1],
    )[0]

    analysis_date = st.date_input(
        "Analysis Date",
        value=date.today(),
        min_value=date(1920, 1, 1),
        max_value=date(2100, 12, 31),
    )

    st.markdown("**Place of Birth**")

    city_options = ["-- Select a city --"] + get_city_list() + ["Other (enter manually)"]
    selected_city = st.selectbox("City", city_options)

    if selected_city == "Other (enter manually)":
        col3, col4 = st.columns(2)
        with col3:
            latitude = st.number_input("Latitude", value=28.6139, format="%.4f")
        with col4:
            longitude = st.number_input("Longitude", value=77.2090, format="%.4f")
        st.caption("Tip: search '[city name] latitude longitude' if unsure")
    elif selected_city == "-- Select a city --":
        latitude, longitude = 28.6139, 77.2090
        st.caption("Select a city above, or choose 'Other' to enter coordinates manually")
    else:
        latitude, longitude = INDIAN_CITIES[selected_city]
        st.caption(f"Coordinates: {latitude}, {longitude}") 

    submitted = st.form_submit_button("Generate Report", type="primary")


if submitted:
    with st.spinner("Calculating chart..."):
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=latitude, lng=longitude)
        if not tz_name:
            st.error("Could not detect timezone for this location. Please check latitude and longitude.")
            st.stop()
        local_tz = pytz.timezone(tz_name)
        local_dt = datetime.combine(birth_date, birth_time)
        localized_dt = local_tz.localize(local_dt)
        utc_dt = localized_dt.astimezone(pytz.utc).replace(tzinfo=None)
        analysis_local_dt = local_tz.localize(
            datetime.combine(analysis_date, time(12, 0))
        )
        analysis_utc_dt = analysis_local_dt.astimezone(pytz.utc).replace(tzinfo=None)

        report = generate_full_report(
            utc_dt,
            latitude,
            longitude,
            query_datetime=analysis_utc_dt,
        )
        consultation_brief = build_consultation_brief(report, time_precision=time_precision)
        model_payload = {
            "report": report,
            "consultation_brief": consultation_brief,
        }

    st.success("Chart calculated successfully")

    # --- Display raw computed data ---
    with st.expander("📊 View Raw Computed Data (Ascendant, Planets, Dasha, etc.)"):
        st.subheader("Ascendant")
        st.json(report["ascendant"])

        st.subheader("Planetary Positions")
        st.json(report["planets"])

        st.subheader("Current Dasha")
        st.json(report["current_dasha"])

        st.subheader("House Lordships")
        st.json(report["house_lordships"])

        st.subheader("Parashari Aspects")
        st.json(report["parashari_aspects"])

        st.subheader("Functional Planetary Roles")
        st.json(report["functional_roles"])

        st.subheader("Dispositor Analysis")
        st.json(report["dispositor_analysis"])

        st.subheader("Transits for Analysis Date")
        st.json(report["transits"])

        st.subheader("Ashtakavarga (House Strengths)")
        st.json(report["ashtakavarga"]["sarva_by_house"])

        st.subheader("Detected Yogas")
        if report["yogas"]:
            st.json(report["yogas"])
        else:
            st.write("No yogas detected from current rule set.")

        st.subheader("D10 Career Chart")
        st.json(report["d10_career_chart"])

    with st.expander("🧭 Consultant Brief (Deterministic Model Output)", expanded=True):
        st.json(consultation_brief)

    # --- LLM Interpretation ---
    st.divider()
    st.subheader("📝 Session Interpretation")

    with st.spinner("Generating interpretation..."):
        try:
            interpretation = generate_interpretation(model_payload)
            st.markdown(interpretation)

            # Save session
            birth_details = {
                "date": str(birth_date),
                "time": str(birth_time),
                "city": selected_city,
                "latitude": latitude,
                "longitude": longitude,
                "utc_datetime": str(utc_dt),
                "time_precision": time_precision,
                "analysis_date": str(analysis_date),
                "analysis_datetime_utc": str(analysis_utc_dt),
            }
            saved_path = save_session(name, birth_details, model_payload, interpretation)
            st.caption("✅ Session saved")

        except Exception as e:
            st.error(f"Could not generate interpretation: {e}")
            st.info("Raw computed data above is still available for manual review.")

st.divider()
st.subheader("📁 Past Sessions")

sessions = list_sessions()

if sessions:
    session_labels = [
        f"{s['timestamp'][:16].replace('T', ' ')} — {s['client_name'] or 'Unnamed'}"
        for s in sessions
    ]
    selected_idx = st.selectbox("Select a past session to view", range(len(sessions)),
                                  format_func=lambda i: session_labels[i])

    if st.button("Load Session"):
        session_data = load_session(sessions[selected_idx]["filename"])
        st.markdown("### Interpretation")
        st.markdown(session_data["interpretation"])
        with st.expander("Raw report data"):
            st.json(session_data["report"])
else:
    st.caption("No past sessions saved yet.")
