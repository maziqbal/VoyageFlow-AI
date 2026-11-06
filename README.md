# VoyageFlow AI

**A multi-agent travel research and itinerary planning prototype built with Python, LangGraph, Groq, Tavily, Aviationstack, PostgreSQL, and Streamlit.**

VoyageFlow AI accepts a natural-language trip request, gathers flight-status information and web-based hotel research, generates a suggested itinerary, and presents a consolidated travel plan. It is a **travel research tool**, not a ticket-booking engine: flight fares, hotel prices, inventory, and reservations are **not verified** by the current implementation.

## What it does

- Runs a four-step LangGraph workflow: flight research, hotel research, itinerary generation, and final response.
- Calls **Aviationstack** for flight information and **Tavily** for web search results.
- Uses **Groq** for LLM-generated itineraries and final travel summaries.
- Saves LangGraph execution checkpoints in **PostgreSQL**.
- Provides a **Streamlit** UI with destination shortcuts, a session identifier, agent progress, result tabs, and Markdown export.
- Can also run from the command line using `python main.py`.

## Architecture

```mermaid
flowchart TD
    U[User request<br/>Streamlit or CLI] --> G[LangGraph StateGraph]
    G --> F[Flight agent]
    F -->|Aviationstack API| FD[Flight-status information]
    FD --> H[Hotel agent]
    H -->|Tavily API| HD[Web search results]
    HD --> I[Itinerary agent]
    I -->|Groq LLM| IT[Suggested itinerary]
    IT --> R[Final response agent]
    R -->|Groq LLM| O[Consolidated travel plan]
    G <-->|Checkpoints by thread ID| PG[(PostgreSQL)]
    O --> UI[UI results and Markdown download]
```

**Important architectural distinction:** These are four named processing nodes in a **fixed sequential graph**, not four independently negotiating or self-routing agents. The flight and hotel nodes call external tools; the itinerary and final response nodes call the LLM.

### Current limitations

| Area | Current behavior |
| --- | --- |
| Flight research | The Aviationstack integration retrieves a small set of flight-status records; it does **not yet extract and apply** origin, destination, or date filters from a natural-language request. Results may be unrelated to the trip. |
| Flight booking | No fare search, ticket inventory, booking, or payment integration. |
| Hotel research | Tavily returns web search snippets and source URLs, **not confirmed room rates or availability**. |
| Itinerary | LLM-generated suggestions can contain unsupported assumptions; users should verify dates, operating hours, costs, and transport details. |
| Memory | PostgreSQL stores LangGraph checkpoints keyed by thread ID. The current prompts do **not yet deliberately use previous turns as conversational memory**. |
| Session handling | Streamlit generates a session ID for a new trip; the CLI currently uses a fixed thread ID. |
| Reliability | External APIs may fail, rate-limit, or be unavailable. Robust retries, fallback behavior, and automated tests remain future work. |

## Technology stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.12 (local virtual environment `langgraph_env312`) |
| Orchestration | LangGraph / LangChain |
| LLM provider | Groq, using the configured model in `main.py` |
| Flight information | Aviationstack API |
| Web research | Tavily API |
| Checkpoint persistence | PostgreSQL + `langgraph-checkpoint-postgres` |
| Web interface | Streamlit |
| Local services | Docker Compose, PostgreSQL, Adminer |

## Project structure

```text
Multi_Agent_System/
├── main.py                 # LangGraph state, agents, graph, and CLI
├── frontend.py             # Streamlit user interface
├── tools/
│   ├── flight_tool.py      # Aviationstack integration
│   └── tavily_tool.py      # Tavily search integration
├── compose.yaml            # PostgreSQL and Adminer services
├── env.example             # Example environment configuration
├── .env                    # Local secrets (ignored by Git)
├── .gitignore
└── README.md
```

The local `langgraph_env312/` virtual environment and `.env` are **not committed** to Git.

## Run locally (Windows / PowerShell)

### 1. Prerequisites

- Python 3.12
- Docker Desktop with Docker Compose
- API keys for Groq, Tavily, and Aviationstack
- Git (optional if using a downloaded source archive)

### 2. Create and activate the environment

From the project root:

```powershell
py -3.12 -m venv langgraph_env312
.\langgraph_env312\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If `langgraph_env312` already exists and works, **reuse it** rather than recreating it.

### 3. Install dependencies

The repository does not yet have a verified, pinned dependency manifest. For the currently shared implementation, install:

```powershell
python -m pip install langgraph langchain-core langchain-groq langgraph-checkpoint-postgres "psycopg[binary,pool]" python-dotenv tavily-python requests streamlit
```

A lockfile or pinned `requirements.txt` should be added after recording and testing the versions used by the working environment.

### 4. Configure environment variables

Copy the example file into a local `.env` file:

```powershell
Copy-Item env.example .env
```

Populate `.env` with your **own** credentials, retaining the database values configured for your Docker volume:

```dotenv
GROQ_API_KEY=replace_with_your_key
TAVILY_API_KEY=replace_with_your_key
AVIATIONSTACK_API_KEY=replace_with_your_key

POSTGRES_USER=travel
POSTGRES_PASSWORD=replace_with_your_local_password
POSTGRES_DB=travel_db
POSTGRES_HOST_PORT=5433
DATABASE_URL=postgresql://travel:replace_with_your_local_password@localhost:5433/travel_db
```

The two password values must agree. For an **already initialized** PostgreSQL volume, changing `POSTGRES_PASSWORD` in `.env` does **not** automatically change the database user's existing password. Do not remove the volume to apply a password change.

Never commit `.env` or API keys. The sample values above are placeholders.

### 5. Start PostgreSQL and Adminer

```powershell
docker compose config --quiet
docker compose up -d
docker compose ps
```

This project uses PostgreSQL via Docker; installing PostgreSQL directly on Windows is unnecessary.

If the supplied `compose.yaml` is unchanged, the services are:

| Service | Address |
| --- | --- |
| PostgreSQL (local application connection) | `localhost:5433` |
| Adminer | <http://localhost:8080> |

For Adminer, select **PostgreSQL**, set **Server** to `postgres`, and enter the database name, user, and password from `.env`. Inside the Docker network, the host is `postgres` on port `5432`; the Windows host uses `localhost:5433`.

PostgreSQL data lives in a named Docker volume. `docker compose down` stops/removes containers but normally preserves the volume; **do not run `docker compose down -v`** unless you intentionally want to delete the database data.

### 6. Run the CLI

```powershell
python main.py
```

Enter a trip request at the prompt. The app initializes the LangGraph PostgreSQL checkpoint tables automatically when it starts and uses the configured `DATABASE_URL`.

### 7. Run the web interface

```powershell
streamlit run frontend.py
```

Open <http://localhost:8501>, describe a trip, and select **Create my travel plan**. The frontend shows progress as the four graph nodes execute, displays results, and offers a Markdown download.

## Example request

> Plan a 3-day trip to Paris from Helsinki for 2 adults in May 2027. Suggest hotels, sightseeing activities, and an estimated budget of €1,500.

Treat returned flight and hotel information as research leads, not confirmed offers. Verify details with airlines, hotels, and official visitor information before purchasing anything.

## Session persistence and privacy

LangGraph uses a PostgreSQL checkpointer so executions can be associated with a `thread_id`. Streamlit creates a new thread ID for new travel sessions. This is **workflow checkpoint persistence**; it is not the same thing as a production-ready user account system, secure multi-user history, or reliable conversational recall. Do not use personal or sensitive travel details in shared demo environments.

## Development workflow

Changes are developed and tested in small, focused commits. Before committing:

```powershell
git status
git diff --cached
```

Stage only the files belonging to the logical change, verify that no secrets are included, run the relevant CLI/UI tests, and then commit and push.

## Planned improvements

- Parse travel requests into structured origin, destination, dates, passengers, and budget fields.
- Implement route/date-aware flight information retrieval; evaluate a separate flight-offer provider if prices and booking options are required.
- Clearly label sourced facts versus estimates and LLM-generated recommendations.
- Add structured agent results, typed state, and accurate LLM-call metrics.
- Improve retries, timeouts, error classification, and graceful degraded responses.
- Use previous conversation history deliberately where appropriate, rather than relying on checkpointing alone.
- Add unit tests with mocked external APIs, linting, dependency pinning, and CI.
- Refactor initialization and connection lifecycle for robust Streamlit reruns and concurrent sessions.
- Add screenshots and a deployment guide after testing a reproducible deployment.

## Disclaimer

VoyageFlow AI is an educational/portfolio prototype for **travel research and planning**. It does not book flights or hotels, guarantee availability or prices, or make reservations. Information generated by external APIs and language models can be incomplete or outdated.
