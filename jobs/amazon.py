"""Amazon internship job scraper."""
import datetime
import logging
from typing import Optional

import requests
from utils.webhook import send_webhook
from utils.job_storage import is_new_job
from config import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def getJobsAmazon() -> Optional[int]:
    """Fetch internship jobs from Amazon careers API.
    
    Returns:
        Number of new jobs found, or None if error occurred.
    """
    try:
        r = requests.post(
            'https://www.amazon.jobs/api/jobs/search',
            params={
                'is_als': 'true'
            },
            json={
                "accessLevel": "EXTERNAL",
                "contentFilterFacets": [
                    {
                        "name": "primarySearchLabel",
                        "requestedFacetCount": 9999,
                        "values": [{"name": "studentprograms.team-internships-for-students"}]
                    }
                ],
                "excludeFacets": [
                    {"name": "isConfidential", "values": [{"name": "1"}]},
                    {"name": "businessCategory", "values": [{"name": "a-confidential-job"}]},
                    {"name": "isTech", "values": [{"name": "0"}]},
                ],
                "jobTypeFacets": [
                    {
                        "name": "employeeClass",
                        "values": [{"name": "Intern"}]
                    }
                ],
                "size": 100,
                "start": 0,
                "sort": {
                    "sortOrder": "DESCENDING",
                    "sortType": "SCORE"
                },
                "treatment": "OM",
            },
            headers={
                'accept-encoding': 'plain'
            },
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Amazon jobs: {e}")
        return None

    try:
        data = r.json()
        searchHits = data.get('searchHits', [])
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse Amazon API response: {e}")
        return None
    
    new_jobs_count = 0
    for hit in searchHits:
        try:
            hit = hit['fields']
            title = hit['title'][0]
            country = hit['country'][0]
            updatedDate = hit['updatedDate'][0]
            location = hit['location'][0]
            jobRole = hit['jobRole'][0] if 'jobRole' in hit else '---'
            jobFamily = hit['jobFamily'][0] if 'jobFamily' in hit else '---'
            category = hit['category'][0]
            jobId = hit['icimsJobId'][0]
            url = 'https://www.amazon.jobs/jobs/' + jobId
        except (KeyError, IndexError) as e:
            logger.warning(f"Skipping malformed Amazon job entry: {e}")
            continue

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
                            'url': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2F01%2Fca%2Fda%2F01cada77a0a7d326d85b7969fe26a728.jpg&f=1&nofb=1&ipt=a8ca1c611878925024fc134526698e3eb4cddf2dcf414253365c37e85112f708'
                        },
                        'fields': [
                            {
                                'name': 'Job Family',
                                'value': f'{jobFamily}',
                            },
                            {
                                'name': 'Job Role',
                                'value': f'{jobRole}'
                            },
                            {
                                'name': 'Category',
                                'value': f'{category}'
                            },
                            {
                                'name': 'Location',
                                'value': f':flag_{country.lower()}: {location}',
                            }, {
                                'name': 'Updated At',
                                'value': f'<t:{updatedDate}:f> | <t:{updatedDate}:R>'
                            }
                        ],
                        'color': int('FF9900', 16),
                        'timestamp': datetime.datetime.now().isoformat(),
                        'footer': {
                            'text': 'BigTech Internship Monitoring | by wiestju'
                        }
                    }
                ]
            }

            company = 'amazon'
            if is_new_job(company, jobId):
                if send_webhook(company, payload):
                    new_jobs_count += 1
                    logger.info(f"New Amazon job posted: {title} ({jobId})")
        except Exception as e:
            logger.error(f"Error processing Amazon job: {e}")
            continue
    
    logger.info(f"Amazon: Found {new_jobs_count} new jobs")
    return new_jobs_count