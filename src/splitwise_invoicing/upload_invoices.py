import os
import json
from datetime import datetime

from splitwise import Group, User, Expense, SplitwiseError, Splitwise
from splitwise.user import ExpenseUser
import pandas as pd

from splitwise_invoicing.load_env import get_splitwise_object

s = get_splitwise_object()

s.setOAuth2AccessToken(json.loads(os.environ.get("SPLITWISE_INVOICING_OAUTH2TOKEN_DICT")))
groups_list: list[Group] = s.getGroups()

dev_group = next((group for group in groups_list if group.name == "Development Group"), None)
print(dev_group.__dict__)
members_list: list[User] = dev_group.getMembers()
for member in members_list:
    print(member.getId())
    print(member.getFirstName(), member.getLastName())


def add_equally_split_expense(
        group: Group,
        amount: float,
        description: str,
        splitwise_object: Splitwise,
        date: datetime | None = None,
        details: str | None = None):
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
    return splitwise_object.createExpense(e)


expense, error = add_equally_split_expense(dev_group, 10.0, "Test", s, details="big test")
error: SplitwiseError
if error is not None:
    print(error.getErrors())
