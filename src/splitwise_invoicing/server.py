from enum import Enum

from fastapi import FastAPI


app = FastAPI()


@app.get("/splitwise/oauth2")
async def read_user_item(code: str, state: str):
    item = {"oauth2_token": code, "state": state}
    return item
