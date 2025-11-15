"""Google internship job scraper."""
import datetime
import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup
from utils.webhook import send_webhook
from utils.job_storage import is_new_job
from config import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def getJobsGoogle() -> Optional[int]:
    """Fetch internship jobs from Google careers page.
    
    Google uses a Single Page Application that loads jobs dynamically.
    We scrape the initial HTML to extract job IDs and titles.
    Google shows max 20 jobs per page, so we need to paginate.
    
    Returns:
        Number of new jobs found, or None if error occurred.
    """
    all_unique_jobs = []
    seen = set()
    page = 1
    max_pages = 10  # Safety limit to avoid infinite loops
    
    try:
        url = 'https://www.google.com/about/careers/applications/jobs/results/'
        base_params = {
            'company': ['Fitbit', 'Google', 'YouTube'],
            'employment_type': 'INTERN'
        }
        
        while page <= max_pages:
            params = base_params.copy()
            if page > 1:
                params['page'] = str(page)
            
            try:
                r = requests.get(
                    url,
                    params=params,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    timeout=REQUEST_TIMEOUT
                )
                r.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Failed to fetch Google jobs page {page}: {e}")
                if page == 1:
                    return None  # First page failed
                else:
                    break  # Continue with jobs found so far
            
            html = r.text
            
            # Extract job IDs and slugs from the HTML
            # Pattern: jobs/results/<job_id>-<job-slug>
            job_pattern = r'jobs/results/(\d+)-([^?"\'\s]+)'
            matches = re.findall(job_pattern, html)
            
            if not matches:
                logger.info(f"No more jobs found on page {page}")
                break
            
            # Track jobs found on this page
            page_jobs_count = 0
            for job_id, slug in matches:
                if job_id not in seen:
                    seen.add(job_id)
                    all_unique_jobs.append((job_id, slug))
                    page_jobs_count += 1
            
            logger.info(f"Page {page}: Found {page_jobs_count} new unique jobs ({len(matches)} total matches)")
            
            # If we found fewer than 20 jobs, we've likely reached the end
            if len(matches) < 20:
                logger.info(f"Reached last page (page {page})")
                break
            
            # If no new unique jobs were found on this page, stop
            if page_jobs_count == 0:
                logger.info(f"No new unique jobs on page {page}, stopping pagination")
                break
            
            page += 1
        
        logger.info(f"Found {len(all_unique_jobs)} total unique jobs across {page} page(s)")
        
        if not all_unique_jobs:
            logger.warning("No job patterns found in Google careers pages")
            return 0
        
    except Exception as e:
        logger.error(f"Failed to parse Google jobs pages: {e}")
        return None
    
    new_jobs_count = 0
    for job_id, job_slug in all_unique_jobs:
        try:
            # Convert slug to title
            title = job_slug.replace('-', ' ').title()
            url = f'https://www.google.com/about/careers/applications/jobs/results/{job_id}'
            
            payload = {
                'username': 'BigTech Internship Monitoring',
                'avatar_url': None,
                'embeds': [
                    {
                        'title': f'New Internship: {title}',
                        'url': url,
                        'thumbnail': {
                            'url': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%2Fid%2FOIP.KOKzZsAVKlqyZLa1L-ICYAHaHa%3Fpid%3DApi&f=1'
                        },
                        'fields': [
                            {
                                'name': 'Job ID',
                                'value': job_id
                            }
                        ],
                        'color': int('4285F4', 16),  # Google Blue
                        'timestamp': datetime.datetime.now().isoformat(),
                        'footer': {
                            'text': 'BigTech Internship Monitoring | by wiestju'
                        }
                    }
                ]
            }

            company = 'google'
            if is_new_job(company, job_id):
                if send_webhook(company, payload):
                    new_jobs_count += 1
                    logger.info(f"New Google job posted: {title} ({job_id})")
        except Exception as e:
            logger.error(f"Error processing Google job {job_id}: {e}")
            continue
    
    logger.info(f"Google: Found {new_jobs_count} new jobs")
    return new_jobs_count
