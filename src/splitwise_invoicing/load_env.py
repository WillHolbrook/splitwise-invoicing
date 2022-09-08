import os

from dotenv import load_dotenv
from splitwise import Splitwise

load_dotenv()

environment: str = os.getenv("SPLITWISE_INVOICING_ENV")


def get_splitwise_object() -> Splitwise:
    """
    Gets a splitwise object using the consumer key and secret in .env
    Returns:

    """
    consumer_key = os.getenv("SPLITWISE_CONSUMER_KEY")
    consumer_secret = os.getenv("SPLITWISE_CONSUMER_SECRET")
    return Splitwise(consumer_key, consumer_secret)
