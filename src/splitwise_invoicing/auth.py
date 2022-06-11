import os
import webbrowser

from splitwise import Splitwise

import splitwise_invoicing.load_env


def post_auth(oauth2_code: str, oauth2_state: str) -> None:
    """
    Function that is run from the server after the authorization call

    Args:
        oauth2_code: The code passed back from the oauth url
        oauth2_state: The state passed back from the oauth url

    Returns:
        None
    """


consumer_key = os.getenv("SPLITWISE_CONSUMER_KEY")
consumer_secret = os.getenv("SPLITWISE_CONSUMER_SECRET")

s = Splitwise(consumer_key, consumer_secret)
redirect_url = os.getenv("SPLITWISE_REDIRECT_URL")

url, state = s.getOAuth2AuthorizeURL(redirect_url)
webbrowser.open_new(url)
