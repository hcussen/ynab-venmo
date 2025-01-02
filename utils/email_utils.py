import base64
import email
import os.path
import pickle
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]
TOKEN_PICKLE_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"


def authorize():
    creds = None
    """Handles the OAuth2 flow with refresh token support."""
    creds = None

    # Load existing credentials from pickle file if it exists
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, "rb") as token:
            creds = pickle.load(token)

    # If credentials exist but are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error refreshing token: {e}")
            creds = None

    # If no valid credentials available, start OAuth flow
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(
                "credentials.json not found. Please download OAuth 2.0 Client ID credentials "
                "from Google Cloud Console and save as 'credentials.json'"
            )

        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(TOKEN_PICKLE_FILE, "wb") as token:
            pickle.dump(creds, token)

    return creds


def get_messages(service, user_id, query):
    try:
        return service.users().messages().list(userId=user_id, q=query).execute()
    except Exception as error:
        print("An error occurred: %s" % error)


def get_message(service, user_id, msg_id):
    try:
        return (
            service.users()
            .messages()
            .get(userId=user_id, id=msg_id, format="metadata")
            .execute()
        )
    except Exception as error:
        print("An error occurred: %s" % error)


def get_mime_message(service, user_id, msg_id):
    try:
        message = (
            service.users()
            .messages()
            .get(userId=user_id, id=msg_id, format="raw")
            .execute()
        )
        print("Message snippet: %s" % message["snippet"])
        msg_str = base64.urlsafe_b64decode(message["raw"].encode("utf-8")).decode(
            "utf-8"
        )
        mime_msg = email.message_from_string(msg_str, policy=email.policy.default)
        return mime_msg
    except Exception as error:
        print("An error occurred: %s" % error)


def mark_as_read(service, user_id, msg_id):
    try:
        service.users().messages().modify(
            userId=user_id, id=msg_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
    except Exception as error:
        print("An error occurred: %s" % error)


def batch_mark_as_read(service, user_id, msg_ids: List[str]):
    try:
        service.users().messages().batchModify(
            userId=user_id, body={"ids": msg_ids, "removeLabelIds": ["UNREAD"]}
        ).execute()
    except Exception as error:
        print("An error occurred: %s" % error)


def main():
    """
    test harness
    """
    creds = authorize()
    try:
        service = build("gmail", "v1", credentials=creds)
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
