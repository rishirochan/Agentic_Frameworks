"""Handles Google Calendar API OAuth 2.0 authentication."""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete token.json to re-authenticate
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Paths relative to this file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')


def get_calendar_service():
    """Authenticates and returns the Google Calendar API service."""
    creds = None
    
    # Check for existing token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # No token or can't refresh - need full OAuth flow
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_PATH}. "
                    "Download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the token for future runs
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
    
    # Build and return the Calendar API service
    service = build('calendar', 'v3', credentials=creds)
    return service


if __name__ == '__main__':
    # Quick test - run this file directly to test authentication
    service = get_calendar_service()
    print("Authentication successful!")
    print(f"Token saved to: {TOKEN_PATH}")
    
    # List next 5 upcoming events as a sanity check
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=5,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    if not events:
        print("No upcoming events found.")
    else:
        print(f"\nNext {len(events)} upcoming event(s):")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"  - {start}: {event['summary']}")
