"""
Job storage module for tracking known jobs using GitHub API.
Manages job IDs across multiple companies to detect new postings.
"""
import requests
import json
import base64
import logging
from typing import Dict, List, Optional

from config import GITHUB_STORAGE_URL, GITHUB_TOKEN, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class JobStorage:
    """Manages job storage using GitHub API."""
    
    def __init__(self):
        self.content: Dict[str, List[str]] = {}
        self.old_content: Dict[str, List[str]] = {}
        self.sha: Optional[str] = None
        self.loaded = False
    
    def load(self) -> bool:
        """Load job data from GitHub repository.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            r = requests.get(
                GITHUB_STORAGE_URL,
                headers={
                    'Authorization': f'Bearer {GITHUB_TOKEN}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                timeout=REQUEST_TIMEOUT
            )
            r.raise_for_status()
            
            response_data = r.json()
            content_str = base64.b64decode(response_data['content'].encode()).decode()
            self.content = json.loads(content_str)
            self.old_content = json.loads(content_str)
            self.sha = response_data['sha']
            self.loaded = True
            
            logger.info(f"Loaded job storage from GitHub (SHA: {self.sha[:7]})")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to load job storage from GitHub: {e}")
            return False
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse job storage data: {e}")
            return False
    
    def is_new_job(self, company: str, job_id: str) -> bool:
        """Check if a job is new and add it to storage.
        
        Args:
            company: Company identifier (e.g., 'amazon', 'microsoft')
            job_id: Unique job identifier
            
        Returns:
            True if job is new, False if already exists.
        """
        if not self.loaded:
            logger.warning("Job storage not loaded, attempting to load now")
            if not self.load():
                logger.error("Cannot check if job is new - storage not loaded")
                return False
        
        if company not in self.content:
            self.content[company] = []
        
        if job_id in self.content[company]:
            return False
        
        self.content[company].append(job_id)
        logger.debug(f"Marked {company} job {job_id} as new")
        return True
    
    def has_changes(self) -> bool:
        """Check if there are any changes compared to original content.
        
        Returns:
            True if there are changes, False otherwise.
        """
        if not self.loaded:
            return False
        
        for company in self.content:
            if company not in self.old_content:
                return True
            for job_id in self.content[company]:
                if job_id not in self.old_content[company]:
                    return True
        return False
    
    def save(self) -> bool:
        """Save updated job data to GitHub repository.
        
        Returns:
            True if successful or no changes, False if error occurred.
        """
        if not self.loaded:
            logger.error("Cannot save - storage not loaded")
            return False
        
        if not self.has_changes():
            logger.info("No changes to save")
            return True
        
        try:
            content_json = json.dumps(self.content, indent=2)
            content_b64 = base64.b64encode(content_json.encode()).decode()
            
            r = requests.put(
                GITHUB_STORAGE_URL,
                headers={
                    'Authorization': f'Bearer {GITHUB_TOKEN}',
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28',
                },
                json={
                    'message': 'Daily data update',
                    'committer': {
                        'name': 'Auto Data Updater | by wiestju',
                        'email': 'b267a@protonmail.com'
                    },
                    'content': content_b64,
                    'sha': self.sha
                },
                timeout=REQUEST_TIMEOUT
            )
            r.raise_for_status()
            
            logger.info("Successfully saved job storage to GitHub")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to save job storage to GitHub: {e}")
            return False

# Global storage instance
_storage = JobStorage()

def load_job_storage() -> bool:
    """Load job storage from GitHub. Must be called before other functions."""
    return _storage.load()

def is_new_job(company: str, job_id: str) -> bool:
    """Check if a job is new."""
    return _storage.is_new_job(company, job_id)

def update_job_storage() -> bool:
    """Save updated job storage to GitHub."""
    return _storage.save()
