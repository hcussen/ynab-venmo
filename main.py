import os
import argparse
import utils.email_utils as email_utils
from utils.parsing_utils import Transaction
from utils.ynab_utils import *

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--fetch",
        help="fetch new emails, default False",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-r",
        "--read",
        help="mark emails as read, defaults to true",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "-p",
        "--post",
        help="post transactions to YNAB, defaults to true",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "--real",
        help="post transactions to real budget, not dev budget",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    return args


def create_Ynab_transaction(t: Transaction, real: bool):
    yt = YNABTransaction()
    yt.from_Transaction(t)
    yt.set_account_id(os.getenv("REAL_ACCOUNT_ID" if real else "DEV_ACCOUNT_ID"))
    yt.set_cleared("cleared")
    return yt


def main():
    args = get_arguments()

    if args.fetch:
        creds = email_utils.authorize()

        # fetch emails
        try:
            service = build("gmail", "v1", credentials=creds)
            unreads = email_utils.get_messages(
                service, user_id="me", query="label:unread"
            )

            if unreads["resultSizeEstimate"] == 0:
                print("No new emails found.")
                return

            messages = unreads["messages"]

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
            if args.read:
                response = email_utils.batch_mark_as_read(
                    service, user_id="me", msg_ids=[msg["id"] for msg in messages]
                )
                if response:
                    print("unable to mark emails as read")

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    # create Transaction objects
    transactions = []
    for fname in os.listdir("scratch"):
        if "lines" in fname:
            continue

        # create the transactions object
        try:
            t = Transaction(f"scratch/{fname}")
            transactions.append(t)
        except:
            print("Couldn't parse this email, moving on")

    # create a single API call for all transaction objects
    ynab_transactions = [
        create_Ynab_transaction(t, real=args.real) for t in transactions
    ]
    if args.post:
        r = post_transactions(
            os.getenv("REAL_BUDGET_ID" if args.real else "DEV_BUDGET_ID"),
            ynab_transactions,
        )
        print("ynab response:")
        print(r.json())


if __name__ == "__main__":
    main()
