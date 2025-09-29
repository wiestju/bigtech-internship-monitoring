import requests
import datetime
import json
from utils.webhook import send_webhook
from utils.job_storage import is_new_job

def getJobsFacebook():
    r = requests.post(
        f'https://www.metacareers.com/graphql',
        data={
            "lsd": "AdFL9XlD5sA",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "CareersJobSearchResultsDataQuery",
            "variables": json.dumps({
                "search_input": {
                    "q": None,
                    "divisions": [],
                    "offices": [],
                    "roles": [],
                    "leadership_levels": [],
                    "saved_jobs": [],
                    "saved_searches": [],
                    "sub_teams": [],
                    "teams": [
                        "University Grad - Business",
                        "University Grad - Engineering, Tech & Design",
                        # "University Grad - PhD & Postdoc"
                    ],
                    "is_leadership": False,
                    "is_remote_only": False,
                    "sort_by_new": False,
                    "results_per_page": None
                }
            }),
            "doc_id": "29615178951461218"
        }, headers={
            'x-asbd-id': '359341',
            'x-fb-friendly-name': 'CareersJobSearchResultsDataQuery',
            'x-fb-lsd': 'AdFL9XlD5sA',
        }
    )

    jobs = r.json()['data']['job_search_with_featured_jobs']['all_jobs']

    for job in jobs:
        title = job['title']
        jobId = job['id']
        location = '\n'.join(job['locations'])
        topics = '; '.join(job['sub_teams'])
        teams = '; '.join(job['teams'])
        url = 'https://www.metacareers.com/jobs/' + jobId

        payload = {
            # 'content': '--',
            'username': 'BigTech Internship Monitoring',
            'avatar_url': None,
            'embeds': [
                {
                    'title': f'New Internship: {title}',
                    'url': url,
                    'thumbnail': {
                        'url': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%2Fid%2FOIP.mzp7qjNYxT5a1WBZG52e0AHaHI%3Fpid%3DApi&f=1&ipt=fda0ef3d260a3b9ae177d37c8589d107bf5dfd599d5077c87def5e76cf9b7e95&ipo=images'
                    },
                    'fields': [
                        {
                            'name': 'Topics',
                            'value': f'{topics}',
                        },
                        {
                            'name': 'Teams',
                            'value': f'{teams}'
                        },
                        {
                            'name': 'Locations',
                            'value': f'{location}',
                        }
                    ],
                    'color': int('0668E1', 16),
                    'timestamp': datetime.datetime.now().isoformat(),
                    'footer': {
                        'text': 'BigTech Internship Monitoring | by wiestju'
                    }
                }
            ]
        }

        company = 'facebook'
        if is_new_job(company, jobId):
            send_webhook(company, payload)