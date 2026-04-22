"""
MCP tool manager.

Design note for learners:
  Each mcp_servers/*.py file is a FULL MCP server (you can plug them into
  Claude Desktop or any MCP client over stdio). Inside THIS project we take
  a shortcut: we import the tool functions directly instead of spawning
  them as subprocesses. That keeps the code simple and avoids an async
  event-loop dance inside FastAPI.

  If you want to practice the "real" MCP client pattern later, swap the
  imports below for mcp.client.stdio + StdioServerParameters and route tool
  calls through session.call_tool(name, args). The tool SCHEMAS will be
  exactly the same.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "mcp_servers"))

from gmail_server import list_recent_emails, search_emails  # noqa: E402
from calendar_server import get_upcoming_events, check_availability  # noqa: E402
from websearch_server import web_search  # noqa: E402


# Tool registry. Keys = tool names the LLM sees.
# Schema format follows JSON Schema (Gemini + Claude + GPT all accept this).
TOOLS = {
    "list_recent_emails": {
        "function": list_recent_emails,
        "description": (
            "List the most recent emails in the user's Gmail inbox. "
            "Returns subject, sender, date, and snippet."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of emails to return. Default 10."
                },
            },
        },
    },
    "search_emails": {
        "function": search_emails,
        "description": (
            "Search Gmail using Gmail's native query syntax. "
            "Examples: 'from:prof@college.edu', 'has:attachment', 'subject:exam', "
            "'is:unread newer_than:7d'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Gmail search query."},
                "max_results": {"type": "integer", "description": "Max results. Default 10."},
            },
            "required": ["query"],
        },
    },
    "get_upcoming_events": {
        "function": get_upcoming_events,
        "description": (
            "Get the user's Google Calendar events for the next N days. "
            "Use for schedule, meetings, exams, or deadlines questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "How many days ahead to look. Default 7."
                },
            },
        },
    },
    "check_availability": {
        "function": check_availability,
        "description": "Check if the user is free during a specific window on a given date.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format."},
                "start_time": {"type": "string", "description": "Start time HH:MM (24hr)."},
                "end_time": {"type": "string", "description": "End time HH:MM (24hr)."},
            },
            "required": ["date", "start_time", "end_time"],
        },
    },
    "web_search": {
        "function": web_search,
        "description": (
            "Search the web for current info, news, documentation, or anything "
            "the LLM needs real-time data for."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
                "num_results": {"type": "integer", "description": "Number of results. Default 5."},
            },
            "required": ["query"],
        },
    },
}


def call_tool(name: str, args: dict):
    """Execute a tool by name. Returns whatever the tool returns (or an error dict)."""
    if name not in TOOLS:
        return {"error": f"Unknown tool: {name}"}
    try:
        return TOOLS[name]["function"](**(args or {}))
    except TypeError as e:
        return {"error": f"Bad arguments for {name}: {e}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def get_tool_schemas() -> list[dict]:
    """Return all tool schemas as a flat list."""
    return [
        {
            "name": name,
            "description": t["description"],
            "parameters": t["parameters"],
        }
        for name, t in TOOLS.items()
    ]
