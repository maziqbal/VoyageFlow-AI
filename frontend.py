"""VoyageFlow AI — Streamlit travel planning application."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from html import escape
from urllib.parse import urlparse
from uuid import uuid4

import streamlit as st
from langchain_core.messages import HumanMessage

from main import app


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="VoyageFlow AI | Intelligent Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="locked",
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
<style>
:root {
    --background: #f5f7f5;
    --surface: rgba(255,255,255,.88);
    --border: #dce6df;
    --text: #20382f;
    --muted: #63796e;
    --accent: #287467;
}

html, body, .stApp,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 90% 5%,
            rgba(172,215,191,.23),
            transparent 36%
        ),
        radial-gradient(
            circle at 10% 90%,
            rgba(213,229,219,.30),
            transparent 42%
        ),
        #f5f7f5 !important;
    color: var(--text) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 1120px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

.stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp p, .stApp label {
    color: var(--text);
}

[data-testid="stCaptionContainer"] p {
    color: var(--muted) !important;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: rgba(255,255,255,.94) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: .45rem !important;
}

[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
    margin: .75rem 0 !important;
}

.brand-name {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1c4537;
    letter-spacing: -.03em;
}

.brand-description {
    color: #71857a;
    font-size: .82rem;
    margin-top: .2rem;
}

.sidebar-title {
    color: #234437;
    font-size: .87rem;
    font-weight: 750;
    margin: .2rem 0 .5rem;
}

.agent-step {
    display: flex;
    align-items: center;
    gap: .7rem;
    background: #f2f7f3;
    border: 1px solid #e3ebe5;
    border-radius: 11px;
    padding: .5rem .7rem;
    margin-bottom: .35rem;
    color: #365347;
    font-size: .84rem;
}

.step-number {
    display: grid;
    place-items: center;
    width: 25px;
    height: 25px;
    border-radius: 8px;
    background: #dceee4;
    color: #246a55;
    font-weight: 800;
    flex-shrink: 0;
}

.tech-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: .4rem 0 .8rem;
}

.tech-badge {
    background: #edf5ef;
    border: 1px solid #d5e6db;
    border-radius: 7px;
    padding: 5px 9px;
    font-size: .74rem;
    font-weight: 650;
    color: #315c4c;
}

.sidebar-notice {
    background: #f4f8f5;
    border-left: 3px solid #7ea997;
    border-radius: 7px;
    padding: .75rem .8rem;
    color: #60776b;
    font-size: .77rem;
    line-height: 1.6;
}

/* Landing page */

.hero {
    background: linear-gradient(
        115deg,
        rgba(255,255,255,.96),
        rgba(234,246,238,.86)
    );
    border: 1px solid #d5e5da;
    border-radius: 19px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 10px 30px rgba(34,75,54,.045);
    margin-bottom: 1rem;
    backdrop-filter: blur(18px);
}

.hero-eyebrow {
    color: #287467;
    font-size: .69rem;
    font-weight: 800;
    letter-spacing: .13em;
    margin-bottom: .35rem;
}

.hero-title {
    font-size: clamp(1.65rem, 3vw, 2.15rem);
    color: #193a2c;
    font-weight: 800;
    letter-spacing: -.045em;
    margin: 0 0 .4rem;
    line-height: 1.2;
}

.hero-description {
    color: #536e61;
    line-height: 1.6;
    font-size: .91rem;
    margin: 0;
}

.section-heading {
    font-size: .99rem;
    font-weight: 750;
    color: #243e32;
    margin: .4rem 0 .6rem;
}

.section-help {
    font-size: .79rem;
    color: #72867b;
    margin: .55rem 0;
}

/* Buttons */

[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {
    background: #fff !important;
    border: 1px solid #d8e5dc !important;
    color: #294d3e !important;
    border-radius: 12px !important;
    min-height: 2.8rem !important;
    font-weight: 650 !important;
}

[data-testid="stButton"] button *,
[data-testid="stDownloadButton"] button * {
    color: inherit !important;
}

[data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover {
    background: #eff7f1 !important;
    border-color: #91b9a3 !important;
}

[data-testid="stButton"] button[kind="primary"] {
    background: #287467 !important;
    border-color: #287467 !important;
    color: white !important;
    min-height: 3rem !important;
    font-weight: 750 !important;
}

[data-testid="stButton"] button[kind="primary"]:hover {
    background: #205d53 !important;
    color: white !important;
}

/* Inputs */

[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,.92) !important;
    color: #243e32 !important;
    border: 1px solid #d6e4db !important;
    border-radius: 12px !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #82988b !important;
}

[data-testid="stTextInput"] input:disabled {
    color: #607b6d !important;
    -webkit-text-fill-color: #607b6d !important;
}

/* Results heading */

.results-intro {
    padding: 1.25rem 1.5rem;
    background: rgba(255,255,255,.89);
    border: 1px solid var(--border);
    border-radius: 17px;
    margin: 1.25rem 0;
}

.results-kicker {
    color: #287467;
    font-size: .7rem;
    letter-spacing: .1em;
    font-weight: 800;
}

.results-title {
    color: #1c3b2e;
    font-size: 1.55rem;
    font-weight: 800;
    margin: .35rem 0;
}

.results-subtitle {
    color: #70867a;
    font-size: .85rem;
    line-height: 1.55;
}

/* Cards */

.result-card {
    background: rgba(255,255,255,.92);
    border: 1px solid #dce7df;
    border-radius: 15px;
    padding: 1.1rem 1.25rem;
    margin-bottom: .75rem;
    box-shadow: 0 5px 18px rgba(33,70,48,.035);
}

.card-eyebrow {
    color: #688173;
    font-size: .68rem;
    font-weight: 750;
    letter-spacing: .09em;
    text-transform: uppercase;
}

.card-title {
    color: #203c30;
    font-size: 1.05rem;
    font-weight: 750;
    margin: .35rem 0;
}

.card-muted {
    color: #6a8174;
    font-size: .84rem;
    line-height: 1.6;
}

.flight-route {
    display: grid;
    grid-template-columns: 1fr 42px 1fr;
    gap: 10px;
    align-items: center;
    margin: .9rem 0;
}

.flight-airport {
    font-size: 1rem;
    font-weight: 750;
    color: #244437;
    overflow-wrap: anywhere;
}

.flight-route-arrow {
    color: #7ca38b;
    text-align: center;
    font-size: 1.25rem;
}

.flight-status {
    display: inline-block;
    border-radius: 20px;
    padding: 5px 11px;
    background: #edf5ee;
    border: 1px solid #d9e8db;
    color: #426e4f;
    font-size: .75rem;
    font-weight: 700;
}

.result-label {
    font-weight: 750;
    color: #234437;
    margin-bottom: .75rem;
}

/* Tabs */

[data-testid="stTabs"] [role="tablist"] {
    gap: .35rem;
    border-bottom: 1px solid #dce6df !important;
}

[data-testid="stTabs"] [role="tab"] {
    color: #526c5d !important;
    font-weight: 650 !important;
    padding: .7rem 1rem !important;
}

[data-testid="stTabs"] [role="tab"] * {
    color: inherit !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #287467 !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: #287467 !important;
}

[data-testid="stTabs"] [role="tabpanel"] {
    padding-top: 1rem !important;
}

/* Report-style Markdown blocks */

.report-container {
    padding: .3rem 0;
}

.report-heading {
    font-weight: 800;
    color: #244236;
    margin-bottom: .7rem;
}

/* Native Streamlit cards and metrics */

[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: #dce6df !important;
    border-radius: 15px !important;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,.87);
    border: 1px solid #dce6df;
    border-radius: 13px;
    padding: .75rem 1rem;
}

[data-testid="stMetric"] * {
    color: #284538 !important;
}

@media(max-width:768px) {
    .block-container {
        padding: 1rem .8rem 2rem !important;
    }
    .hero {
        padding: 1rem 1.1rem;
    }
    .flight-route {
        grid-template-columns: 1fr 25px 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# APPLICATION CONSTANTS
# ============================================================

DESTINATIONS = [
    (
        "Tokyo",
        "Plan a 5-day trip to Tokyo, Japan, "
        "including hotels, sightseeing and an estimated budget.",
    ),
    (
        "Paris",
        "Plan a 5-day trip to Paris, France, "
        "including hotels, attractions and local transport.",
    ),
    (
        "Rome",
        "Plan a 4-day trip to Rome, Italy, "
        "including hotels, food and historic attractions.",
    ),
    (
        "Bangkok",
        "Plan a 6-day trip to Bangkok, Thailand, "
        "including hotels, food and sightseeing.",
    ),
]

AGENTS = {
    "flight_agent": ("Flight research", "flight_results"),
    "hotel_agent": ("Hotel discovery", "hotel_results"),
    "itinerary_agent": ("Itinerary", "itinerary"),
    "final_agent": ("Final plan", "final_response"),
}


# ============================================================
# SESSION MANAGEMENT
# ============================================================

def new_thread_id() -> str:
    return f"travel-{uuid4().hex[:12]}"


def initialize_session() -> None:
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = new_thread_id()

    if "trip_query" not in st.session_state:
        st.session_state.trip_query = ""

    if "last_plan" not in st.session_state:
        st.session_state.last_plan = None


def select_destination(query: str) -> None:
    st.session_state.trip_query = query
    st.session_state.last_plan = None


def start_new_trip() -> None:
    st.session_state.thread_id = new_thread_id()
    st.session_state.trip_query = ""
    st.session_state.last_plan = None


initialize_session()


# ============================================================
# PRESENTATION HELPERS
# ============================================================

def safe_html(value: object) -> str:
    """Escape external or model-provided text for HTML output."""
    return escape(str(value), quote=True)


def safe_source_url(url: str) -> str | None:
    """Accept only HTTP(S) links returned by search providers."""
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return None

    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url.strip()

    return None


def parse_flights(text: str) -> list[dict[str, str]]:
    """Parse the current Aviationstack text output into display cards.

    This is a temporary presentation adapter until the flight
    tool provides structured JSON-compatible results.
    """
    flights = []

    for block in re.split(r"\n\s*\n", text.strip()):
        record = {}

        for line in block.splitlines():
            if ":" not in line:
                continue

            label, value = line.split(":", 1)
            key = label.strip().lower()

            if key in {"airline", "departure", "arrival", "status"}:
                record[key] = value.strip()

        if "departure" in record or "arrival" in record:
            flights.append(record)

    return flights


def parse_hotels(text: str) -> list[dict[str, str]]:
    """Parse formatted Tavily results into hotel research cards.

    Tavily returns web search results, not confirmed hotel offers.
    """
    hotels = []

    blocks = re.split(
        r"\n\s*\n(?=\d+\.\s)",
        text.strip(),
    )

    for block in blocks:
        lines = [line.strip() for line in block.splitlines()]

        if not lines:
            continue

        heading = re.match(
            r"^\d+\.\s+(.+)$",
            lines[0],
        )

        if not heading:
            continue

        title = heading.group(1).strip().strip("*")
        url = ""
        description = []

        for line in lines[1:]:
            if line.startswith(("https://", "http://")) and not url:
                url = line
            elif line:
                description.append(line)

        hotels.append({
            "title": title,
            "url": url,
            "description": " ".join(description),
        })

    return hotels


def export_markdown(
    query: str,
    thread_id: str,
    results: dict[str, str],
) -> str:
    sections = [
        "# VoyageFlow AI — Travel Plan",
        f"**Request:** {query}",
        f"**Generated:** {datetime.now().astimezone():%Y-%m-%d %H:%M %Z}",
        f"**Session:** {thread_id}",
    ]

    for title, key in (
        ("Flight information", "flight_results"),
        ("Hotel research", "hotel_results"),
        ("Itinerary", "itinerary"),
        ("Final travel plan", "final_response"),
    ):
        content = results.get(key) or "No data available."
        sections.append(f"## {title}\n\n{content}")

    sections.append(
        "*Research only. Verify pricing, schedules and "
        "availability directly with travel providers.*"
    )

    return "\n\n".join(sections) + "\n"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div class="brand-name">VoyageFlow AI</div>'
        '<div class="brand-description">'
        'Your intelligent travel companion'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-title">Travel session</div>',
        unsafe_allow_html=True,
    )

    st.text_input(
        "Session ID",
        value=st.session_state.thread_id,
        disabled=True,
        help="Your LangGraph checkpoint session in PostgreSQL.",
    )

    st.button(
        "Start a new trip",
        key="new_trip",
        on_click=start_new_trip,
        use_container_width=True,
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-title">Your AI travel team</div>',
        unsafe_allow_html=True,
    )

    for number, label in enumerate(
        [
            "Flight research",
            "Hotel discovery",
            "Itinerary planning",
            "Final travel plan",
        ],
        start=1,
    ):
        st.markdown(
            '<div class="agent-step">'
            f'<span class="step-number">{number}</span>'
            f'<span>{escape(label)}</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        '<div class="sidebar-title">Powered by</div>',
        unsafe_allow_html=True,
    )

    technology_badges = "".join(
        f'<span class="tech-badge">{escape(name)}</span>'
        for name in (
            "LangGraph",
            "Groq",
            "Tavily",
            "Aviationstack",
            "PostgreSQL",
        )
    )

    st.markdown(
        f'<div class="tech-list">{technology_badges}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-notice">'
        'Travel suggestions are for research and planning. '
        'Verify prices, schedules and availability before booking.'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# LANDING PAGE
# ============================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-eyebrow">'
    'INTELLIGENT TRAVEL PLANNING'
    '</div>'
    '<h1 class="hero-title">'
    'Your next journey starts here.'
    '</h1>'
    '<p class="hero-description">'
    'Meet <strong>VoyageFlow AI</strong>. '
    'Explore destinations, research travel options, '
    'and create a personalized itinerary with '
    'four coordinated AI agents.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">'
    'Explore a destination'
    '</div>',
    unsafe_allow_html=True,
)

columns = st.columns(4, gap="small")

for column, (city, query) in zip(columns, DESTINATIONS):
    with column:
        st.button(
            city,
            key=f"destination_{city.lower()}",
            on_click=select_destination,
            args=(query,),
            use_container_width=True,
        )


# ============================================================
# TRAVEL INPUT
# ============================================================

st.markdown(
    '<div class="section-heading">Describe your trip</div>',
    unsafe_allow_html=True,
)

st.text_area(
    "Travel request",
    key="trip_query",
    label_visibility="collapsed",
    placeholder=(
        "Example: Plan a 5-day Tokyo trip from Helsinki "
        "for two adults, including hotels and sightseeing."
    ),
    height=100,
)

submitted = st.button(
    "Create my travel plan",
    key="generate_plan",
    type="primary",
    use_container_width=True,
)

st.markdown(
    '<div class="section-help">'
    'Research and planning only. '
    'Prices and availability must be verified.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# EXECUTE LANGGRAPH WORKFLOW
# ============================================================

if submitted:
    query = st.session_state.trip_query.strip()

    if not query:
        st.warning("Please describe your trip first.")
    else:
        st.session_state.last_plan = None

        results = {
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "final_response": "",
        }

        completed_steps = 0

        status = st.status(
            "Your AI travel team is researching...",
            expanded=True,
        )

        try:
            with status:
                initial_state = {
                    "messages": [
                        HumanMessage(content=query),
                    ],
                    "user_query": query,
                    "flight_results": "",
                    "hotel_results": "",
                    "itinerary": "",
                    "llm_calls": 0,
                }

                config = {
                    "configurable": {
                        "thread_id": st.session_state.thread_id,
                    }
                }

                for chunk in app.stream(
                    initial_state,
                    config=config,
                    stream_mode="updates",
                ):
                    for node_name, update in chunk.items():

                        if node_name not in AGENTS:
                            continue

                        if not isinstance(update, dict):
                            continue

                        completed_steps += 1
                        label, result_key = AGENTS[node_name]

                        if node_name == "final_agent":
                            messages = update.get("messages") or []

                            if messages:
                                results[result_key] = str(
                                    messages[-1].content
                                )
                        else:
                            results[result_key] = str(
                                update.get(result_key) or ""
                            )

                        st.write(f"✓ {label} completed")

            if not results["final_response"]:
                raise RuntimeError(
                    "Workflow returned no final response."
                )

            status.update(
                label="Your travel plan is ready",
                state="complete",
                expanded=False,
            )

            st.session_state.last_plan = {
                "query": query,
                "thread_id": st.session_state.thread_id,
                "results": results,
                "steps_completed": completed_steps,
            }

        except Exception:
            logger.exception("Travel planning workflow failed")

            status.update(
                label="Unable to generate travel plan",
                state="error",
                expanded=False,
            )

            st.error(
                "The travel planning workflow encountered an error. "
                "Check the Python terminal for details."
            )


# ============================================================
# RESULTS DASHBOARD
# ============================================================

plan = st.session_state.last_plan

if plan:
    results = plan["results"]

    st.markdown(
        '<div class="results-intro">'
        '<div class="results-kicker">YOUR TRAVEL RESEARCH</div>'
        '<div class="results-title">Your journey, thoughtfully planned.</div>'
        '<div class="results-subtitle">'
        'Explore flight information, hotel research and your '
        'personalized itinerary. Review sources before booking.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(2)

    metric_columns[0].metric(
        "Agent steps completed",
        plan["steps_completed"],
    )

    metric_columns[1].metric(
        "Workflow",
        "Complete",
    )

    st.write("")

    tab_flights, tab_hotels, tab_itinerary, tab_final = st.tabs(
        [
            "Flights",
            "Hotels",
            "Itinerary",
            "Final plan",
        ]
    )

    # --------------------------------------------------------
    # FLIGHT RESEARCH
    # --------------------------------------------------------

    with tab_flights:
        st.markdown("#### Flight information")

        st.info(
            "These are general flight-status records from "
            "Aviationstack. The current integration does not "
            "filter by your requested route or travel date. "
            "They are not ticket offers."
        )

        flights = parse_flights(results["flight_results"])

        if flights:
            for index, flight in enumerate(flights, start=1):
                airline = safe_html(
                    flight.get("airline") or "Unknown airline"
                )
                departure = safe_html(
                    flight.get("departure") or "Unknown airport"
                )
                arrival = safe_html(
                    flight.get("arrival") or "Unknown airport"
                )
                status_text = safe_html(
                    flight.get("status") or "Unknown"
                )

                st.markdown(
                    '<div class="result-card">'
                    f'<div class="card-eyebrow">Flight record {index}</div>'
                    f'<div class="card-title">{airline}</div>'
                    '<div class="flight-route">'
                    '<div>'
                    '<div class="card-eyebrow">Departure</div>'
                    f'<div class="flight-airport">{departure}</div>'
                    '</div>'
                    '<div class="flight-route-arrow">&rarr;</div>'
                    '<div>'
                    '<div class="card-eyebrow">Arrival</div>'
                    f'<div class="flight-airport">{arrival}</div>'
                    '</div>'
                    '</div>'
                    f'<span class="flight-status">{status_text}</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.warning(
                "No structured flight records were available."
            )

        with st.expander("View original flight response"):
            st.code(
                results["flight_results"] or "No flight data",
                language="text",
            )

    # --------------------------------------------------------
    # HOTEL RESEARCH
    # --------------------------------------------------------

    with tab_hotels:
        st.markdown("#### Hotel and accommodation research")

        st.caption(
            "These are web search sources, not verified "
            "hotel room offers or availability."
        )

        hotels = parse_hotels(results["hotel_results"])

        if hotels:
            for index, hotel in enumerate(hotels, start=1):
                st.markdown(
                    '<div class="result-card">'
                    f'<div class="card-eyebrow">Research source {index}</div>'
                    f'<div class="card-title">'
                    f'{safe_html(hotel["title"])}'
                    '</div>'
                    f'<div class="card-muted">'
                    f'{safe_html(hotel["description"] or "No summary available.")}'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                source = safe_source_url(hotel["url"])

                if source:
                    st.link_button(
                        "View source",
                        url=source,
                        key=f"hotel_source_{index}",
                    )
        else:
            st.markdown(
                results["hotel_results"]
                or "_No hotel research available._",
                unsafe_allow_html=False,
            )

    # --------------------------------------------------------
    # ITINERARY
    # --------------------------------------------------------

    with tab_itinerary:
        st.markdown("#### Your day-by-day itinerary")

        st.caption(
            "An AI-generated travel outline based on "
            "the available research."
        )

        with st.container(border=True):
            st.markdown(
                results["itinerary"]
                or "_No itinerary generated._",
                unsafe_allow_html=False,
            )

    # --------------------------------------------------------
    # FINAL TRAVEL PLAN
    # --------------------------------------------------------

    with tab_final:
        st.markdown("#### Complete travel plan")

        st.caption(
            "Your combined travel research and "
            "personalized recommendations."
        )

        with st.container(border=True):
            st.markdown(
                results["final_response"]
                or "_No final plan generated._",
                unsafe_allow_html=False,
            )

        st.info(
            "Before booking, confirm all flight schedules, "
            "hotel rates, opening hours and availability "
            "with the relevant providers."
        )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.write("")

    st.download_button(
        "Download complete travel plan (.md)",
        data=export_markdown(
            plan["query"],
            plan["thread_id"],
            results,
        ),
        file_name=(
            f"voyageflow_plan_{datetime.now():%Y%m%d}.md"
        ),
        mime="text/markdown",
        use_container_width=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "VoyageFlow AI · Intelligent travel research and planning"
)
