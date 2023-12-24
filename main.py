import os
import utils.email_utils as email_utils
from utils.parsing_utils import Transaction
from utils.ynab_utils import *

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def create_Ynab_transaction(t: Transaction):
    yt = YNABTransaction()
    yt.from_Transaction(t)
    yt.set_account_id(os.getenv("ACCOUNT_ID"))
    yt.set_cleared("cleared")
    return yt


def main():
    creds = email_utils.authorize()

    # fetch emails
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
            ind += 1
        response = email_utils.batch_mark_as_read(
            service, user_id="me", msg_ids=[msg["id"] for msg in messages]
        )
        print(response)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

    # create Transaction objects
    transactions = []
    for fname in os.listdir("scratch"):
        if "lines" in fname:
            continue

        # create the transactions object
        t = Transaction(f"scratch/{fname}")
        transactions.append(t)

    # create a single API call for all transaction objects
    ynab_transactions = [create_Ynab_transaction(t) for t in transactions]
    r = post_transactions(os.getenv("BUDGET_ID"), ynab_transactions)
    print("ynab response:")
    print(r.json())


if __name__ == "__main__":
    main()
