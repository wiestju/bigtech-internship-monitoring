import datetime

import requests
from utils.webhook import send_webhook
from utils.job_storage import is_new_job

def getJobsMicrosoft():
    r = requests.get(
        f'https://gcsservices.careers.microsoft.com/search/api/v1/search',
        params={
            'et': 'Internship',
            'l': 'en_us',
            'pg': '1',
            'pgSz': '100',
            'o': 'Relevance',
            'flt': 'true',
        }
    )

    jobs = r.json()['operationResult']['result']['jobs']

    for job in jobs:
        title = job['title']
        postingDate = datetime.datetime.fromisoformat(job['postingDate'])
        location = job['properties']['primaryLocation']
        profession = job['properties']['profession']
        discipline = job['properties']['discipline']
        educationLevel = job['properties']['educationLevel']
        jobId = job['jobId']

        url = 'https://jobs.careers.microsoft.com/global/en/job/' + jobId

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
            send_webhook(company, payload)