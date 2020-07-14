import requests
from datetime import datetime
import time


class BotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text}
        method = "sendMessage"
        resp = requests.post(self.api_url + method, params)
        return resp
