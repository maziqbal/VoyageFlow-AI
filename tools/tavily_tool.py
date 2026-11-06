"""Tavily web search integration for travel research."""

import os

import requests
from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

MAX_RESULTS = 5
MAX_SNIPPET_LENGTH = 300
REQUEST_TIMEOUT = 15


def tavily_search(query: str) -> str:
    """Search the web using Tavily and format the results.

    Args:
        query: Natural-language search query.

    Returns:
        Formatted search results containing titles,
        source URLs, and content snippets.

    Raises:
        ValueError: If the query or API key is missing.
        RuntimeError: If the search request fails or
            the API returns an invalid response.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError(
            "Search query must be a non-empty string."
        )

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is missing from .env"
        )

    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=query.strip(),
            max_results=MAX_RESULTS,
            timeout=REQUEST_TIMEOUT,
        )

    except requests.exceptions.RequestException:
        raise RuntimeError(
            "Tavily search failed due to a network or API error."
        ) from None

    except TimeoutError:
        raise RuntimeError(
            "Tavily search request timed out."
        ) from None

    if not isinstance(response, dict):
        raise RuntimeError(
            "Unexpected Tavily API response format."
        )

    results = response.get("results")

    if not isinstance(results, list):
        raise RuntimeError(
            "Tavily response is missing search results."
        )

    if not results:
        return "No search results found."

    formatted_results = []

    for result in results[:MAX_RESULTS]:
        if not isinstance(result, dict):
            continue

        title = result.get("title") or "Unknown"
        url = result.get("url") or ""
        snippet = result.get("content") or ""

        title = str(title).strip()
        url = str(url).strip()
        snippet = str(snippet).strip()

        if len(snippet) > MAX_SNIPPET_LENGTH:
            snippet = snippet[:MAX_SNIPPET_LENGTH]
            snippet = snippet.rsplit(" ", 1)[0] + "..."

        formatted_results.append(
            f"{len(formatted_results) + 1}. **{title}**\n"
            f"   {url}\n"
            f"   {snippet}"
        )

    if not formatted_results:
        return "No valid search results found."

    return "\n\n".join(formatted_results)
