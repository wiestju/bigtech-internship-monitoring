import os
import json

config_json = os.getenv('WEBHOOK_URLS_JSON')

WEBHOOK_URLS = json.loads(config_json)