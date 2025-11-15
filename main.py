"""
BigTech Internship Monitoring - Main Script
Monitors internship postings from major tech companies and sends Discord notifications.
"""
import logging
import sys

from utils.job_storage import load_job_storage, update_job_storage
from jobs.amazon import getJobsAmazon
from jobs.microsoft import getJobsMicrosoft
from jobs.facebook import getJobsFacebook

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to fetch jobs from all companies and update storage."""
    logger.info("=" * 60)
    logger.info("BigTech Internship Monitoring - Starting")
    logger.info("=" * 60)
    
    # Load existing job storage
    logger.info("Loading job storage from GitHub...")
    if not load_job_storage():
        logger.error("Failed to load job storage. Exiting.")
        sys.exit(1)
    
    # Fetch jobs from all companies
    companies = [
        ("Amazon", getJobsAmazon),
        ("Microsoft", getJobsMicrosoft),
        ("Meta/Facebook", getJobsFacebook)
    ]
    
    total_new_jobs = 0
    failed_companies = []
    
    for company_name, fetch_func in companies:
        logger.info(f"Fetching jobs from {company_name}...")
        result = fetch_func()
        
        if result is None:
            logger.warning(f"Failed to fetch jobs from {company_name}")
            failed_companies.append(company_name)
        else:
            total_new_jobs += result
    
    # Update job storage
    logger.info("Updating job storage on GitHub...")
    if update_job_storage():
        logger.info("Job storage updated successfully")
    else:
        logger.warning("Job storage update failed or no changes")
    
    # Summary
    logger.info("=" * 60)
    logger.info(f"Task completed - Total new jobs: {total_new_jobs}")
    if failed_companies:
        logger.warning(f"Failed companies: {', '.join(failed_companies)}")
    logger.info("=" * 60)
    
    # Exit with error code if any company failed
    if failed_companies:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)