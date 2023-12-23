import base64
import email
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def authorize():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

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


def mark_as_unread(service, user_id, msg_id):
    try:
        service.users().messages().modify(
            userId=user_id, id=msg_id, body={"removeLabelIds": ["UNREAD"]}
        )
    except Exception as error:
        print("An error occurred: %s" % error)
