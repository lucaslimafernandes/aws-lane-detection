import os
import json

import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv

from services.telegram import TelegramBot

load_dotenv()


app = FastAPI()


@app.get("/")
def hello():
    return {
        "status": "healthy",
    }

@app.post("/sns-telegram")
async def handle_sns(request: Request):
    payload = await request.json()

    print("Payload SNS recebido:", json.dumps(payload, indent=2))

    if payload.get("Type") == "SubscriptionConfirmation":
        subscribe_url = payload.get("SubscribeURL")
        print(f"Confirmando subscription em: {subscribe_url}")

        # replace, devido ao uso do localstack (localstack-main compose name)
        subscribe_url = subscribe_url.replace("localhost.localstack.cloud", "localstack-main")
        requests.get(subscribe_url)
        return {"status": "confirmed"}

    message = payload.get("Message", "Notificação SNS")
    bot = TelegramBot()
    result = bot.send_message(message)

    return {
        "status": "received",
        "sns_message": message,
        "telegram_response": result
    }

