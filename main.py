import utils.job_storage
from jobs.amazon import getJobsAmazon
from jobs.microsoft import getJobsMicrosoft
from jobs.facebook import getJobsFacebook

def main():

    print("Getting all Jobs from Amazon...")
    getJobsAmazon()
    print("Getting all Jobs from Microsoft...")
    getJobsMicrosoft()
    print("Getting all Jobs from Facebook...")
    getJobsFacebook()
    print("Updating Job Storage File...")
    utils.job_storage.update_job_storage()
    print("Task ran successfully.")

if __name__ == "__main__":
    main()