"""
Quick sanity check for each tool, run BEFORE wiring up the chatbot.

Usage:
    python test_tools.py web        # tests web search only (no Google auth)
    python test_tools.py gmail      # tests Gmail (triggers OAuth on 1st run)
    python test_tools.py calendar   # tests Calendar
    python test_tools.py all        # runs everything

If a single tool works here, it will work in the chatbot. If it fails here,
fix it here first — debugging is 10x easier without the LLM in the loop.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "mcp_servers"))


def test_web():
    print("\n=== Testing web_search ===")
    from websearch_server import web_search
    results = web_search("latest news on AI", num_results=3)
    print(json.dumps(results, indent=2, default=str))


def test_gmail():
    print("\n=== Testing list_recent_emails ===")
    from gmail_server import list_recent_emails
    emails = list_recent_emails(max_results=3)
    print(json.dumps(emails, indent=2, default=str))


def test_calendar():
    print("\n=== Testing get_upcoming_events ===")
    from calendar_server import get_upcoming_events
    events = get_upcoming_events(days_ahead=7)
    print(json.dumps(events, indent=2, default=str))


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {"web": test_web, "gmail": test_gmail, "calendar": test_calendar}

    if target == "all":
        for name, fn in runners.items():
            try:
                fn()
            except Exception as e:
                print(f"[{name}] FAILED: {type(e).__name__}: {e}")
    elif target in runners:
        runners[target]()
    else:
        print(f"Unknown target: {target}. Use: web | gmail | calendar | all")


if __name__ == "__main__":
    main()
