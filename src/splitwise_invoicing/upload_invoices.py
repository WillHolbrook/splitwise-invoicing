import os
import json

from splitwise_invoicing.load_env import get_splitwise_object


s = get_splitwise_object()

s.setOAuth2AccessToken(json.loads(os.environ.get("SPLITWISE_INVOICING_OAUTH2TOKEN_DICT")))

print(s.getCurrentUser().__dict__)
