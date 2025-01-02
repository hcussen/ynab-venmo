import requests
import os
from dotenv import load_dotenv
from utils.parsing_utils import Transaction
from datetime import datetime
from typing import List
from pprint import pprint

load_dotenv()

BASE_API = "https://api.ynab.com/v1"


def budgets_endpoint(budget_id):
    return f"{BASE_API}/budgets/{budget_id}/transactions"


def post_transactions(budget_id, transactions: List[Transaction]):
    endpoint = budgets_endpoint(budget_id)
    headers = {"Authorization": f"Bearer {os.getenv('YNAB_TOKEN')}"}
    data = {"transactions": [t.as_json() for t in transactions]}
    print(f"posting data to YNAB api:")
    pprint(data)

    response = requests.post(endpoint, headers=headers, json=data)
    return response


class YNABTransaction:
    def __init__(self) -> None:
        self.account_id = ""
        self.date = ""
        self.amount = 0
        self.payee_id = ""
        self.payee_name = ""
        self.category_id = ""
        self.memo = ""
        self.cleared = ""
        self.approved = False
        self.flag_color = None
        self.import_id = None

    def from_Transaction(self, t: Transaction):
        outgoing_format = "%Y-%m-%d"
        self.date = datetime.strftime(t.date, outgoing_format)
        self.amount = t.amount if t.isInflow else -1 * t.amount
        self.payee_name = t.person
        self.memo = t.memo

    def as_json(self):
        non_null_member_vars = [
            (key, value) for key, value in vars(self).items() if value
        ]
        return dict(non_null_member_vars)

    def set_account_id(self, id):
        self.account_id = id

    def set_cleared(self, status):
        allowed = ["cleared", "uncleared", "reconciled"]
        if not status in allowed:
            raise f"Status is {status} which is not in {allowed}"
        self.cleared = status


def main():
    post_transactions(
        os.getenv("BUDGET_ID"),
    )


if __name__ == "__main__":
    main()
