import os
import json
from dotenv import load_dotenv

load_dotenv('.env', override=True)
config_json = os.getenv('WEBHOOK_URLS_JSON')

WEBHOOK_URLS = json.loads(config_json)

GITHUB_STORAGE_URL = 'https://api.github.com/repos/wiestju/bigtech-internship-monitoring/contents/data/known_jobs.json'