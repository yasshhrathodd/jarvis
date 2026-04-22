Drop your Google OAuth credential file here.

1. Go to https://console.cloud.google.com/
2. Create a project (call it "xyz")
3. Enable: Gmail API, Google Calendar API
4. OAuth consent screen: External, add your email as a test user
5. Credentials -> Create OAuth client ID -> Desktop app
6. Download the JSON, rename to: google_oauth.json
7. Place it in THIS folder (credentials/google_oauth.json)

On first run, a browser window opens for you to grant access.
After that, a token.pickle file is created here automatically for future runs.
