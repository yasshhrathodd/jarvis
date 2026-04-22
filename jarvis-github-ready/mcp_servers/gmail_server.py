"""
Gmail MCP server.

Two tools:
  - list_recent_emails: show the latest inbox items
  - search_emails: use Gmail's native search syntax

Run standalone (for Claude Desktop / other MCP clients):
    python mcp_servers/gmail_server.py

The backend imports these functions directly (see backend/mcp_manager.py),
so they are plain Python functions AND registered as MCP tools.
"""
import sys
from pathlib import Path

# Make sure this folder is on sys.path so google_auth imports cleanly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastmcp import FastMCP  # noqa: E402
from google_auth import get_gmail_service  # noqa: E402

mcp = FastMCP("gmail")


def _header(headers, name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _format_message(msg_full: dict) -> dict:
    headers = msg_full.get("payload", {}).get("headers", [])
    return {
        "id": msg_full.get("id"),
        "subject": _header(headers, "Subject"),
        "from": _header(headers, "From"),
        "to": _header(headers, "To"),
        "date": _header(headers, "Date"),
        "snippet": msg_full.get("snippet", ""),
    }


def list_recent_emails(max_results: int = 10) -> list[dict]:
    """List the most recent emails in the user's inbox.

    Returns subject, sender, date, and a snippet for each email.
    Use when the user asks about recent emails, new messages, or their inbox.
    """
    service = get_gmail_service()
    resp = service.users().messages().list(
        userId="me", maxResults=max_results, labelIds=["INBOX"]
    ).execute()

    emails = []
    for m in resp.get("messages", []):
        full = service.users().messages().get(userId="me", id=m["id"], format="metadata",
                                               metadataHeaders=["Subject", "From", "To", "Date"]).execute()
        emails.append(_format_message(full))
    return emails


def search_emails(query: str, max_results: int = 10) -> list[dict]:
    """Search the user's Gmail with Gmail search syntax.

    Examples of query strings:
      - "from:professor@college.edu"
      - "has:attachment"
      - "subject:exam"
      - "is:unread newer_than:7d"
    Use when the user wants to find specific emails.
    """
    service = get_gmail_service()
    resp = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    emails = []
    for m in resp.get("messages", []):
        full = service.users().messages().get(userId="me", id=m["id"], format="metadata",
                                               metadataHeaders=["Subject", "From", "To", "Date"]).execute()
        emails.append(_format_message(full))
    return emails


# Register with FastMCP so this file also works as a standalone MCP server
mcp.tool()(list_recent_emails)
mcp.tool()(search_emails)


if __name__ == "__main__":
    mcp.run()
