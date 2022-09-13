import os
import json

from splitwise import Group, User, Expense
from splitwise.user import ExpenseUser

from splitwise_invoicing.load_env import get_splitwise_object


s = get_splitwise_object()

s.setOAuth2AccessToken(json.loads(os.environ.get("SPLITWISE_INVOICING_OAUTH2TOKEN_DICT")))
groups_list: list[Group] = s.getGroups()

group = next((group for group in groups_list if group.name == "Development Group"), None)
print(group.__dict__)
members_list: list[User] = group.getMembers()
for member in members_list:
    e = Expense()
    e.
    print(member.getId())
    print(member.getFirstName(), member.getLastName())

