from jobs.amazon import getJobsAmazon
from jobs.microsoft import getJobsMicrosoft
from jobs.facebook import getJobsFacebook

def main():
    getJobsAmazon()
    getJobsMicrosoft()
    getJobsFacebook()

if __name__ == "__main__":
    main()