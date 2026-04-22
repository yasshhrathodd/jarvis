"""
Google Calendar MCP server.

Two tools:
  - get_upcoming_events: next N days on the primary calendar
  - check_availability: is the user free at a given time window?

Run standalone:
    python mcp_servers/calendar_server.py
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastmcp import FastMCP  # noqa: E402
from google_auth import get_calendar_service  # noqa: E402

mcp = FastMCP("calendar")


def get_upcoming_events(days_ahead: int = 7) -> list[dict]:
    """Get the user's upcoming calendar events for the next N days.

    Use when the user asks about their schedule, meetings, exams,
    deadlines, or anything on their calendar.
    """
    service = get_calendar_service()
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)

    resp = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=50,
    ).execute()

    events = []
    for e in resp.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date"))
        end_time = e["end"].get("dateTime", e["end"].get("date"))
        events.append({
            "id": e.get("id"),
            "title": e.get("summary", "(no title)"),
            "start": start,
            "end": end_time,
            "location": e.get("location", ""),
            "description": (e.get("description") or "")[:300],
        })
    return events


def check_availability(date: str, start_time: str, end_time: str) -> dict:
    """Check if the user is free in a specific time window.

    Args:
        date: YYYY-MM-DD (e.g., "2026-04-25")
        start_time: HH:MM in 24-hour format (e.g., "14:00")
        end_time: HH:MM in 24-hour format (e.g., "15:30")

    Returns availability flag and any conflicting events.
    """
    service = get_calendar_service()
    start_dt = datetime.fromisoformat(f"{date}T{start_time}:00").astimezone(timezone.utc)
    end_dt = datetime.fromisoformat(f"{date}T{end_time}:00").astimezone(timezone.utc)

    resp = service.events().list(
        calendarId="primary",
        timeMin=start_dt.isoformat(),
        timeMax=end_dt.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    conflicts = []
    for e in resp.get("items", []):
        conflicts.append({
            "title": e.get("summary", "(no title)"),
            "start": e["start"].get("dateTime", e["start"].get("date")),
            "end": e["end"].get("dateTime", e["end"].get("date")),
        })

    return {
        "available": len(conflicts) == 0,
        "conflicts": conflicts,
        "window": {"date": date, "start_time": start_time, "end_time": end_time},
    }


mcp.tool()(get_upcoming_events)
mcp.tool()(check_availability)


if __name__ == "__main__":
    mcp.run()
