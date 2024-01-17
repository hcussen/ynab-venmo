from bs4 import BeautifulSoup
from parse import parse
import os
from urllib.parse import unquote
from datetime import datetime
import pprint as pp

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
        lines = self._get_lines(filename)
        memo = self._extract_memo(lines)
        date = self._extract_date(lines)
        if date is None or memo is None:
            raise Exception(
                "Email wasn't a Transaction type email, Transaction creation failed"
            )
        transaction_type, person, amount = self._extract_transaction_type_person_amount(
            lines
        )

        incoming_format = "%b %d, %Y"
        dt = datetime.strptime(date[:-4], incoming_format)

        self.isInflow = transaction_types[transaction_type]["isInflow"]
        self.isChargeRequest = transaction_types[transaction_type]["isChargeRequest"]
        self.amount = int(amount.replace(".", "")) * 10
        self.person = person
        self.date = dt
        self.memo = memo

    def __repr__(self) -> str:
        return f"""{{\n\tisInflow: {self.isInflow}\n\tisChargeRequest: {self.isChargeRequest}\n\tamount: {self.amount}\n\tperson: {self.person}\n\tdate: {self.date}\n\tmemo: {self.memo}\n}}"""

    def _process_line(self, s):
        s = s.replace("=20", " ")
        s = s.strip()
        return s

    def _get_lines(self, filename):
        f = open(filename, "r")
        soup = BeautifulSoup(f, "html.parser")
        f.close()
        strings = [self._process_line(s) for s in soup.strings if self._process_line(s)]
        head, tail = os.path.split(filename)
        newfile = f"{head}/lines_{tail}"
        with open(newfile, "w") as f:
            f.writelines([l + "\n" for l in strings])
        return strings

    def _extract_transaction_type_person_amount(self, lines) -> (str, str, str):
        """
        returns type, person, amount
        """
        subject = lines[0]
        if "Fwd:" in subject:
            subject = lines[0].split("Fwd:")[1].split("\n")[0].strip()
        if "\n" in subject:
            subject = subject.split("\n")[0]
        parses = [
            (type, parse(template, subject)) for type, template in templates.items()
        ]
        # filter for the not-None parse
        valid_parse = [p for p in parses if p[1] is not None]
        res = (None, None, None)
        if len(valid_parse) > 0:
            res = valid_parse[0]
            return res[0], res[1]["person"], res[1]["amount"]
        return res

    def _extract_date(self, lines: []):
        query = "Transfer Date and Amount:"
        if query in lines:
            i = lines.index(query)
            return lines[i + 1]
        return None

    def _extract_memo(self, lines: []):
        query = "Transfer Date and Amount:"
        if query in lines:
            i = lines.index(query)
            memo = lines[i - 1]
            memo = memo.replace("=", "%")
            memo = unquote(memo)
            return memo
        return None


def main():
    for fname in os.listdir("scratch"):
        if "lines" in fname:
            continue

        # create the transaction object
        t = Transaction(f"scratch/{fname}")
        print(t)


if __name__ == "__main__":
    main()
