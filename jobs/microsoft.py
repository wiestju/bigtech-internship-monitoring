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
            'https://gcsservices.careers.microsoft.com/search/api/v1/search',
            params={
                'et': 'Internship',
                'l': 'en_us',
                'pg': '1',
                'pgSz': '100',
                'o': 'Relevance',
                'flt': 'true',
            },
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Microsoft jobs: {e}")
        return None

    try:
        data = r.json()
        jobs = data['operationResult']['result']['jobs']
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse Microsoft API response: {e}")
        return None
    
    new_jobs_count = 0
    for job in jobs:
        try:
            title = job['title']
            postingDate = datetime.datetime.fromisoformat(job['postingDate'])
            location = job['properties']['primaryLocation']
            profession = job['properties']['profession']
            discipline = job['properties']['discipline']
            educationLevel = job['properties']['educationLevel']
            jobId = job['jobId']
        except (KeyError, ValueError) as e:
            logger.warning(f"Skipping malformed Microsoft job entry: {e}")
            continue

        url = 'https://jobs.careers.microsoft.com/global/en/job/' + jobId

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
                                'name': 'Profession',
                                'value': f'{profession}',
                            },
                            {
                                'name': 'Discipline',
                                'value': f'{discipline}'
                            },
                            {
                                'name': 'Education Level',
                                'value': f'{educationLevel}'
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