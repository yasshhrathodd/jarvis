"""
Shared Google OAuth helper used by gmail_server.py and calendar_server.py.

On first run this opens a browser so you can grant permission.
After that, a token.pickle file is saved and reused automatically.
"""
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load .env from the project root (one level up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Scopes = permissions we ask Google for.
# .readonly is safer for MVP. Change to full scopes later if you want send/write.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p


def get_credentials():
    """Return valid Google credentials, running OAuth flow if needed."""
    creds_path = _resolve(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials/google_oauth.json"))
    token_path = _resolve(os.getenv("GOOGLE_TOKEN_PATH", "credentials/token.pickle"))

    creds = None
    if token_path.exists():
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    # If no valid creds, go through auth flow (or refresh if we can)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"Missing {creds_path}. See credentials/README.txt for setup steps."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return creds


def get_gmail_service():
    return build("gmail", "v1", credentials=get_credentials(), cache_discovery=False)


def get_calendar_service():
    return build("calendar", "v3", credentials=get_credentials(), cache_discovery=False)
