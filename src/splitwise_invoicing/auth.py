import logging
import os
import webbrowser
import json

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from splitwise import Splitwise

from splitwise_invoicing.load_env import environment, get_splitwise_object

logging.info(f"Environment: {environment}")

app = FastAPI()


@app.get("/splitwise/oauth2")
async def read_user_item(code: str, state: str):
    if init_state != state:
        raise Exception(f"Initial state: \"{init_state}\" doesn't equal the returned state: \"{state}\"")

    user = s.getOAuth2AccessToken(code, redirect_url)

    print(json.dumps(user))
    html_content = """
    <html>
        <head>
            <title>User Authorized</title>
        </head>
        <body>
            <h1>You are now authorised please close this window<h1>
        </body>
    </html>

    """
    return HTMLResponse(content=html_content, status_code=200)


s = get_splitwise_object()

redirect_url = os.getenv("SPLITWISE_REDIRECT_URL")
url, init_state = s.getOAuth2AuthorizeURL(redirect_url)
print(init_state)
webbrowser.open(url)

