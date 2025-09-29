import utils.job_storage
from jobs.amazon import getJobsAmazon
from jobs.microsoft import getJobsMicrosoft
from jobs.facebook import getJobsFacebook

def main():

    getJobsAmazon()
    getJobsMicrosoft()
    getJobsFacebook()
    utils.job_storage.update_job_storage()

if __name__ == "__main__":
    main()