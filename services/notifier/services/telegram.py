import os
import requests

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class TelegramBot:

    def __init__(self):

        self.telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    def send_message(self, message:str):

        req = requests.post(self.telegram_url, data={"chat_id": CHAT_ID, "text": message})

        if req.status_code != 200:

            return {
                "status": req.status_code,
                "message": f"Error: {req.content}"
            }
        
        return {
            "status": req.status_code,
            "message": f"Sucess: {req.content}"
        }