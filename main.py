import utils.email_utils as email_utils

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def main():
    creds = email_utils.authorize()

    try:
        service = build("gmail", "v1", credentials=creds)
        unreads = email_utils.get_messages(service, user_id="me", query="label:unread")
        messages = unreads["messages"]

        if not unreads:
            print("No emails found.")
            return

        # write all found messages to disk
        ind = 0
        for msg in messages:
            mime_msg = email_utils.get_mime_message(
                service, user_id="me", msg_id=msg["id"]
            )
            with open(f"scratch/email_{ind}.txt", "w") as f:
                f.write(mime_msg.get("SUBJECT") + "\n")
                print(mime_msg.get_body(), file=f)
            # email_utils.mark_as_read(service, user_id="me", msg_id=msg["id"])
            ind += 1

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
