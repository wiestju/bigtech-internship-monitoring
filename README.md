# BigTech Internship Monitoring 🔍
*by wiestju*

Automated monitoring system for internship positions at major tech companies. Fetches new job postings and sends Discord notifications via webhooks.

## 🏢 Supported Companies

The system currently monitors internships from:

| Company | API Type | Status |
|---------|----------|--------|
| **Amazon** | JSON REST API | ✅ Active |
| **Microsoft** | JSON REST API | ✅ Active |
| **Meta/Facebook** | GraphQL API | ✅ Active |
| Google | HTML Scraping | 🚧 Planned |
| Apple | HTML Scraping | 🚧 Planned |

## 🚀 Features

- ✅ Automated job scraping from multiple sources
- ✅ Discord webhook notifications with rich embeds
- ✅ Duplicate detection using GitHub storage
- ✅ Comprehensive error handling and logging
- ✅ Configurable via environment variables
- ✅ Request timeouts and retry logic

## 📋 Requirements

- Python 3.8+
- GitHub repository for job storage
- Discord webhook URLs (one per company)
- GitHub Personal Access Token

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wiestju/bigtech-internship-monitoring.git
   cd bigtech-internship-monitoring
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Create a `.env` file in the root directory:
   ```env
   # GitHub API Token (needs repo write access)
   GH_TOKEN=your_github_personal_access_token
   
   # Discord Webhook URLs (JSON format)
   WEBHOOK_URLS_JSON={"amazon":"https://discord.com/api/webhooks/...","microsoft":"https://discord.com/api/webhooks/...","facebook":"https://discord.com/api/webhooks/..."}
   ```

## 🎯 Usage

### Run manually:
```bash
python main.py
```

### Run with logging output:
```bash
python main.py 2>&1 | tee output.log
```

### Automated execution (recommended):

Set up a scheduled task or cron job to run the script periodically:

**Windows Task Scheduler:**
```
Program: C:\path\to\venv\Scripts\python.exe
Arguments: C:\path\to\main.py
```

**Linux/macOS Cron:**
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/project && /path/to/venv/bin/python main.py
```

**GitHub Actions (example):**
```yaml
name: Check Internships
on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          WEBHOOK_URLS_JSON: ${{ secrets.WEBHOOK_URLS_JSON }}
```

## 📁 Project Structure

```
bigtech-internship-monitoring/
├── main.py                 # Main entry point
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── jobs/                  # Job scraper modules
│   ├── __init__.py
│   ├── amazon.py         # Amazon internships scraper
│   ├── microsoft.py      # Microsoft internships scraper
│   └── facebook.py       # Meta/Facebook internships scraper
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── job_storage.py    # GitHub storage management
│   └── webhook.py        # Discord webhook sender
└── data/
    └── known_jobs.json   # Tracked job IDs (managed by GitHub API)
```

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use environment variables or secrets management for sensitive data
- Limit GitHub token permissions to repository scope only
- Regularly rotate your tokens and webhook URLs

## 🐛 Troubleshooting

**"Failed to load job storage"**
- Verify your `GH_TOKEN` has write access to the repository
- Check the GitHub repository URL in `config.py`

**"No webhook URL configured"**
- Ensure `WEBHOOK_URLS_JSON` contains all company keys: `amazon`, `microsoft`, `facebook`
- Verify the JSON format is valid

**"Request timeout"**
- Increase `REQUEST_TIMEOUT` in `config.py` (default: 30 seconds)
- Check your internet connection

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📧 Contact

Created by **wiestju** - [GitHub Profile](https://github.com/wiestju)

---

*Happy internship hunting! 🎓💼*