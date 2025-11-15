"""Apple internship job scraper."""
import datetime
import logging
from typing import Optional

import requests
from utils.webhook import send_webhook
from utils.job_storage import is_new_job
from config import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def getJobsApple() -> Optional[int]:
    """Fetch internship jobs from Apple careers API.
    
    Returns:
        Number of new jobs found, or None if error occurred.
    """
    try:
        r = requests.post(
            'https://jobs.apple.com/api/v1/search',
            json={
                "filters": {
                    "postingType": ["Internship"]
                }
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Apple jobs: {e}")
        return None

    try:
        data = r.json()
        # Apple API returns data in res.searchResults
        if 'res' not in data or 'searchResults' not in data['res']:
            logger.error(f"Unexpected Apple API response structure: {list(data.keys())}")
            return None
        jobs = data['res']['searchResults']
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse Apple API response: {e}")
        return None
    
    new_jobs_count = 0
    for job in jobs:
        try:
            title = job['postingTitle']
            jobId = job['postingId']
            locations = ', '.join([loc['name'] for loc in job.get('locations', [])])
            team = job.get('team', {}).get('teamName', 'N/A')
            job_type = job.get('postingType', 'Internship')
            posted_date = job.get('postingDate', '')
            
            url = f'https://jobs.apple.com/en-us/details/{jobId}'
        except (KeyError, TypeError) as e:
            logger.warning(f"Skipping malformed Apple job entry: {e}")
            continue

        try:
            # Parse posted date if available
            timestamp_str = ''
            if posted_date:
                try:
                    # Apple dates are typically in format like "2024-01-15"
                    posted_dt = datetime.datetime.fromisoformat(posted_date)
                    timestamp_str = f'<t:{int(posted_dt.timestamp())}:f> | <t:{int(posted_dt.timestamp())}:R>'
                except (ValueError, AttributeError):
                    timestamp_str = posted_date

            fields = [
                {
                    'name': 'Team',
                    'value': team,
                },
                {
                    'name': 'Job Type',
                    'value': job_type
                }
            ]
            
            if locations:
                fields.append({
                    'name': 'Locations',
                    'value': locations,
                })
            
            if timestamp_str:
                fields.append({
                    'name': 'Posted At',
                    'value': timestamp_str
                })

            payload = {
                'username': 'BigTech Internship Monitoring',
                'avatar_url': None,
                'embeds': [
                    {
                        'title': f'New Internship: {title}',
                        'url': url,
                        'thumbnail': {
                            'url': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%2Fid%2FOIP.u_w1ED64rKNAEt0D3CTZNAAAAA%3Fpid%3DApi&f=1&ipt=8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e&ipo=images'
                        },
                        'fields': fields,
                        'color': int('A2AAAD', 16),  # Apple Gray
                        'timestamp': datetime.datetime.now().isoformat(),
                        'footer': {
                            'text': 'BigTech Internship Monitoring | by wiestju'
                        }
                    }
                ]
            }

            company = 'apple'
            if is_new_job(company, jobId):
                if send_webhook(company, payload):
                    new_jobs_count += 1
                    logger.info(f"New Apple job posted: {title} ({jobId})")
        except Exception as e:
            logger.error(f"Error processing Apple job: {e}")
            continue
    
    logger.info(f"Apple: Found {new_jobs_count} new jobs")
    return new_jobs_count
