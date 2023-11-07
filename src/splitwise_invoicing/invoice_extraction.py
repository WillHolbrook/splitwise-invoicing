import re
from datetime import datetime, date
from pathlib import Path
import pandas as pd

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

from splitwise_invoicing.load_env import environment


def load_hsbc_credit_transaction_data_old(filepath: Path) -> tuple[list[date], list[str], list[float]]:
    pages = []

    for page_layout in extract_pages(filepath):
        pages.append(page_layout)

    dates_regex = "(?:\\d{2} [A-Za-z]{3} \\d{2}\\n)(?:\\d{2} [A-Za-z]{3} \\d{2}\\n)*"
    amounts_regex = "(?:\\d{0,4}.\\d{2}(?:CR)?\\n)(?:\\d{0,4}.\\d{2}(?:CR)?\\n)*"

    received_dates: list[tuple[str, int, float]] = []
    transaction_dates: list[tuple[str, int, float]] = []
    details: list[tuple[str, int, float]] = []
    amounts: list[tuple[str, int, float]] = []

    page_number = 0

    for page in pages:
        min_valid_y = 1000000000000000
        max_valid_y = -1
        buffer = 10
        for element in page:
            if isinstance(element, LTTextContainer):
                element_text = element.get_text()
                if 42.5 < element.x0 < 62.5 and re.fullmatch(dates_regex, element_text):
                    received_dates.append((element_text, page_number, element.y0))
                    min_valid_y = min(min_valid_y, element.y0)
                    max_valid_y = max(max_valid_y, element.y1)
                elif 110 < element.x0 < 130 and re.fullmatch(dates_regex, element_text):
                    transaction_dates.append((element_text, page_number, element.y0))
                    min_valid_y = min(min_valid_y, element.y0)
                    max_valid_y = max(max_valid_y, element.y1)

        for element in page:
            if isinstance(element, LTTextContainer):
                element_text = element.get_text()
                if 190 < element.x0 < 210 and min_valid_y - buffer < element.y0 and element.y1 < max_valid_y + buffer:
                    details.append((element_text, page_number, element.y0))
                elif 512.5 < element.x0 < 532.5 and \
                        min_valid_y - buffer < element.y0 and \
                        element.y1 < max_valid_y + buffer and \
                        re.fullmatch(amounts_regex, element_text):
                    amounts.append((element_text, page_number, element.y0))

        page_number += 1

    transaction_dates = sorted(transaction_dates, key=lambda x: (x[1], -x[2]))
    details = sorted(details, key=lambda x: (x[1], -x[2]))
    amounts = sorted(amounts, key=lambda x: (x[1], -x[2]))

    transaction_dates: list[date] = [datetime.strptime(y, "%d %b %y").date() for x in transaction_dates for y in
                                     x[0].strip().split("\n")]
    details: list[str] = [y.replace(")", "") for x in details for y in x[0].strip().split("\n")]
    amounts: list[float] = [-float(y[:-2]) if y.endswith("CR") else float(y) for x in amounts for y in
                            x[0].strip().split("\n")]

    return transaction_dates, details, amounts


def load_hsbc_transaction_data(filepath: Path) -> tuple[list[date], list[str], list[float]]:
    transactions = pd.read_csv(filepath, names=["dates", "details", "amount"])

    transactions["dates"] = transactions["dates"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").date())
    transactions["amount"] = transactions["amount"].apply(lambda x: -float(str(x).replace("\"", "").replace(",", "")))

    return transactions["dates"].tolist(), transactions["details"].tolist(), transactions["amount"].tolist()


def load_amex_credit_transaction_data(filepath: Path) -> tuple[list[date], list[str], list[float]]:
    transactions = pd.read_csv(filepath)
    transactions["Date"] = transactions["Date"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").date())
    return transactions["Date"].tolist(), transactions["Description"].tolist(), transactions["Amount"].tolist()


def load_nationwide_debit_transaction_data(filepath: Path) -> tuple[list[date], list[str], list[float]]:
    transactions = pd.read_csv(filepath, skiprows=4, encoding="windows-1252")
    transactions["Date"] = transactions["Date"].apply(lambda x: datetime.strptime(x, "%d %b %Y").date())
    transactions["Amount"] = transactions.apply(
        lambda x: float(str(x["Paid out"]).replace("£", "").replace("nan", "0")) - float(
            str(x["Paid in"]).replace("£", "").replace("nan", "0")), axis=1)
    transactions["Out Details"] = transactions.apply(
        lambda x: f'{str(x["Transaction type"])} - {str(x["Description"])}', axis=1)

    return transactions["Date"].tolist(), transactions["Out Details"].tolist(), transactions["Amount"].tolist()
