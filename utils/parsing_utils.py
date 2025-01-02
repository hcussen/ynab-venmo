from bs4 import BeautifulSoup
from parse import parse
import os
from urllib.parse import unquote
from datetime import datetime
import quopri
from email import policy
from email.parser import Parser
import re

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
        lines = self._parse_mime_from_disk(filename)
        self._write_strings_to_disk(filename, lines)
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
        dt = datetime.strptime(date, incoming_format)

        self.isInflow = transaction_types[transaction_type]["isInflow"]
        self.isChargeRequest = transaction_types[transaction_type]["isChargeRequest"]
        self.amount = int(amount.replace(".", "")) * 10
        self.person = person
        self.date = dt
        self.memo = memo

    def __repr__(self) -> str:
        return f"""{{\n\tisInflow: {self.isInflow}\n\tisChargeRequest: {self.isChargeRequest}\n\tamount: {self.amount}\n\tperson: {self.person}\n\tdate: {self.date}\n\tmemo: {self.memo}\n}}"""

    def _decode_quoted_printable_text(self, text):
        """
        Decode quoted-printable text, handling both UTF-8 encoding and line continuations.
        """
        # Convert bytes to string if needed
        if isinstance(text, bytes):
            text = text.decode("utf-8")

        # Remove soft line breaks (= followed by newline)
        text = re.sub("=\r?\n", "", text)

        # Decode the quoted-printable content
        decoded = quopri.decodestring(text.encode("utf-8")).decode("utf-8")

        return decoded

    def _parse_mime_from_disk(self, filename):
        """
        Parse an email file and extract clean text content.
        """
        # First, parse the email properly using email.parser
        with open(filename, "r", encoding="utf-8") as f:
            email_content = f.read()

        # Parse the email message
        msg = Parser(policy=policy.default).parsestr(email_content)
        # If the content is quoted-printable, decode it first
        if msg.get_content_type() == "text/html":
            content = msg.get_payload()
            if msg.get("Content-Transfer-Encoding") == "quoted-printable":
                content = self._decode_quoted_printable_text(content)
        else:
            content = email_content

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        # Extract and clean text
        strings = []
        for string in soup.stripped_strings:
            # Clean the string
            cleaned = string.strip()
            if cleaned:  # Only add non-empty strings
                strings.append(cleaned)

        return strings

    def _write_strings_to_disk(self, filename, strings):
        head, tail = os.path.split(filename)
        newfile = f"{head}/lines_{tail}"
        with open(newfile, "w") as f:
            f.writelines([l + "\n" for l in strings])

    # def _get_lines(self, filename):
    #     f = open(filename, "r")
    #     soup = BeautifulSoup(f, "html.parser")
    #     f.close()
    #     strings = [self._process_line(s) for s in soup.strings if self._process_line(s)]
    #     head, tail = os.path.split(filename)
    #     newfile = f"{head}/lines_{tail}"
    #     with open(newfile, "w") as f:
    #         f.writelines([l + "\n" for l in strings])
    #     return strings

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

    def _extract_date(self, lines):
        query = "Date"
        if query in lines:
            i = lines.index(query)
            return lines[i + 1]
        return None

    def _extract_memo(self, lines):
        query = "See transaction"
        if query in lines:
            i = lines.index(query)
            memo = lines[i - 1]
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
