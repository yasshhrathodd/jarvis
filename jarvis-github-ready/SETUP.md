# JARVIS — Setup Guide

Step-by-step setup. Follow in order. Don't skip.

---

## 1. Prerequisites

- Python 3.11 or higher (`python --version` to check)
- A terminal you're comfortable with

---

## 2. Get Your API Keys (do this BEFORE coding)

### A. Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API key**
3. Copy the key. Save it somewhere safe.

### B. Serper API Key (for web search)

1. Go to https://serper.dev
2. Sign up with Google (free tier: 2500 queries/month)
3. Dashboard -> copy your API key

### C. Google OAuth Credentials (for Gmail + Calendar)

This is the trickiest part. Take it slow.

1. Go to https://console.cloud.google.com/
2. Top bar -> **Select a project** -> **New Project** -> name it `jarvis` -> Create
3. In the search bar at the top, search for **Gmail API** -> click **Enable**
4. Search for **Google Calendar API** -> click **Enable**
5. Left menu -> **APIs & Services** -> **OAuth consent screen**
   - User Type: **External** -> Create
   - App name: `Jarvis`, support email: your email
   - Scopes: skip (next)
   - Test users: **Add Users** -> add your own Gmail address
   - Save and continue through to the end
6. Left menu -> **Credentials** -> **+ Create Credentials** -> **OAuth client ID**
   - Application type: **Desktop app**
   - Name: `jarvis-desktop`
   - Create
7. A popup shows your client ID. Click **Download JSON**.
8. Rename the downloaded file to `google_oauth.json`
9. Move it into the `credentials/` folder of this project.

---

## 3. Install Python Dependencies

Open a terminal in the `jarvis/` folder.

### Mac / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

You should see `(venv)` at the start of your terminal prompt now.

---

## 4. Create Your `.env` File

Copy `.env.example` to `.env` and fill in your real keys.

Mac / Linux:
```bash
cp .env.example .env
```
Windows:
```cmd
copy .env.example .env
```

Open `.env` in any editor and paste your keys:
```
GEMINI_API_KEY=AIza...your real key here
SERPER_API_KEY=your real serper key here
GOOGLE_CREDENTIALS_PATH=credentials/google_oauth.json
GOOGLE_TOKEN_PATH=credentials/token.pickle
```

---

## 5. Test Each Tool Individually (recommended)

Before launching the chatbot, test each MCP tool directly. This catches setup bugs fast.

```bash
# Test web search (no Google auth needed)
python test_tools.py web

# Test Gmail (opens browser for OAuth on FIRST run)
python test_tools.py gmail

# Test Calendar
python test_tools.py calendar
```

When you run `gmail` or `calendar` for the first time, a browser opens.
Click your Google account, click **Continue** through the warning ("Google
hasn't verified this app" — that's fine, you ARE the app), grant access.
A `token.pickle` file will be created in `credentials/`. After that,
no more browser prompts.

---

## 6. Run JARVIS

### Mac / Linux
```bash
./run.sh
```
(if you get permission denied: `chmod +x run.sh` first)

### Windows
```cmd
run.bat
```

### Or directly
```bash
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000 in your browser. Start chatting.

---

## 7. Try These Demo Prompts

- "What's on my calendar this week?"
- "Show me my last 5 emails."
- "Find emails from my professor about exams."
- "Am I free tomorrow at 3pm?"
- "What's the latest news on Gemini AI?"
- "Do I have any exam-related emails this week, and do they clash with my calendar?" (chains Gmail + Calendar)

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | venv not active. Re-run `source venv/bin/activate` (or Windows equivalent). |
| `GEMINI_API_KEY missing` | `.env` not loaded. Check the file is named exactly `.env` (no `.txt`). |
| OAuth error "access blocked" | You're not added as a test user on the consent screen. Go back to step 2C-5. |
| `Insufficient Permission` from Gmail | Delete `credentials/token.pickle`, re-run, re-grant access. |
| Port 8000 already in use | Run with `--port 8001` instead. |
| Frontend looks broken | Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac). |

---

## Project Structure

```
jarvis/
├── mcp_servers/        # 3 FastMCP servers (Gmail, Calendar, Web)
├── backend/            # FastAPI + Gemini tool-calling loop
├── frontend/           # Plain HTML/CSS/JS chat UI
├── credentials/        # Google OAuth files (gitignored)
├── test_tools.py       # Test each tool individually
├── run.sh / run.bat    # One-command startup
├── requirements.txt
├── .env.example
└── SETUP.md            # this file
```

---

## What to Learn Next

After it works, dig into the code in this order:

1. `mcp_servers/websearch_server.py` — simplest MCP server
2. `mcp_servers/google_auth.py` — OAuth flow
3. `mcp_servers/gmail_server.py` — real API integration
4. `backend/mcp_manager.py` — tool registry
5. `backend/gemini_client.py` — LLM tool-calling loop
6. `backend/main.py` — FastAPI glue

Each file has comments explaining what's happening.

Let's get it.
