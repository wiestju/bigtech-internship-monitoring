"""
Webhook module for sending Discord notifications about new jobs.
"""
import logging
from typing import Dict, Any

import requests
from config import WEBHOOK_URLS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def send_webhook(company: str, payload: Dict[str, Any]) -> bool:
    """Send webhook notification for a new job posting.
    
    Args:
        company: Company identifier (e.g., 'amazon', 'microsoft')
        payload: Discord webhook payload with embed data
        
    Returns:
        True if webhook sent successfully, False otherwise.
    """
    if company not in WEBHOOK_URLS:
        logger.error(f"No webhook URL configured for company: {company}")
        return False
    
    webhook_url = WEBHOOK_URLS[company]
    
    try:
        r = requests.post(
            webhook_url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        logger.debug(f"Webhook sent successfully for {company}")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to send webhook for {company}: {e}")
        return False
