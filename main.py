import os.path
import utils
import email

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
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
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    # results = service.users().labels().list(userId="me").execute()
    # labels = results.get("labels", [])
    unreads = utils.get_messages(service, user_id='me', query='label:unread')
    messages=unreads['messages']

    if not unreads:
      print("No emails found.")
      return
    print("First unread email:")
    # for label in labels:
    # print(unreads)
    msg = utils.get_mime_message(service, user_id='me', msg_id=messages[0]['id'])
    print(msg.get_body())
    # for part in msg.walk():
    #     print(part.get_content_type())
    #     print(part)
    # print(type(email1))
    # print(email1.as_string())
    # with open('email1.txt', 'w') as f:
    #   f.writelines(email1.as_string())
    #   pass



  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()