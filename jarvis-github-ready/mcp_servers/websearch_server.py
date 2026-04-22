"""
Web search MCP server using the Serper API (serper.dev).

Sign up at https://serper.dev for a free API key (2500 queries/month).
Set SERPER_API_KEY in your .env file.

Run standalone:
    python mcp_servers/websearch_server.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from fastmcp import FastMCP  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

mcp = FastMCP("websearch")

SERPER_URL = "https://google.serper.dev/search"


def web_search(query: str, num_results: int = 5) -> list[dict]:
    """Search the web via Google (through the Serper API).

    Use when the user asks for current information, recent news, documentation,
    or anything that needs real-time web data.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [{"error": "SERPER_API_KEY not set. Add it to your .env file."}]

    try:
        response = httpx.post(
            SERPER_URL,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num_results},
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as e:
        return [{"error": f"Search request failed: {e}"}]

    results = []

    # Top answer box (if Google gave us a direct answer)
    if "answerBox" in data:
        ab = data["answerBox"]
        results.append({
            "type": "answer_box",
            "title": ab.get("title", ""),
            "answer": ab.get("answer") or ab.get("snippet", ""),
            "link": ab.get("link", ""),
        })

    for item in data.get("organic", [])[:num_results]:
        results.append({
            "type": "organic",
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
        })

    return results or [{"error": "No results found."}]


mcp.tool()(web_search)


if __name__ == "__main__":
    mcp.run()
