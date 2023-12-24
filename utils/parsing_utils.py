from bs4 import BeautifulSoup
import pprint as pp
from parse import parse
import os
from urllib.parse import unquote

filename = "scratch/email_1.txt"

templates = {
    "paid_you": "{person} paid you ${amount}",
    "you_paid": "You paid {person} ${amount}",
    "paid_your_request": "{person} paid your ${amount} request",
    "you_paid_request": "You completed {person}'s ${amount} charge request",
}

transaction_types = {
    "paid_you": {"isInflow": True, "isChargeRequest": False},
    "you_paid": {"isInflow": False, "isChargeRequest": False},
    "paid_your_request": {"isInflow": True, "isChargeRequest": True},
    "you_paid_request": {"isInflow": False, "isChargeRequest": True},
}


class Transaction:
    def __init__(self, filename) -> None:
        print("processing " + filename)
        lines = get_lines(filename)
        memo = extract_memo(lines)
        date = extract_date(lines)
        transaction_type, person, amount = extract_transaction_type_person_amount(lines)

        self.isInflow = (transaction_types[transaction_type]["isInflow"],)
        self.isChargeRequest = (transaction_types[transaction_type]["isChargeRequest"],)
        self.amount = amount
        self.person = person
        self.date = date
        self.memo = memo

    def __repr__(self) -> str:
        return f"""{{ 
            isInflow: {self.isInflow}
            isChargeRequest: {self.isChargeRequest}
            amount: {self.amount}
            person: {self.person}
            date: {self.date}
            memo: {self.memo}
          }}"""


def process_line(s):
    return s.replace("=20", " ").strip()


def get_lines(filename):
    f = open(filename, "r")
    soup = BeautifulSoup(f, "html.parser")
    f.close()
    strings = [process_line(s) for s in soup.strings if process_line(s)]
    return strings


def extract_transaction_type_person_amount(lines) -> (str, str, str):
    """
    returns type, person, amount
    """
    subject = lines[0].split("Fwd:")[1].split("\n")[0].strip()
    parses = [(type, parse(template, subject)) for type, template in templates.items()]
    # filter for the only not-None parse
    res = [p for p in parses if p[1] is not None][0]

    return res[0], res[1]["person"], res[1]["amount"]


def extract_date(lines: []):
    i = lines.index("Transfer Date and Amount:")
    return lines[i + 1]


def extract_memo(lines: []):
    i = lines.index("Transfer Date and Amount:")
    memo = lines[i - 1]
    memo = memo.replace("=", "%")
    memo = unquote(memo)
    return memo


def main():
    # process a single file
    # extract lines

    for fname in os.listdir("scratch"):
        if "lines" in fname:
            continue

        # create the transaction object
        t = Transaction(f"scratch/{fname}")
        print(t)


if __name__ == "__main__":
    main()
