import os
import json
from datetime import datetime

from splitwise import Group, User, Expense, SplitwiseError, Splitwise
from splitwise.user import ExpenseUser
import pandas as pd

from splitwise_invoicing.load_env import get_splitwise_object

s = get_splitwise_object()

s.setOAuth2AccessToken(json.loads(os.environ.get("SPLITWISE_INVOICING_OAUTH2TOKEN_DICT")))
transactions_df = pd.read_excel(os.getenv("INPUT_FILE_PATH"), sheet_name=os.getenv("TRANSACTION_SHEET_NAME"))


def add_equally_split_expense(
        group: Group,
        amount: float,
        description: str,
        date: datetime | None = None,
        details: str | None = None) -> tuple[Expense, SplitwiseError]:
    if date is None:
        date = datetime.now()
    e = Expense()
    e.setCost(str(amount))
    e.setDate(str(date))
    e.setDescription(description)
    e.setGroupId(group.id)
    e.setSplitEqually()
    if details is not None:
        e.setDetails(details)
    return s.createExpense(e)


def get_group_by_name(group_name: str) -> Group | None:
    groups_list: list[Group] = s.getGroups()
    return next((group for group in groups_list if group.name == group_name), None)


def parse_row(row) -> None:
    if row[os.getenv("ADD_TO_SPLITWISE_COLUMN_NAME")]:
        print(row)
        transaction_date = row[os.getenv("TRANSACTION_DATE_COLUMN_NAME")]
        description = row[os.getenv("DETAILS_COLUMN_NAME")]
        amount = row[os.getenv("AMOUNT_COLUMN_NAME")]
        splitwise_group = get_group_by_name(row[os.getenv("GROUP_COLUMN_NAME")])
        expense, error = add_equally_split_expense(
            splitwise_group,
            amount,
            description,
            date=transaction_date
        )
        error: SplitwiseError
        if error is not None:
            print(error.getErrors())


transactions_df.apply(parse_row, axis=1)

# expense, error = add_equally_split_expense(dev_group, 10.0, "Test", details="big test")
# error: SplitwiseError
# if error is not None:
#     print(error.getErrors())
