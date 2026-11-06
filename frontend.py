"""VoyageFlow AI — Streamlit travel planning frontend."""
from __future__ import annotations

from datetime import datetime
from html import escape
from uuid import uuid4

import streamlit as st
from langchain_core.messages import HumanMessage

from main import app

st.set_page_config(
    page_title="VoyageFlow AI · Intelligent Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Only static, developer-authored HTML is passed using unsafe_allow_html=True.
# Never interpolate AI responses or user input into the HTML templates.
ICONS = {
    "plane": '<path d="M17.8 21.2 15 12l6.5-6.5a2.1 2.1 0 0 0-3-3L12 9 2.8 6.2l-2 2 7.4 5.1-4.1 4.1-2.9-.4-1.2 1.2 4.7 2.1 2.1 4.7 1.2-1.2-.4-2.9 4.1-4.1 5.1 7.4z"/>',
    "hotel": '<path d="M4 21V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v16M2 21h20M9 21v-5h6v5M8 7h2M14 7h2M8 11h2M14 11h2"/>',
    "map": '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6ZM9 3v15M15 6v15"/>',
    "sparkle": '<path d="m12 3 1.9 6.1L20 11l-6.1 1.9L12 19l-1.9-6.1L4 11l6.1-1.9L12 3ZM19 17l.7 1.3L21 19l-1.3.7L19 21l-.7-1.3L17 19l1.3-.7L19 17Z"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m15.7 8.3-2.3 5.1-5.1 2.3 2.3-5.1 5.1-2.3Z"/>',
    "camera": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
    "palm": '<path d="M13 8c0-2.76-2.24-5-5-5s-5 2.24-5 5c0 1.64.81 3.09 2.05 4H4v2h4v5h2v-5h4v-2h-2.05C12.19 11.09 13 9.64 13 8z"/><path d="M18 10a4 4 0 0 0-4-4v2a2 2 0 0 1 2 2h2z"/><path d="M21 14a7 7 0 0 0-7-7v2a5 5 0 0 1 5 5h2z"/>',
}


def icon(name: str, size: int = 20) -> str:
    """Return an application-authored SVG icon, independent of system fonts."""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'{ICONS.get(name, ICONS["sparkle"])}</svg>'
    )


st.markdown(
    """
<style>
/* Clean, professional dark palette */
:root {
    --bg: #131b24;
    --surface: #1c2733;
    --surface-hover: #263545;
    --stroke: rgba(255, 255, 255, 0.12);
    --fg: #f8fafc;
    --muted: #94a3b8;
    --accent: #fbbf24;
    --accent-hover: #f59e0b;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--fg) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

[data-testid="stHeader"] { 
    background: transparent !important; 
}
[data-testid="stToolbar"] { background: transparent !important; }

/* Fix Sidebar Collapse Button visibility (makes the collapse arrow bright & clearly visible) */
[data-testid="stSidebarCollapseButton"] svg {
    fill: var(--accent) !important;
    color: var(--accent) !important;
}
button[kind="header"] svg, [data-testid="stSidebarCollapsedControl"] svg {
    color: var(--fg) !important;
    fill: var(--fg) !important;
}

.block-container { 
    max-width: 1180px !important; 
    padding-top: 2rem !important; 
    padding-bottom: 3rem !important; 
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #10171f !important;
    border-right: 1px solid var(--stroke) !important;
}
[data-testid="stSidebar"] > div:first-child { 
    padding-top: 2.5rem !important; 
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--fg) !important; }
[data-testid="stSidebar"] hr { border-color: var(--stroke) !important; margin: 1.2rem 0 !important; }

/* Brand & Sidebar Components */
.vf-brand {
    display: flex;
    gap: 0.85rem;
    align-items: center;
    margin-bottom: 0.35rem;
}
.vf-brand-mark {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: rgba(251, 191, 36, 0.15);
    color: var(--accent);
    border: 1px solid rgba(251, 191, 36, 0.3);
}
.vf-brand-name {
    font-weight: 700;
    font-size: 1.2rem;
    color: #ffffff;
}
.vf-brand-sub {
    font-size: 0.78rem;
    color: var(--muted);
}
.vf-side-heading {
    font-weight: 700;
    font-size: 0.82rem;
    color: #cbd5e1;
    margin: 0.2rem 0 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.vf-step {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.5rem 0.6rem;
    color: #e2e8f0;
    font-size: 0.88rem;
    border-radius: 8px;
}
.vf-step-icon {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    color: var(--accent);
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.2);
}
.vf-tech-badge {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--stroke);
    padding: 0.75rem;
    border-radius: 10px;
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.5;
    margin-top: 0.75rem;
}

/* Hero Section */
.vf-hero {
    border: 1px solid var(--stroke);
    border-radius: 18px;
    padding: 2.2rem 2.5rem;
    margin: 0 0 1.75rem;
    background: var(--surface);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}
.vf-overline {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--accent);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-size: 0.75rem;
    font-weight: 700;
    margin-bottom: 0.7rem;
}
.vf-title {
    color: #ffffff;
    font-size: clamp(2rem, 3.5vw, 2.8rem);
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 0.6rem;
}
.vf-description {
    font-size: 1rem;
    line-height: 1.6;
    color: var(--muted);
    max-width: 680px;
    margin: 0;
}
.vf-label {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-weight: 700;
    color: var(--fg);
    font-size: 1.05rem;
    margin: 0.5rem 0 0.75rem;
}
.vf-label svg { color: var(--accent); }
.vf-help {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.65rem;
}
.vf-rule {
    height: 1px;
    background: var(--stroke);
    margin: 1.5rem 0;
}

/* Destination Tile Buttons with Icons */
.vf-dest-note { color: var(--muted); font-size: 0.85rem; margin: -0.2rem 0 0.85rem; }

div[class*="st-key-destination_"] button {
    background: var(--surface) !important;
    border: 1px solid var(--stroke) !important;
    min-height: 4.8rem !important;
    padding: 0.9rem 1.1rem !important;
    border-radius: 12px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
}
div[class*="st-key-destination_"] button:hover {
    background: var(--surface-hover) !important;
    border-color: var(--accent) !important;
    transform: translateY(-2px);
}
div[class*="st-key-destination_"] button p {
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: var(--fg) !important;
}

/* Form controls & Buttons */
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {
    background: var(--surface) !important;
    color: var(--fg) !important;
    border: 1px solid var(--stroke) !important;
    border-radius: 10px !important;
    min-height: 2.8rem !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
    background: var(--surface-hover) !important;
    border-color: var(--accent) !important;
}
[data-testid="stButton"] button[kind="primary"] {
    color: #111827 !important;
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    font-weight: 750 !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
}
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    background: #0d131a !important;
    color: var(--fg) !important;
    border: 1px solid var(--stroke) !important;
    border-radius: 10px !important;
}
[data-testid="stTextArea"] textarea { min-height: 110px !important; }
[data-testid="stTextArea"] textarea:focus, [data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.2) !important;
}

/* Enhanced Tabs & Results Styling */
[data-testid="stTabs"] [role="tablist"] { gap: 0.4rem; border-bottom: 1px solid var(--stroke) !important; }
[data-testid="stTabs"] [role="tab"] {
    color: var(--muted) !important;
    font-weight: 650 !important;
    padding: 0.7rem 1.2rem !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: #fff !important; background: rgba(255, 255, 255, 0.05) !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    background: var(--surface) !important;
    border-bottom: 3px solid var(--accent) !important;
}
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--stroke);
    border-radius: 12px;
    padding: 0.75rem 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

DESTINATIONS = (
    ("Tokyo", "Japan", "🇯🇵", "Plan 7 days in Tokyo with hotels, attractions and a realistic budget."),
    ("Paris", "France", "🇫🇷", "Plan 5 days in Paris departing from Helsinki, with hotels and sightseeing."),
    ("Rome", "Italy", "🇮🇹", "Plan 4 days in Rome with hotels, food and historic attractions."),
    ("Bangkok", "Thailand", "🇹🇭", "Plan 6 days in Bangkok with hotels, food and sightseeing."),
)
AGENTS = {
    "flight_agent": ("Flight information", "flight_results"),
    "hotel_agent": ("Hotel research", "hotel_results"),
    "itinerary_agent": ("Itinerary", "itinerary"),
    "final_agent": ("Final response", "final_response"),
}


def new_thread_id() -> str:
    return f"travel-{uuid4().hex[:12]}"


def export_markdown(query: str, thread_id: str, results: dict[str, str]) -> str:
    parts = [
        "# VoyageFlow AI — Travel Plan",
        f"**Request:** {query}",
        f"**Generated:** {datetime.now().astimezone():%Y-%m-%d %H:%M %Z}",
        f"**Session:** {thread_id}",
    ]
    for label, key in (
        ("Flight information", "flight_results"),
        ("Hotel research", "hotel_results"),
        ("Itinerary", "itinerary"),
        ("Final travel plan", "final_response"),
    ):
        parts.append(f"## {label}\n\n{results.get(key) or 'No data available.'}")
    parts.append("*Research only. Confirm pricing, schedules and availability before booking.*")
    return "\n\n".join(parts) + "\n"


if "thread_id" not in st.session_state:
    st.session_state.thread_id = new_thread_id()
if "trip_query" not in st.session_state:
    st.session_state.trip_query = ""
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None

with st.sidebar:
    st.markdown(
        '<div class="vf-brand"><span class="vf-brand-mark">'
        + icon("compass", 22)
        + '</span><div><div class="vf-brand-name">VoyageFlow AI</div>'
        '<div class="vf-brand-sub">Intelligent travel research</div></div></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown('<div class="vf-side-heading">Your Session</div>', unsafe_allow_html=True)
    st.text_input(
        "Session ID",
        value=st.session_state.thread_id,
        disabled=True,
        help="LangGraph checkpoint session thread ID.",
    )
    if st.button("Start a new trip", use_container_width=True):
        st.session_state.thread_id = new_thread_id()
        st.session_state.trip_query = ""
        st.session_state.last_plan = None
        st.rerun()
    st.divider()
    st.markdown('<div class="vf-side-heading">Workflow Agents</div>', unsafe_allow_html=True)
    steps = [
        ("plane", "Flight research"),
        ("hotel", "Hotel discovery"),
        ("map", "Day-by-day itinerary"),
        ("sparkle", "Final travel plan"),
    ]
    st.markdown(
        "".join(
            f'<div class="vf-step"><span class="vf-step-icon">{icon(kind, 16)}</span>'
            f'<span>{escape(label)}</span></div>'
            for kind, label in steps
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="vf-tech-badge">⚡ Powered by LangGraph, Groq, Tavily, Aviationstack & PostgreSQL.<br><br>🔒 Secure & private session data.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<section class="vf-hero">'
    f'<div class="vf-overline">{icon("palm", 15)} Adventure Awaits · Travel Planned Beautifully</div>'
    '<h1 class="vf-title">The world is waiting.</h1>'
    '<p class="vf-description">Meet <strong>VoyageFlow AI</strong> — your intelligent travel research companion powered by coordinated AI agents.</p>'
    '</section>',
    unsafe_allow_html=True,
)

st.markdown(f'<div class="vf-label">{icon("camera", 18)} Explore Popular Destinations</div>', unsafe_allow_html=True)
st.markdown('<div class="vf-dest-note">Click any destination card below to quickly load a starting request</div>', unsafe_allow_html=True)
cols = st.columns(4, gap="small")
for col, (city, country, flag_icon, query) in zip(cols, DESTINATIONS):
    with col:
        if st.button(
            f"{flag_icon}  {city}  ·  {country}",
            key=f"destination_{city.lower()}",
            use_container_width=True,
        ):
            st.session_state.trip_query = query

st.markdown('<div class="vf-rule"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="vf-label">{icon("map", 18)} Tell us about your trip</div>', unsafe_allow_html=True)
st.text_area(
    "Travel request",
    key="trip_query",
    label_visibility="collapsed",
    placeholder="Where would you like to go? Add dates, departure city, travelers and budget…",
    height=110,
)
submitted = st.button("Create my travel plan", type="primary", use_container_width=True)
st.markdown(
    '<div class="vf-help">💡 Tip: Be specific with your dates, departure location, and preferences for the best results.</div>',
    unsafe_allow_html=True,
)

if submitted:
    query = st.session_state.trip_query.strip()
    if not query:
        st.warning("Please enter or select where you want to go before generating a plan.")
    else:
        st.session_state.last_plan = None
        results = {"flight_results": "", "hotel_results": "", "itinerary": "", "final_response": ""}
        completed = 0
        st.markdown(f'<div class="vf-label">{icon("sparkle", 18)} Research in progress</div>', unsafe_allow_html=True)
        
        status = st.status("🚀 Coordinating your four AI agents (Flights, Hotels, Itinerary, Final Plan)...", expanded=True)
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
                        if node not in AGENTS:
                            continue
                        completed += 1
                        label, result_key = AGENTS[node]
                        st.write(f"✓ {label} completed successfully")
                        if node == "final_agent":
                            messages = update.get("messages") or []
                            if messages:
                                results[result_key] = str(messages[-1].content)
                        else:
                            results[result_key] = str(update.get(result_key) or "")
                if not results["final_response"]:
                    raise RuntimeError("Workflow returned no final response")
                status.update(label="✨ Your travel plan is fully ready!", state="complete", expanded=False)
            st.session_state.last_plan = {
                "query": query,
                "thread_id": st.session_state.thread_id,
                "results": results,
                "steps_completed": completed,
            }
        except Exception as e:
            status.update(label="⚠️ Unable to complete the plan", state="error", expanded=False)
            st.error(f"Travel research couldn't finish: {e}")

plan = st.session_state.last_plan
if plan:
    results = plan["results"]
    st.markdown('<div class="vf-rule"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="vf-label">{icon("sparkle", 18)} Your completed travel plan</div>', unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    m1.metric("Agent steps completed", plan["steps_completed"])
    m2.metric("Workflow status", "Ready & Verified")
    
    tab_flights, tab_hotels, tab_itinerary, tab_final = st.tabs(
        ["✈️ Flights", "🏨 Hotels", "🗺️ Itinerary", "✨ Final Plan"]
    )
    with tab_flights:
        with st.container(border=True):
            st.markdown(results["flight_results"] or "_No flight information returned._", unsafe_allow_html=False)
        st.caption("Flight status info is for reference only.")
    with tab_hotels:
        with st.container(border=True):
            st.markdown(results["hotel_results"] or "_No hotel information returned._", unsafe_allow_html=False)
    with tab_itinerary:
        with st.container(border=True):
            st.markdown(results["itinerary"] or "_No itinerary generated._", unsafe_allow_html=False)
    with tab_final:
        with st.container(border=True):
            st.markdown(results["final_response"] or "_No final response generated._", unsafe_allow_html=False)
            
    st.download_button(
        "📥 Download full travel plan (.md)",
        data=export_markdown(plan["query"], plan["thread_id"], results),
        file_name=f"voyageflow_plan_{datetime.now():%Y%m%d}.md",
        mime="text/markdown",
        use_container_width=True,
    )
    