"""VoyageFlow AI: Streamlit interface for the travel-planning LangGraph."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import streamlit as st
from langchain_core.messages import HumanMessage

from main import app


st.set_page_config(
    page_title="VoyageFlow AI | Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# This HTML/CSS is authored by the application; untrusted model responses
# are always passed separately to Streamlit's Markdown renderer.
st.markdown(
    """
    <style>
      :root { color-scheme: dark; }
      .stApp, [data-testid="stAppViewContainer"] {
        background: #0b1220;
        color: #eaf1fc;
      }
      [data-testid="stHeader"] { background: #0b1220; }
      [data-testid="stToolbar"] { background: transparent; }
      .block-container {
        max-width: 1060px;
        padding-top: 1.25rem !important;
        padding-bottom: 2rem !important;
      }
      [data-testid="stSidebar"] { background: #101c2e; }
      [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .65rem; }
      [data-testid="stSidebar"] h1,
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] h3,
      [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] label { color: #eaf1fc !important; }
      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #adc1d9 !important;
      }
      [data-testid="stSidebar"] [data-testid="stAlert"] {
        background: #1c344a !important;
        border: 1px solid #3b6076 !important;
      }
      [data-testid="stSidebar"] [data-testid="stAlert"] * {
        color: #eaf3fc !important;
      }
      .vf-hero {
        border: 1px solid #294563;
        border-radius: 15px;
        background: linear-gradient(110deg, #152943, #123b47);
        padding: 1.45rem 1.65rem;
        margin-bottom: .8rem;
      }
      .vf-eyebrow { font-size: .74rem; letter-spacing: .12em;
        text-transform: uppercase; color: #9dd7ef; font-weight: 700; }
      .vf-hero h1 { color: #fff !important; font-size: 2rem;
        line-height: 1.17; margin: .32rem 0 .45rem; padding: 0; }
      .vf-hero p { color: #d4e5f1 !important; font-size: .95rem;
        line-height: 1.55; margin: 0; max-width: 710px; }
      .vf-note { color: #a9bdd5; font-size: .79rem; margin-top: .75rem; }
      div[data-testid="stButton"] > button,
      div[data-testid="stDownloadButton"] > button {
        background: #1b2c42 !important;
        border: 1px solid #3b5570 !important;
        color: #f2f7ff !important;
        border-radius: 9px !important;
        min-height: 2.65rem;
        font-weight: 600;
      }
      div[data-testid="stButton"] > button *,
      div[data-testid="stDownloadButton"] > button * {
        color: #f2f7ff !important;
      }
      div[data-testid="stButton"] > button:hover,
      div[data-testid="stDownloadButton"] > button:hover {
        background: #29405e !important;
        border-color: #75b9f5 !important;
      }
      div[data-testid="stButton"] > button[kind="primary"] {
        background: #236ab5 !important;
        border-color: #3484da !important;
        color: #fff !important;
      }
      div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: #2d7ccc !important;
      }
      [data-testid="stTextArea"] textarea,
      [data-testid="stTextInput"] input {
        background: #142238 !important;
        color: #f2f7ff !important;
        border: 1px solid #3c5572 !important;
        border-radius: 9px !important;
      }
      [data-testid="stTextArea"] textarea::placeholder {
        color: #a5b7ca !important;
        opacity: 1;
      }
      [data-testid="stTextInput"] input:disabled {
        color: #d0deef !important;
        -webkit-text-fill-color: #d0deef !important;
      }
      [data-testid="stMetric"] {
        background: #142238; border: 1px solid #2d4562;
        border-radius: 10px; padding: .65rem .9rem;
      }
      [data-testid="stMetric"] * { color: #edf5ff !important; }
      [data-testid="stTabs"] button { color: #c6d9ec !important; }
      [data-testid="stTabs"] button[aria-selected="true"] { color: #8ccafa !important; }
      [data-testid="stStatusWidget"], [data-testid="stAlert"] {
        border-radius: 10px;
      }
      @media (max-width: 700px) {
        .block-container { padding-top: .75rem !important; }
        .vf-hero { padding: 1.1rem; }
        .vf-hero h1 { font-size: 1.65rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

AGENT_LABELS = {
    "flight_agent": "✈️ Flight information",
    "hotel_agent": "🏨 Hotel research",
    "itinerary_agent": "🗓️ Itinerary",
    "final_agent": "🤖 Final response",
}
EXAMPLES = {
    "Tokyo": "Plan 7 days in Tokyo with hotels, attractions and a realistic budget.",
    "Paris": "Plan 5 days in Paris departing from Helsinki, with hotels and sightseeing.",
    "Rome": "Plan 4 days in Rome with hotels, food and historic attractions.",
    "Bangkok": "Plan 6 days in Bangkok with hotels, food and sightseeing.",
}


def new_thread_id() -> str:
    return f"travel-{uuid4().hex}"


def export_markdown(query: str, thread_id: str, results: dict[str, str]) -> str:
    sections = [
        ("Flight information", "flight_results"),
        ("Hotel research", "hotel_results"),
        ("Itinerary", "itinerary"),
        ("Final travel plan", "final_response"),
    ]
    content = [
        "# VoyageFlow AI — Travel Plan",
        f"**Request:** {query}",
        f"**Generated:** {datetime.now().astimezone():%Y-%m-%d %H:%M %Z}",
        f"**Session:** {thread_id}",
    ]
    for title, key in sections:
        content.append(f"## {title}\n\n{results.get(key) or 'No data available.'}")
    content.append(
        "*For travel research only. Verify fares, schedules and availability "
        "with providers before booking.*"
    )
    return "\n\n".join(content) + "\n"


if "thread_id" not in st.session_state:
    st.session_state.thread_id = new_thread_id()
if "trip_query" not in st.session_state:
    st.session_state.trip_query = ""
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None

with st.sidebar:
    st.markdown("### ✈️ VoyageFlow AI")
    st.caption("Multi-agent travel research")
    st.divider()
    st.markdown("**Current session**")
    st.text_input(
        "Session ID",
        value=st.session_state.thread_id,
        disabled=True,
        help="Identifies the LangGraph conversation stored in PostgreSQL.",
    )
    if st.button("New session", use_container_width=True):
        st.session_state.thread_id = new_thread_id()
        st.session_state.trip_query = ""
        st.session_state.last_plan = None
        st.rerun()
    st.divider()
    st.markdown("**How it works**")
    st.caption("① Flight information → ② Hotel research → ③ Itinerary → ④ Final plan")
    st.divider()
    st.caption("LangGraph · Groq · Tavily · Aviationstack · PostgreSQL")
    st.caption("Research and planning only. No bookings are made.")

st.markdown(
    """
    <div class="vf-hero">
      <div class="vf-eyebrow">Your AI travel research assistant</div>
      <h1>✈️ VoyageFlow AI</h1>
      <p>Explore flight information, research hotels and build a personalized
      itinerary with four coordinated AI agents.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("**Popular trip ideas**")
cols = st.columns(4, gap="small")
for col, (destination, query) in zip(cols, EXAMPLES.items()):
    with col:
        if st.button(destination, key=f"example_{destination}", use_container_width=True):
            st.session_state.trip_query = query

st.markdown("**Describe your trip**")
st.text_area(
    "Travel request",
    key="trip_query",
    label_visibility="collapsed",
    placeholder="Example: Plan a 5-day trip to Paris in April from Helsinki, including hotels and a daily itinerary.",
    height=110,
)

submitted = st.button("Generate travel plan", type="primary", use_container_width=True)
st.caption("Results are AI-assisted research, not verified prices or reservations.")

if submitted:
    query = st.session_state.trip_query.strip()
    if not query:
        st.warning("Enter a destination or describe your travel plans first.")
    else:
        st.session_state.last_plan = None
        results = {"flight_results": "", "hotel_results": "", "itinerary": "", "final_response": ""}
        steps_completed = 0
        st.markdown("### Agent progress")
        status = st.status("Researching your trip…", expanded=True)
        try:
            with status:
                for chunk in app.stream(
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
                ):
                    for node, update in chunk.items():
                        if not isinstance(update, dict):
                            continue
                        steps_completed += 1
                        st.write(f"✓ {AGENT_LABELS.get(node, node)}")
                        if node == "flight_agent":
                            results["flight_results"] = update.get("flight_results") or ""
                        elif node == "hotel_agent":
                            results["hotel_results"] = update.get("hotel_results") or ""
                        elif node == "itinerary_agent":
                            results["itinerary"] = update.get("itinerary") or ""
                        elif node == "final_agent":
                            messages = update.get("messages") or []
                            if messages:
                                results["final_response"] = str(messages[-1].content)
                if not results["final_response"]:
                    raise RuntimeError("Workflow returned no final response")
                status.update(label="Travel plan ready", state="complete", expanded=False)
            st.session_state.last_plan = {
                "query": query,
                "thread_id": st.session_state.thread_id,
                "results": results,
                "steps_completed": steps_completed,
            }
        except Exception:
            status.update(label="Unable to complete plan", state="error", expanded=False)
            st.error("Travel research failed. Review the server terminal for details and try again.")

plan = st.session_state.last_plan
if plan:
    results = plan["results"]
    st.markdown("### Your travel plan")
    m1, m2 = st.columns(2)
    m1.metric("Agent steps completed", plan["steps_completed"])
    m2.metric("Status", "Complete")

    flight_tab, hotel_tab, itinerary_tab, final_tab = st.tabs(
        ["✈️ Flights", "🏨 Hotels", "🗓️ Itinerary", "✨ Final plan"]
    )
    with flight_tab:
        st.markdown(results["flight_results"] or "_No flight information returned._")
        st.caption("Flight information is not a ticket quote or confirmed availability.")
    with hotel_tab:
        st.markdown(results["hotel_results"] or "_No hotel information returned._")
    with itinerary_tab:
        st.markdown(results["itinerary"] or "_No itinerary generated._")
    with final_tab:
        with st.container(border=True):
            st.markdown(results["final_response"], unsafe_allow_html=False)

    st.download_button(
        "Download plan (.md)",
        data=export_markdown(plan["query"], plan["thread_id"], results),
        file_name=f"voyageflow_plan_{datetime.now():%Y%m%d}.md",
        mime="text/markdown",
        use_container_width=True,
    )
