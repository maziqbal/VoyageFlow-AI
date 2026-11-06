"""Aviationstack flight information integration."""

import os

import requests
from dotenv import load_dotenv


load_dotenv()

AVIATIONSTACK_URL = "https://api.aviationstack.com/v1/flights"
REQUEST_TIMEOUT = 15
MAX_RESULTS = 5


def search_flights(query: str) -> str:
    """Fetch and format live flight information from Aviationstack.

    Note:
        The natural-language query is reserved for future
        route/date filtering. This version retrieves general
        live flight information, not ticket prices.
    """
    api_key = os.getenv("AVIATIONSTACK_API_KEY")

    if not api_key:
        raise ValueError(
            "AVIATIONSTACK_API_KEY is missing from .env"
        )

    params = {
        "access_key": api_key,
        "limit": MAX_RESULTS,
    }

    try:
        response = requests.get(
            AVIATIONSTACK_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

    except requests.Timeout as exc:
        raise RuntimeError(
            "Aviationstack request timed out."
        ) from exc

    except requests.RequestException as exc:
        # Do not expose the exception URL: it may contain
        # the API key as a query parameter.
        raise RuntimeError(
            "Aviationstack request failed. "
            "Check network access and API availability."
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "Aviationstack returned invalid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            "Unexpected Aviationstack response format."
        )

    if "error" in data:
        raise RuntimeError(
            "Aviationstack reported an API error. "
            "Check your credentials and usage quota."
        )

    flight_data = data.get("data")

    if not isinstance(flight_data, list):
        raise RuntimeError(
            "Aviationstack response is missing flight data."
        )

    if not flight_data:
        return "No live flight information was found."

    flights = []

    for flight in flight_data[:MAX_RESULTS]:
        if not isinstance(flight, dict):
            continue

        airline_info = flight.get("airline") or {}
        departure_info = flight.get("departure") or {}
        arrival_info = flight.get("arrival") or {}

        airline = airline_info.get("name") or "Unknown"
        departure = departure_info.get("airport") or "Unknown"
        arrival = arrival_info.get("airport") or "Unknown"
        status = flight.get("flight_status") or "Unknown"

        flights.append(
            f"Airline: {airline}\n"
            f"Departure: {departure}\n"
            f"Arrival: {arrival}\n"
            f"Status: {status}"
        )

    if not flights:
        return "No valid flight records were returned."

    return "\n\n".join(flights)
