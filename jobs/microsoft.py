"""Microsoft internship job scraper."""
import datetime
import logging
from typing import Optional

import requests
from utils.webhook import send_webhook
from utils.job_storage import is_new_job
from config import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def getJobsMicrosoft() -> Optional[int]:
    """Fetch internship jobs from Microsoft careers API.
    
    Returns:
        Number of new jobs found, or None if error occurred.
    """
    try:
        r = requests.get(
            'https://apply.careers.microsoft.com/api/pcsx/search',
            params={
                'domain': 'microsoft.com',
                'query': '',
                'location': '',
                'start': '0',
                'sort_by': 'timestamp',
                'filter_profession': 'software engineering',
                'filter_seniority': 'Intern'
            },
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Microsoft jobs: {e}")
        return None

    try:
        data = r.json()
        jobs = data['data']['positions']
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse Microsoft API response: {e}")
        return None
    
    new_jobs_count = 0
    for job in jobs:
        try:
            title = job['name']
            postingDate = datetime.datetime.fromtimestamp(job['postedTs'])
            location = job['locations']
            department = job['department']
            jobId = job['id']
        except (KeyError, ValueError) as e:
            logger.warning(f"Skipping malformed Microsoft job entry: {e}")
            continue

        url = 'https://apply.careers.microsoft.com/careers/job/' + str(jobId)

        try:
            payload = {
                # 'content': '--',
                'username': 'BigTech Internship Monitoring',
                'avatar_url': None,
                'embeds': [
                    {
                        'title': f'New Internship: {title}',
                        'url': url,
                        'thumbnail': {
                            'url': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%2Fid%2FOIP.6vG35pC3pcMANHZIPAT0twHaHa%3Fpid%3DApi&f=1&ipt=31c85567791d2c2042a71a829e48db38e241a4c4c1c98dee34a30219d266903a&ipo=images'
                        },
                        'fields': [
                            {
                                'name': 'Department',
                                'value': f'{department}',
                            },
                            {
                                'name': 'Location',
                                'value': f'{location}',
                            }, {
                                'name': 'Created At',
                                'value': f'<t:{int(postingDate.timestamp())}:f> | <t:{int(postingDate.timestamp())}:R>'
                            }
                        ],
                        'color': int('F25022', 16),
                        'timestamp': datetime.datetime.now().isoformat(),
                        'footer': {
                            'text': 'BigTech Internship Monitoring | by wiestju'
                        }
                    }
                ]
            }

            company = 'microsoft'
            if is_new_job(company, jobId):
                if send_webhook(company, payload):
                    new_jobs_count += 1
                    logger.info(f"New Microsoft job posted: {title} ({jobId})")
        except Exception as e:
            logger.error(f"Error processing Microsoft job: {e}")
            continue
    
    logger.info(f"Microsoft: Found {new_jobs_count} new jobs")
    return new_jobs_count