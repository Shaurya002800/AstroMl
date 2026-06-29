"""
Streamlit interface for the astrology report tool.
Run with: streamlit run app.py
"""

import os
import sys

SRC_DIR = os.path.dirname(__file__)
sys.path.insert(0, SRC_DIR)
sys.path.append(os.path.join(SRC_DIR, "calculations"))
sys.path.append(os.path.join(SRC_DIR, "knowledge_base"))
sys.path.append(os.path.join(SRC_DIR, "interpretation"))

import streamlit as st
from datetime import datetime, date, time
from timezonefinder import TimezoneFinder
import pytz

from report import generate_full_report
from session_log import save_session, list_sessions, load_session
from cities import (
    get_city_coordinates,
    get_city_list,
    get_state_list,
)
from astrology_model import build_consultation_brief
from feedback import save_feedback
from operational_status import build_operational_status
from presentation import (
    SUPPORTED_LANGUAGES,
    build_plain_language_report,
    render_plain_language_markdown,
)
from secure_storage import SecureStorageConfigurationError
from time_utils import local_datetime_to_utc


st.set_page_config(
    page_title="Serenova Astrology Tool",
    page_icon="🪔",
    layout="centered",
)


def inject_responsive_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 980px;
            padding-top: 1.25rem;
            padding-bottom: 2.5rem;
        }
        div[data-testid="stForm"] {
            border-radius: 8px;
        }
        div[data-testid="stExpander"] details {
            border-radius: 8px;
        }
        .stButton > button,
        .stDownloadButton button {
            min-height: 2.75rem;
        }
        @media (max-width: 760px) {
            .block-container {
                padding: 0.75rem 0.85rem 2rem;
            }
            h1 {
                font-size: 1.7rem;
                line-height: 1.2;
            }
            h2 {
                font-size: 1.3rem;
            }
            h3 {
                font-size: 1.05rem;
            }
            div[data-testid="stHorizontalBlock"] {
                gap: 0.35rem;
            }
            div[data-testid="stMetric"] {
                padding: 0.35rem 0;
            }
            .stButton > button,
            .stDownloadButton button {
                width: 100%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_responsive_styles()

st.title("🪔 Serenova — Astrology Session Tool")
st.caption("Internal tool · Enter client birth details to generate a chart report")

operational_status = build_operational_status()
status_label = (
    "Ready for paid production"
    if operational_status["production_ready"]
    else "Pilot only"
)
status_message = (
    f"{status_label}: "
    f"{len(operational_status['blocking_items'])} release gates remaining"
)
if operational_status["production_ready"]:
    st.success(status_message)
else:
    st.warning(status_message)

with st.expander("Production readiness"):
    st.markdown(f"**Engine:** {operational_status['engine_version']}")
    st.markdown(f"**Status:** {status_label}")
    current_fixtures = operational_status[
        "independent_reference_fixture_count"
    ]
    required_fixtures = operational_status[
        "required_independent_reference_fixtures"
    ]
    st.progress(
        min(current_fixtures / required_fixtures, 1.0),
        text=(
            "Independent reference fixtures: "
            f"{current_fixtures}/{required_fixtures}"
        ),
    )

    if operational_status["blocking_items"]:
        st.markdown("**Next required actions**")
        for item in operational_status["blocking_items"][:6]:
            st.markdown(f"- **{item['label']}**: {item['next_step']}")
    else:
        st.markdown("All release gates are currently passing.")

language_label = st.segmented_control(
    "Report Language",
    list(SUPPORTED_LANGUAGES),
    default="English",
    key="report_language_label",
)
report_language = SUPPORTED_LANGUAGES[language_label or "English"]

st.divider()

TIME_PRECISION_OPTIONS = {
    "exact": "Exact",
    "within_15_min": "Approx. within 15 minutes",
    "within_1_hour": "Approx. within 1 hour",
    "unknown": "Unknown / needs rectification",
}

LOCAL_TIME_POLICIES = {
    "raise": "Ask if local time is ambiguous or nonexistent",
    "earlier": "Use earlier occurrence for repeated clock time",
    "later": "Use later occurrence for repeated clock time",
    "shift_forward": "Shift nonexistent clock time forward",
}

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

    time_precision_label = st.selectbox(
        "Birth Time Accuracy",
        list(TIME_PRECISION_OPTIONS.values()),
    )
    time_precision = next(
        key
        for key, label in TIME_PRECISION_OPTIONS.items()
        if label == time_precision_label
    )

    analysis_date = st.date_input(
        "Analysis Date",
        value=date.today(),
        min_value=date(1920, 1, 1),
        max_value=date(2100, 12, 31),
    )

    local_time_policy_label = st.selectbox(
        "Clock-Change Handling",
        list(LOCAL_TIME_POLICIES.values()),
    )
    local_time_policy = next(
        key
        for key, label in LOCAL_TIME_POLICIES.items()
        if label == local_time_policy_label
    )

    st.markdown("**Place of Birth**")

    state_options = [
        "-- Select state / union territory --",
        *get_state_list(),
        "Other / Outside India",
    ]
    selected_state = st.selectbox(
        "State / Union Territory",
        state_options,
    )
    selected_city = ""
    birth_place_label = ""

    if selected_state == "Other / Outside India":
        birth_place_label = st.text_input("Birth Place Name")
        col3, col4 = st.columns(2)
        with col3:
            latitude = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=None,
                format="%.4f",
            )
        with col4:
            longitude = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=None,
                format="%.4f",
            )
        st.caption("Tip: search '[city name] latitude longitude' if unsure")
    elif selected_state == "-- Select state / union territory --":
        latitude, longitude = None, None
        st.caption("Select the birth state or union territory first")
    else:
        city_options = ["-- Select city --", *get_city_list(selected_state)]
        selected_city = st.selectbox("City", city_options)
        coordinates = get_city_coordinates(
            selected_city,
            selected_state,
        )
        if coordinates:
            latitude, longitude = coordinates
            birth_place_label = f"{selected_city}, {selected_state}"
            st.caption(f"Coordinates: {latitude}, {longitude}")
        else:
            latitude, longitude = None, None
            st.caption("Select the birth city")

    submitted = st.form_submit_button("Generate Report", type="primary")


if submitted:
    if latitude is None or longitude is None:
        st.error(
            "Select a state and city, or enter confirmed manual coordinates."
        )
        st.stop()
    if selected_state == "Other / Outside India" and not birth_place_label.strip():
        st.error("Enter the birth place name for a manual location.")
        st.stop()

    with st.spinner("Calculating chart..."):
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=latitude, lng=longitude)
        if not tz_name:
            st.error("Could not detect timezone for this location. Please check latitude and longitude.")
            st.stop()
        local_dt = datetime.combine(birth_date, birth_time)
        try:
            utc_dt = local_datetime_to_utc(
                local_dt,
                tz_name,
                policy=local_time_policy,
            )
        except (pytz.AmbiguousTimeError, pytz.NonExistentTimeError) as error:
            st.error(
                "The entered local birth time is ambiguous or did not exist "
                "because the clock changed. Select an appropriate "
                "Clock-Change Handling option."
            )
            st.caption(str(error))
            st.stop()
        analysis_utc_dt = local_datetime_to_utc(
            datetime.combine(analysis_date, time(12, 0)),
            tz_name,
            policy="shift_forward",
        )

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
        birth_details = {
            "date": str(birth_date),
            "time": str(birth_time),
            "city": selected_city or birth_place_label,
            "state": selected_state,
            "birth_place": birth_place_label,
            "latitude": latitude,
            "longitude": longitude,
            "utc_datetime": str(utc_dt),
            "time_precision": time_precision,
            "analysis_date": str(analysis_date),
            "analysis_datetime_utc": str(analysis_utc_dt),
            "timezone": tz_name,
            "local_time_policy": local_time_policy,
        }
        st.session_state["latest_model_payload"] = model_payload
        st.session_state["latest_client_name"] = name
        st.session_state["latest_birth_details"] = birth_details

        saved_summary = build_plain_language_report(
            model_payload,
            report_language,
        )
        saved_markdown = render_plain_language_markdown(saved_summary)
        try:
            save_session(
                name,
                birth_details,
                model_payload,
                saved_markdown,
            )
            st.session_state["latest_save_status"] = "saved"
        except SecureStorageConfigurationError as error:
            st.session_state["latest_save_status"] = str(error)

    st.success("Chart calculated successfully")


if "latest_model_payload" in st.session_state:
    model_payload = st.session_state["latest_model_payload"]
    report = model_payload["report"]
    consultation_brief = model_payload["consultation_brief"]
    summary = build_plain_language_report(
        model_payload,
        report_language,
    )
    summary_markdown = render_plain_language_markdown(summary)
    labels = summary["labels"]

    st.divider()
    st.header(summary["title"])
    st.caption(summary["subtitle"])

    st.subheader(labels["overview"])
    st.info(summary["overview"])

    st.subheader(labels["current_phase"])
    with st.container(border=True):
        st.markdown(f"**{summary['current_phase']['title']}**")
        st.write(summary["current_phase"]["summary"])
        st.caption(summary["current_phase"]["dates"])

    st.subheader(labels["priority_areas"])
    for area in summary["priority_areas"]:
        with st.container(border=True):
            st.markdown(f"#### {area['title']}")
            st.markdown(f"**{area['status']}**")
            st.write(area["summary"])
            st.markdown(f"**{labels['focus']}:** {area['focus']}")
            st.caption(f"{labels['attention']}: {area['attention']}")

    col_strengths, col_care = st.columns(2)
    with col_strengths:
        st.subheader(labels["strengths"])
        for item in summary["strengths"]:
            st.markdown(f"- {item}")
    with col_care:
        st.subheader(labels["care"])
        for item in summary["care"]:
            st.markdown(f"- {item}")

    st.subheader(labels["reliability"])
    with st.container(border=True):
        st.markdown(f"**{summary['reliability']['level']}**")
        st.write(summary["reliability"]["text"])

    st.warning(summary["disclaimer"])
    st.download_button(
        labels["download"],
        summary_markdown,
        file_name=f"serenova-summary-{report_language}.md",
        mime="text/markdown",
        icon=":material/download:",
    )

    save_status = st.session_state.get("latest_save_status")
    if save_status == "saved":
        st.caption("Session saved securely")
    elif save_status:
        st.warning(f"Session was not saved: {save_status}")

    with st.expander(labels["technical"]):
        st.subheader("Consultant Brief")
        st.json(consultation_brief)

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

        st.subheader("Rashi Drishti")
        st.json(report["rashi_drishti"])

        st.subheader("Functional Planetary Roles")
        st.json(report["functional_roles"])

        st.subheader("Dispositor Analysis")
        st.json(report["dispositor_analysis"])

        st.subheader("Transits for Analysis Date")
        st.json(report["transits"])

        st.subheader("Extended Divisional Charts")
        st.json(report["extended_divisional_charts"])

        st.subheader("Birth-Time Sensitivity")
        st.json(report["birth_time_sensitivity"])

        st.subheader("Planetary Strength Components")
        st.json(report["planetary_strength"])

        st.subheader("Sources and Validation Status")
        st.json(report["provenance"])

st.divider()
st.subheader("📁 Past Sessions")

sessions = list_sessions()

if sessions:
    session_labels = [
        f"{s['timestamp'][:16].replace('T', ' ')} — "
        f"{s['client_name'] or s.get('client_reference', 'Unnamed')}"
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

    st.markdown("### Consultant Feedback")
    feedback_rating = st.selectbox(
        "Usefulness",
        ["useful", "mixed", "not_useful"],
    )
    feedback_tags = st.multiselect(
        "Tags",
        [
            "accurate_calculation",
            "useful_question",
            "too_generic",
            "false_positive",
            "missing_context",
            "overstated",
            "timing_mismatch",
        ],
    )
    feedback_note = st.text_area(
        "Optional note",
        help=(
            "Notes are not stored unless SERENOVA_STORE_FEEDBACK_NOTES=true. "
            "Avoid client-identifying information."
        ),
    )
    if st.button("Save Feedback"):
        save_feedback(
            sessions[selected_idx]["filename"],
            feedback_rating,
            feedback_tags,
            feedback_note,
        )
        st.success("Feedback saved")
else:
    st.caption("No past sessions saved yet.")
