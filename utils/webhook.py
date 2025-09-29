import requests
from config import WEBHOOK_URLS

def send_webhook(company, payload):

    r = requests.post(
        WEBHOOK_URLS[company],
        json=payload
    )
