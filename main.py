
"""VoyageFlow AI - Multi-Agent Travel Planning System."""

import os
import operator
from uuid import uuid4
from typing import Annotated, TypedDict

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights


# --------------------------------------------------
# Environment Configuration
# --------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. Check your .env file."
    )


# --------------------------------------------------
# LLM Configuration
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


# --------------------------------------------------
# LangGraph State
# --------------------------------------------------

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# --------------------------------------------------
# Flight Agent
# --------------------------------------------------

def flight_agent(state: TravelState):
    query = state["user_query"]

    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight results fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# Hotel Agent
# --------------------------------------------------

def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"

    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# Itinerary Agent
# --------------------------------------------------

def itinerary_agent(state: TravelState):
    prompt = f"""
Create a travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}
"""

    response = llm.invoke([
        SystemMessage(
            content="You are an expert travel planner."
        ),
        HumanMessage(content=prompt),
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# Final Response Agent
# --------------------------------------------------

def final_agent(state: TravelState):
    final_prompt = f"""
Generate a final travel planning response.

User Request:
{state['user_query']}

Flight Information:
{state['flight_results']}

Hotel Information:
{state['hotel_results']}

Itinerary:
{state['itinerary']}

Clearly distinguish verified information from estimates.
Do not invent flight prices or confirmed booking availability.
"""

    response = llm.invoke([
        SystemMessage(
            content="You are a helpful AI travel planning assistant."
        ),
        HumanMessage(content=final_prompt),
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# LangGraph Workflow
# --------------------------------------------------

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# --------------------------------------------------
# PostgreSQL Checkpoint Persistence
# --------------------------------------------------

_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row,
)

checkpointer = PostgresSaver(_conn)

# Initialize checkpoint tables
checkpointer.setup()

# IMPORTANT:
# Expose the compiled application for frontend.py
app = graph.compile(checkpointer=checkpointer)


# --------------------------------------------------
# Command-Line Entry Point
# --------------------------------------------------

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": f"travel-{uuid4().hex[:12]}"
        }
    }

    user_input = input("Enter travel request: ").strip()

    if not user_input:
        print("Please enter a travel request.")
    else:
        result = app.invoke(
            {
                "messages": [
                    HumanMessage(content=user_input)
                ],
                "user_query": user_input,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
        )

        print("\nFINAL RESPONSE:\n")
        print(result["messages"][-1].content)
