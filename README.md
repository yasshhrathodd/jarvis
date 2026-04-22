# JARVIS — Personal AI Assistant

A unified AI assistant that combines Gmail, Google Calendar, and Web Search into a single chat interface, powered by Google Gemini and the Model Context Protocol (MCP).

Built using:
- **FastMCP** — three Model Context Protocol servers (Gmail, Calendar, Web)
- **Google Gemini** — the LLM brain that decides which tool to call
- **FastAPI** — backend chat server
- **Vanilla HTML/CSS/JS** — zero-build chat UI

## Project Code

All source code, setup instructions, and documentation are inside the [`jarvis-github-ready/`](./jarvis-github-ready) folder.

## Quick Start

See [`jarvis-github-ready/SETUP.md`](./jarvis-github-ready/SETUP.md) for the full step-by-step guide on how to run this project locally.

## How It Works

When you ask JARVIS something like *"any exam emails that clash with my calendar?"*, Gemini decides to call both `search_emails` and `get_upcoming_events`, cross-references the results, and replies with a unified answer — all through MCP tool-calling.

## Author

Built by Yash Rathod.

## License

MIT
