import requests
import os
import json
import base64
import copy

from config import GITHUB_STORAGE_URL

GITHUB_TOKEN = os.getenv('GH_TOKEN')

r = requests.get(
        f'{GITHUB_STORAGE_URL}',
        headers={
            'Authorization': f'Bearer {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
)

content = json.loads(base64.b64decode(r.json()['content'].encode()).decode())
old_content = json.loads(base64.b64decode(r.json()['content'].encode()).decode())

def is_new_job(company, jobId):

    if company not in content:
        content[company] = [jobId]
    else:
        if jobId in content[company]:
            return False

    content[company].append(jobId)

    return True

def check_if_lists_are_equal():
    for company in content:
        for id_ in content[company]:
            if id_ not in old_content[company]:
                return False
    return True

def update_job_storage():
    if check_if_lists_are_equal():
        return False

    f = requests.put(
        f'{GITHUB_STORAGE_URL}',
        headers={
            'Authorization': f'Bearer {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }, json={
            'message': 'Daily data update',
            'committer': {
                'name': 'Auto Data Updater | by wiestju',
                'email': 'b267a@protonmail.com'
            },
            'content': base64.b64encode(
                json.dumps(
                    content
                ).encode()
            ).decode(),
            'sha': r.json()['sha']
        }
    )

    return True
