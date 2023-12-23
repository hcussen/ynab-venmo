from bs4 import BeautifulSoup
import pprint
from parse import parse

filename = "scratch/email_0.txt"

templates = {
    "paid_you": "{person} paid you ${amount}",
    "you_paid": "You paid {person} ${amount}",
    "paid_your_request": "{person} paid your ${amount} request",
    "you_paid_request": "You completed {person}'s ${amount} charge request",
}


def process_line(s):
    return s.replace("=20", " ").strip()


def get_lines(filename):
    f = open(filename, "r")
    soup = BeautifulSoup(f, "html.parser")
    f.close()
    strings = [process_line(s) for s in soup.strings if process_line(s)]
    return strings


def test_matching():
    filled_string = "Ellie L paid you $6.56"

    for type, template in templates.items():
        r = parse(template, filled_string)
        print(f"using template {type}, found: {r}")


def main():
    test_matching()


if __name__ == "__main__":
    main()
