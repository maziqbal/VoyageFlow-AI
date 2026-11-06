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
    "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
}


def icon(name: str, size: int = 20) -> str:
    """Return an application-authored SVG icon, independent of system fonts."""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'{ICONS[name]}</svg>'
    )


st.markdown(
    """
<style>
/* Palette: warm charcoal, translucent slate, subtle champagne accent. */
:root { --bg:#0b1015; --surface:rgba(27,37,44,.66); --stroke:rgba(213,229,226,.13);
        --fg:#f4f6f2; --muted:#b3c0bd; --accent:#eccb91; --accent-dark:#242014; }
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: radial-gradient(ellipse 80% 60% at 84% 3%,rgba(89,122,113,.18),transparent 65%),
              radial-gradient(ellipse 48% 45% at 18% 85%,rgba(139,108,77,.09),transparent 70%),
              var(--bg) !important;
  color:var(--fg) !important;
}
[data-testid="stHeader"] { background:transparent !important; }
[data-testid="stToolbar"] { background:transparent !important; }
.block-container { max-width: 1150px !important; padding-top:2.75rem !important; padding-bottom:2.5rem !important; }
/* Sidebar: narrow, readable, independent of content height. */
[data-testid="stSidebar"] {background:rgba(17,25,30,.92) !important; border-right:1px solid var(--stroke);}
[data-testid="stSidebar"] > div:first-child {padding-top:1.75rem;}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.45rem !important;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:var(--muted) !important;}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {color:var(--fg) !important;}
[data-testid="stSidebar"] hr {border-color:var(--stroke) !important; margin:1.15rem 0 !important;}
.vf-brand {display:flex;gap:.75rem;align-items:center;margin-bottom:.35rem;}
.vf-brand-mark {width:40px;height:40px;display:grid;place-items:center;border-radius:13px;
 background:rgba(236,203,145,.12);color:var(--accent);border:1px solid rgba(236,203,145,.25);}
.vf-brand-name {font-weight:750;font-size:1.15rem;letter-spacing:-.025em;color:#fff;}
.vf-brand-sub {font-size:.78rem;color:var(--muted);margin-top:1px;}
.vf-side-heading {font-weight:700;font-size:.85rem;color:#e9efe9;margin:.15rem 0 .6rem;letter-spacing:.01em;}
.vf-step {display:flex;align-items:center;gap:.75rem;padding:.45rem .2rem;color:#cbd6d2;font-size:.88rem;}
.vf-step-icon {width:32px;height:32px;border-radius:10px;display:grid;place-items:center;
 color:var(--accent);background:rgba(236,203,145,.08);border:1px solid rgba(236,203,145,.12);}
.vf-fine {color:#9daea8;font-size:.77rem;line-height:1.65;margin-top:.8rem;}
/* Hero: a real glass card, no large empty artwork block. */
.vf-hero {position:relative;overflow:hidden;border:1px solid rgba(226,236,230,.17);
 border-radius:22px;padding:2rem 2.25rem 1.85rem;margin:0 0 1.55rem;
 background:linear-gradient(115deg,rgba(39,54,57,.8),rgba(28,43,46,.62) 58%,rgba(79,75,57,.25));
 box-shadow:0 14px 42px rgba(0,0,0,.15),inset 0 1px rgba(255,255,255,.07);
 backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);}
.vf-hero:after {content:"";position:absolute;width:260px;height:260px;right:-105px;top:-115px;
 background:radial-gradient(circle,rgba(236,203,145,.11),transparent 70%);pointer-events:none;}
.vf-overline {display:flex;align-items:center;gap:.45rem;color:var(--accent);
 letter-spacing:.14em;text-transform:uppercase;font-size:.7rem;font-weight:750;margin-bottom:.7rem;}
.vf-title {color:#fafbf7;font-size:clamp(2rem,3.5vw,2.8rem);font-weight:750;
 letter-spacing:-.055em;line-height:1.13;margin:0 0 .65rem;}
.vf-description {font-size:.99rem;line-height:1.65;color:#d0ddd9;max-width:660px;margin:0;}
.vf-label {display:flex;align-items:center;gap:.55rem;font-weight:700;color:#f0f3ee;
 font-size:.96rem;margin:.3rem 0 .72rem;}
.vf-label svg {color:var(--accent);}
.vf-help {font-size:.8rem;color:var(--muted);margin-top:.6rem;line-height:1.5;}
.vf-rule {height:1px;background:linear-gradient(90deg,var(--stroke),transparent);margin:1.25rem 0;}
/* Destination tiles: concise travel cards, not generic full-width buttons. */
.vf-dest-heading {display:flex;align-items:baseline;gap:.55rem;margin-bottom:.2rem;}
.vf-dest-note {color:var(--muted);font-size:.79rem;margin:-.2rem 0 .7rem;}
div[class*="st-key-destination_"] button {
  background:linear-gradient(135deg,rgba(39,51,53,.92),rgba(25,36,40,.78)) !important;
  border:1px solid rgba(226,216,186,.20) !important;
  min-height:4.25rem !important;
  padding:.85rem 1rem !important;
  border-radius:15px !important;
  justify-content:flex-start !important;
  text-align:left !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.045),0 5px 18px rgba(0,0,0,.10) !important;
}
div[class*="st-key-destination_"] button:before {
  content:"↗";display:inline-flex;align-items:center;justify-content:center;
  flex:0 0 29px;width:29px;height:29px;margin-right:.65rem;
  color:#eccb91;border:1px solid rgba(236,203,145,.25);
  background:rgba(236,203,145,.09);border-radius:9px;font-size:1rem;
}
div[class*="st-key-destination_"] button:hover {
  transform:translateY(-2px);
  background:linear-gradient(135deg,rgba(58,70,66,.94),rgba(34,48,48,.92)) !important;
  border-color:rgba(236,203,145,.62) !important;
}
div[class*="st-key-destination_"] button p {font-size:.89rem !important;letter-spacing:.005em !important;}
/* Native controls — scope selectors to these controls only. */
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {
 background:rgba(38,51,58,.72) !important;color:#f5f5f1 !important;
 border:1px solid rgba(218,231,225,.20) !important;border-radius:12px !important;
 min-height:2.85rem !important;font-weight:600 !important;box-shadow:none !important;
 transition:background .14s ease,border-color .14s ease !important;
}
[data-testid="stButton"] button *,[data-testid="stDownloadButton"] button * {color:inherit !important;}
[data-testid="stButton"] button:hover,[data-testid="stDownloadButton"] button:hover {
 background:rgba(57,75,79,.86) !important;border-color:rgba(236,203,145,.55) !important;
}
[data-testid="stButton"] button[kind="primary"] {
 color:var(--accent-dark) !important;background:var(--accent) !important;
 border-color:var(--accent) !important;font-weight:750 !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {background:#f4dab0 !important;border-color:#f4dab0 !important;}
[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input {
 background:rgba(21,31,37,.75) !important;color:#f1f5f2 !important;
 border:1px solid rgba(215,231,224,.22) !important;border-radius:12px !important;
 box-shadow:none !important;
}
[data-testid="stTextArea"] textarea {min-height:115px !important;}
[data-testid="stTextArea"] textarea::placeholder {color:#a4b6ae !important;opacity:1 !important;}
[data-testid="stTextArea"] textarea:focus,[data-testid="stTextInput"] input:focus {
 border-color:rgba(236,203,145,.75) !important;box-shadow:0 0 0 1px rgba(236,203,145,.2) !important;}
[data-testid="stTextInput"] input:disabled {color:#cbd6d2 !important;-webkit-text-fill-color:#cbd6d2 !important;}
[data-testid="stCaptionContainer"] p {color:var(--muted) !important;}
/* Results and tabs: transparent glass, visible states. */
[data-testid="stTabs"] [role="tablist"] {gap:.4rem; border-bottom:1px solid var(--stroke) !important;}
[data-testid="stTabs"] [role="tab"] {color:#cbd5d0 !important;font-weight:650 !important;
 padding:.65rem .9rem !important;border-radius:10px 10px 0 0 !important;}
[data-testid="stTabs"] [role="tab"] * {color:inherit !important;}
[data-testid="stTabs"] [role="tab"]:hover {color:#fff !important;background:rgba(255,255,255,.05) !important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {color:var(--accent) !important;background:rgba(236,203,145,.07) !important;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {background:var(--accent) !important;}
[data-testid="stTabs"] [data-baseweb="tab-border"] {background:var(--stroke) !important;}
[data-testid="stTabs"] [role="tabpanel"] {padding-top:1rem !important;}
[data-testid="stMetric"] {background:var(--surface);border:1px solid var(--stroke);border-radius:14px;padding:.65rem 1rem;}
[data-testid="stMetric"] * {color:var(--fg) !important;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:var(--stroke) !important;}
@media(max-width:720px) {
 .block-container {padding:1.9rem .9rem 2rem !important;}
 .vf-hero {padding:1.4rem 1.25rem;border-radius:17px;}
 .vf-title {font-size:2rem;}
 [data-testid="stTabs"] [role="tab"] {font-size:.8rem !important;padding:.55rem .5rem !important;}
}
</style>
""",
    unsafe_allow_html=True,
)

DESTINATIONS = (
    ("Tokyo", "Japan", "Plan 7 days in Tokyo with hotels, attractions and a realistic budget."),
    ("Paris", "France", "Plan 5 days in Paris departing from Helsinki, with hotels and sightseeing."),
    ("Rome", "Italy", "Plan 4 days in Rome with hotels, food and historic attractions."),
    ("Bangkok", "Thailand", "Plan 6 days in Bangkok with hotels, food and sightseeing."),
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
    st.markdown('<div class="vf-side-heading">Your session</div>', unsafe_allow_html=True)
    st.text_input(
        "Session ID",
        value=st.session_state.thread_id,
        disabled=True,
        help="LangGraph uses this ID to identify the checkpoint thread in PostgreSQL.",
    )
    if st.button("Start a new trip", use_container_width=True):
        st.session_state.thread_id = new_thread_id()
        st.session_state.trip_query = ""
        st.session_state.last_plan = None
        st.rerun()
    st.divider()
    st.markdown('<div class="vf-side-heading">Behind your travel plan</div>', unsafe_allow_html=True)
    steps = [
        ("plane", "Flight research"),
        ("hotel", "Hotel discovery"),
        ("map", "Day-by-day itinerary"),
        ("sparkle", "Final travel plan"),
    ]
    st.markdown(
        "".join(
            f'<div class="vf-step"><span class="vf-step-icon">{icon(kind, 17)}</span>'
            f'<span>{escape(label)}</span></div>'
            for kind, label in steps
        ),
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        '<div class="vf-fine">Built with LangGraph, Groq, Tavily, '
        'Aviationstack and PostgreSQL.<br><br>'
        'Travel research only. No bookings are made.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<section class="vf-hero">'
    f'<div class="vf-overline">{icon("sparkle", 15)} Travel planning, thoughtfully done</div>'
    '<h1 class="vf-title">The world is waiting.</h1>'
    '<p class="vf-description">Meet <strong>VoyageFlow AI</strong> — your travel research companion. '
    'Explore destinations, compare useful sources, and shape your journey with four coordinated AI agents.</p>'
    '</section>',
    unsafe_allow_html=True,
)

st.markdown(f'<div class="vf-label">{icon("compass", 19)} Explore a destination</div>', unsafe_allow_html=True)
st.markdown('<div class="vf-dest-note">A little inspiration to get your journey started</div>', unsafe_allow_html=True)
cols = st.columns(4, gap="small")
for col, (city, country, query) in zip(cols, DESTINATIONS):
    with col:
        if st.button(
            f"{city}  ·  {country}",
            key=f"destination_{city.lower()}",
            use_container_width=True,
        ):
            st.session_state.trip_query = query

st.markdown('<div class="vf-rule"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="vf-label">{icon("map", 19)} Tell us about your trip</div>', unsafe_allow_html=True)
st.text_area(
    "Travel request",
    key="trip_query",
    label_visibility="collapsed",
    placeholder="Where would you like to go? Add dates, departure city, travelers and budget…",
    height=115,
)
submitted = st.button("Create my travel plan", type="primary", use_container_width=True)
st.markdown(
    '<div class="vf-help">Thoughtful suggestions, not confirmed fares or bookings. '
    'Please verify availability and prices with providers.</div>',
    unsafe_allow_html=True,
)

if submitted:
    query = st.session_state.trip_query.strip()
    if not query:
        st.warning("Tell us where you want to go before generating a plan.")
    else:
        st.session_state.last_plan = None
        results = {"flight_results": "", "hotel_results": "", "itinerary": "", "final_response": ""}
        completed = 0
        st.markdown(f'<div class="vf-label">{icon("sparkle", 19)} Research in progress</div>', unsafe_allow_html=True)
        status = st.status("Coordinating your four agents…", expanded=True)
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
                        st.write(f"✓ {label} completed")
                        if node == "final_agent":
                            messages = update.get("messages") or []
                            if messages:
                                results[result_key] = str(messages[-1].content)
                        else:
                            results[result_key] = str(update.get(result_key) or "")
                if not results["final_response"]:
                    raise RuntimeError("Workflow returned no final response")
                status.update(label="Your travel plan is ready", state="complete", expanded=False)
            st.session_state.last_plan = {
                "query": query,
                "thread_id": st.session_state.thread_id,
                "results": results,
                "steps_completed": completed,
            }
        except Exception:
            status.update(label="Unable to complete the plan", state="error", expanded=False)
            st.error("Travel research couldn't finish. Check the server terminal for the error and try again.")

plan = st.session_state.last_plan
if plan:
    results = plan["results"]
    st.markdown('<div class="vf-rule"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="vf-label">{icon("sparkle", 19)} Your travel plan</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.metric("Agent steps", plan["steps_completed"])
    m2.metric("Workflow", "Complete")
    tab_flights, tab_hotels, tab_itinerary, tab_final = st.tabs(
        ["Flights", "Hotels", "Itinerary", "Final plan"]
    )
    with tab_flights:
        st.markdown(results["flight_results"] or "_No flight information returned._", unsafe_allow_html=False)
        st.caption("Flight status information does not constitute a ticket quote or booking availability.")
    with tab_hotels:
        st.markdown(results["hotel_results"] or "_No hotel information returned._", unsafe_allow_html=False)
    with tab_itinerary:
        st.markdown(results["itinerary"] or "_No itinerary generated._", unsafe_allow_html=False)
    with tab_final:
        with st.container(border=True):
            st.markdown(results["final_response"] or "_No final response generated._", unsafe_allow_html=False)
    st.download_button(
        "Download travel plan (.md)",
        data=export_markdown(plan["query"], plan["thread_id"], results),
        file_name=f"voyageflow_plan_{datetime.now():%Y%m%d}.md",
        mime="text/markdown",
        use_container_width=True,
    )
