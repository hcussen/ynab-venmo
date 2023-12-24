import requests

BASE_API = "https://api.ynab.com/v1"


def budgets_endpoint(budget_id):
    return f"{BASE_API}/budgets/{budget_id}/transactions"


class YNABTransaction:
    def __init__(self) -> None:
        self.account_id = ""
        self.date = ""
        self.amount = 0
        self.payee_id = ""
        self.payee_name = ""
        self.category_id = ""
        self.memo = ""
        self.approved = False
        self.flag_color = None
        self.import_id = None

    def as_json(self):
        non_null_member_vars = [
            (key, value) for key, value in vars(self).items() if value
        ]
        return dict(non_null_member_vars)


def main():
    y = YNABTransaction()
    print(y.as_json())


if __name__ == "__main__":
    main()
