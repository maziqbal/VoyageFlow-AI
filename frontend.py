"""VoyageFlow AI — Streamlit interface for the LangGraph travel planner."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import streamlit as st
from langchain_core.messages import HumanMessage

from main import app


st.set_page_config(
    page_title="VoyageFlow AI | Multi-Agent Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Only static, application-owned markup/CSS uses unsafe_allow_html.
# Never interpolate user input or LLM/API output into HTML.
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #081323 0%, #0d1a2c 55%, #101b30 100%);
        color: #e8effb;
    }
    .block-container {max-width: 1160px; padding-top: 2rem; padding-bottom: 3rem;}
    [data-testid="stSidebar"] {background: #0b1728;}
    [data-testid="stSidebar"] * {color: #dce8f8;}
    .vf-hero {
        background: linear-gradient(115deg, #163b63, #102a49 50%, #123b48);
        border: 1px solid #315477;
        border-radius: 22px;
        padding: 2.3rem 2.4rem;
        margin-bottom: 1.3rem;
    }
    .vf-kicker {font-size: .78rem; letter-spacing: .16em; color: #9ed7ff;
                text-transform: uppercase; font-weight: 700;}
    .vf-title {font-size: clamp(2rem, 5vw, 3.3rem); font-weight: 800;
               color: #fff; line-height: 1.15; margin: .45rem 0;}
    .vf-subtitle {color: #cfdef0; font-size: 1rem; max-width: 680px;}
    .vf-section {font-size: 1.2rem; font-weight: 700; color: #edf5ff;
                 margin: 1.2rem 0 .45rem;}
    .vf-footnote {color: #9db5ce; font-size: .84rem;}
    div[data-testid="stMetric"] {
        background: #15253d; border: 1px solid #2d4665;
        padding: .85rem 1rem; border-radius: 13px;
    }
    div[data-testid="stMetric"] * {color: #e9f3ff;}
    div.stButton > button[kind="primary"] {
        background: #2875cb; color: white; border-radius: 10px;
        border: 1px solid #4795ef; font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


AGENT_LABELS = {
    "flight_agent": "✈️ Flight research",
    "hotel_agent": "🏨 Hotel research",
    "itinerary_agent": "🗓️ Itinerary planning",
    "final_agent": "🤖 Final travel response",
}

EXAMPLE_TRIPS = {
    "🇯🇵 Tokyo": "Plan a 7-day trip to Tokyo with hotels, sights, and a realistic budget.",
    "🇫🇷 Paris": "Plan a 5-day Paris trip with hotel and sightseeing suggestions.",
    "🇮🇹 Rome": "Plan a 4-day trip to Rome including hotels and cultural attractions.",
    "🇹🇭 Bangkok": "Plan a 6-day Bangkok trip with hotels, food, and sightseeing.",
}


def fresh_thread_id() -> str:
    """Return a unique checkpoint thread ID for a new travel session."""
    return f"travel-{uuid4().hex}"


def make_markdown_plan(query: str, thread_id: str, results: dict) -> str:
    """Build the Markdown download using completed agent results."""
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    return (
        "# VoyageFlow AI — Travel Plan\n\n"
        f"**Request:** {query}\n\n"
        f"**Generated:** {generated}\n\n"
        f"**Session:** {thread_id}\n\n"
        "## Flight information\n\n"
        f"{results.get('flight_results') or 'No data available.'}\n\n"
        "## Hotel research\n\n"
        f"{results.get('hotel_results') or 'No data available.'}\n\n"
        "## Itinerary\n\n"
        f"{results.get('itinerary') or 'No itinerary generated.'}\n\n"
        "## Final recommendation\n\n"
        f"{results.get('final_response') or 'No final response generated.'}\n\n"
        "---\n\n"
        "*Information is for planning only. Verify availability, prices, and schedules "
        "with providers before making bookings.*\n"
    )


# Streamlit reruns the script on interaction, so retain UI data in session_state.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = fresh_thread_id()
if "trip_query" not in st.session_state:
    st.session_state.trip_query = ""
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None

with st.sidebar:
    st.title("✈️ VoyageFlow AI")
    st.caption("Your multi-agent travel planning companion")
    st.divider()
    st.subheader("Travel session")
    st.text_input(
        "Session ID",
        value=st.session_state.thread_id,
        disabled=True,
        help="Used by LangGraph to identify this session's PostgreSQL checkpoints.",
    )
    if st.button("＋ New travel session", use_container_width=True):
        st.session_state.thread_id = fresh_thread_id()
        st.session_state.trip_query = ""
        st.session_state.last_plan = None
        st.rerun()

    st.divider()
    st.subheader("How it works")
    for label in AGENT_LABELS.values():
        st.write(label)
    st.divider()
    st.caption("Powered by LangGraph · Groq · Tavily · Aviationstack · PostgreSQL")
    st.info("Trip suggestions are for research and planning, not confirmed bookings.")

st.markdown(
    """
    <div class="vf-hero">
        <div class="vf-kicker">Plan smarter · Explore further</div>
        <div class="vf-title">✈️ VoyageFlow AI</div>
        <div class="vf-subtitle">
            One travel request. Four specialized AI agents.
            Explore flight information, research hotels, and build a personalized itinerary.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="vf-section">🌍 Find inspiration</div>', unsafe_allow_html=True)
cols = st.columns(len(EXAMPLE_TRIPS))
for col, (destination, sample_query) in zip(cols, EXAMPLE_TRIPS.items()):
    with col:
        if st.button(destination, use_container_width=True):
            st.session_state.trip_query = sample_query

st.markdown('<div class="vf-section">🧭 Describe your trip</div>', unsafe_allow_html=True)
st.text_area(
    "Where would you like to go?",
    key="trip_query",
    placeholder=(
        "Example: Plan 5 days in Paris in April, departing from Helsinki. "
        "Include hotels and a day-by-day itinerary."
    ),
    height=125,
    label_visibility="collapsed",
)

submit = st.button("✨ Generate travel plan", type="primary", use_container_width=True)

if submit:
    query = st.session_state.trip_query.strip()
    if not query:
        st.warning("Please describe your trip before generating a plan.")
    else:
        # Do not show a previous plan as if it were the new result.
        st.session_state.last_plan = None
        results = {
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "final_response": "",
        }
        steps_completed = 0
        st.subheader("🤖 Agent activity")
        status_box = st.status("Preparing your travel plan…", expanded=True)

        try:
            with status_box:
                updates = app.stream(
                    {
                        "messages": [HumanMessage(content=query)],
                        "user_query": query,
                        "flight_results": "",
                        "hotel_results": "",
                        "itinerary": "",
                        "llm_calls": 0,
                    },
                    config={"configurable": {"thread_id": st.session_state.thread_id}},
                    stream_mode="updates",
                )
                for chunk in updates:
                    for node_name, update in chunk.items():
                        if not isinstance(update, dict):
                            continue
                        steps_completed += 1
                        label = AGENT_LABELS.get(node_name, node_name)
                        st.markdown(f"**{label}** — completed")
                        if node_name == "flight_agent":
                            results["flight_results"] = update.get("flight_results") or ""
                        elif node_name == "hotel_agent":
                            results["hotel_results"] = update.get("hotel_results") or ""
                        elif node_name == "itinerary_agent":
                            results["itinerary"] = update.get("itinerary") or ""
                        elif node_name == "final_agent":
                            messages = update.get("messages") or []
                            if messages:
                                results["final_response"] = str(messages[-1].content)

                if not results["final_response"]:
                    raise RuntimeError("The workflow finished without a final travel response.")
                status_box.update(label="Travel plan ready", state="complete", expanded=False)

            st.session_state.last_plan = {
                "query": query,
                "thread_id": st.session_state.thread_id,
                "results": results,
                "steps_completed": steps_completed,
            }
        except Exception:
            status_box.update(label="Travel planning failed", state="error", expanded=True)
            st.error(
                "The travel plan could not be completed. Check the application terminal "
                "for details and try again."
            )
            # Internal exception details are intentionally not printed to the UI.

plan = st.session_state.last_plan
if plan:
    results = plan["results"]
    st.divider()
    st.subheader("📋 Your travel plan")
    a, b, c = st.columns(3)
    a.metric("Agent steps completed", plan["steps_completed"])
    b.metric("Workflow", "Completed")
    c.metric("Session", "Saved in PostgreSQL")

    flight_tab, hotel_tab, itinerary_tab, final_tab = st.tabs(
        ["✈️ Flights", "🏨 Hotels", "🗓️ Itinerary", "🌟 Final plan"]
    )
    with flight_tab:
        st.markdown(results["flight_results"] or "_No flight information returned._")
        st.caption("Flight-status information is not the same as ticket pricing or booking availability.")
    with hotel_tab:
        st.markdown(results["hotel_results"] or "_No hotel information returned._")
        st.caption("Check prices and availability directly with the hotel or booking provider.")
    with itinerary_tab:
        st.markdown(results["itinerary"] or "_No itinerary generated._")
    with final_tab:
        with st.container(border=True):
            # Render model output as Markdown, never as interpolated raw HTML.
            st.markdown(results["final_response"], unsafe_allow_html=False)

    filename = f"voyageflow_plan_{datetime.now().strftime('%Y%m%d')}.md"
    st.download_button(
        "⬇️ Download travel plan (.md)",
        data=make_markdown_plan(plan["query"], plan["thread_id"], results),
        file_name=filename,
        mime="text/markdown",
        use_container_width=True,
    )
    st.caption("Travel plans are downloaded on demand; this UI does not automatically write local files.")

st.markdown(
    '<p class="vf-footnote">VoyageFlow AI · AI-assisted travel research, not a booking service.</p>',
    unsafe_allow_html=True,
)
