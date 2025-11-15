"""
Configuration module for BigTech Internship Monitoring.
Loads environment variables and provides configuration constants.
"""
import os
import json
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env', override=True)

def get_required_env(key: str) -> str:
    """Get required environment variable or exit with error."""
    value = os.getenv(key)
    if value is None:
        print(f"ERROR: Required environment variable '{key}' is not set.", file=sys.stderr)
        sys.exit(1)
    return value

def load_webhook_urls() -> dict:
    """Load and parse webhook URLs from environment variable."""
    try:
        config_json = get_required_env('WEBHOOK_URLS_JSON')
        webhook_urls = json.loads(config_json)
        
        if not isinstance(webhook_urls, dict):
            raise ValueError("WEBHOOK_URLS_JSON must be a JSON object")
        
        return webhook_urls
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in WEBHOOK_URLS_JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load webhook URLs: {e}", file=sys.stderr)
        sys.exit(1)

# Configuration constants
WEBHOOK_URLS = load_webhook_urls()
GITHUB_TOKEN = get_required_env('GH_TOKEN')
GITHUB_STORAGE_URL = 'https://api.github.com/repos/wiestju/bigtech-internship-monitoring/contents/data/known_jobs.json'

# Request timeout in seconds
REQUEST_TIMEOUT = 30