# JARVIS

A personal AI assistant chatbot that can read your Gmail, check your Google
Calendar, and search the web — all from a single chat interface.

Built with:
- **FastMCP** — three Model Context Protocol servers (Gmail, Calendar, Web)
- **Google Gemini** — the LLM brain that decides which tool to call
- **FastAPI** — backend chat server
- **Vanilla HTML/CSS/JS** — zero-build chat UI

## Quick Start

See [SETUP.md](SETUP.md) for the full step-by-step guide.

TL;DR:
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # fill in your API keys
# put google_oauth.json in credentials/
python test_tools.py all          # sanity check
./run.sh                          # Windows: run.bat
```

Open http://localhost:8000.

## How It Works

```
  User (browser)
       |
       v
  Frontend (HTML/JS)
       |
       v    POST /chat
  FastAPI backend
       |
       v
  Gemini LLM  <-- sees tool schemas, decides which to call
       |
       v
  MCP Manager
       |
       +--> Gmail MCP tools
       +--> Calendar MCP tools
       +--> Web Search MCP tool
```

When you ask "any exam emails that clash with my calendar?", Gemini decides
to call both `search_emails` and `get_upcoming_events`, cross-references
the results, and replies with a unified answer.

## Project Structure

```
mcp_servers/   Three FastMCP servers — each is also usable standalone with Claude Desktop
backend/       FastAPI + Gemini tool-calling loop
frontend/      Dark-themed chat UI, no build step
credentials/   Google OAuth files (gitignored)
```

## License

MIT — do whatever you want with it.
