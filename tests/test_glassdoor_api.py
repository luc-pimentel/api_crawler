import pytest
from api_crawler import Glassdoor
from bs4 import BeautifulSoup


def test_search():
    page_source = Glassdoor().search('Data Analyst', days_ago=7)
    soup = BeautifulSoup(page_source, 'html.parser')
    assert isinstance(soup, BeautifulSoup), "Response is not a BeautifulSoup object"


def test_get_job_postings_data():
    glassdoor_api = Glassdoor()
    n_listings = 5
    job_posting_data = glassdoor_api.get_job_postings_data('Data Analyst', n_listings=n_listings, days_ago=7)
    assert isinstance(job_posting_data, list), "Job posting data is not a list"
    assert len(job_posting_data) == n_listings, f"Job posting data list is not of length {n_listings}"
    for job in job_posting_data:
        assert isinstance(job, dict), "Job posting is not a dictionary"

        ## NOTE: If any part of the scraping function fails to retrieve the job posting data, it will inevitably return None in the dict, thus failing the test below
        assert all(job.get(key) is not None for key in ['title', 'company', 'location', 'snippet', 'salary', 'date', 'link']), f"Job posting has None values for required keys: {job}"



def test_get_full_description():
    url = "https://www.glassdoor.com/job-listing/junior-data-engineer-mccoy-federal-credit-union-JV_IC1154247_KO0,20_KE21,47.htm?jl=1009330887225&cs=1_d858c383&s=58&t=SR&pos=101"
    glassdoor_api = Glassdoor()
    full_description = glassdoor_api._get_job_posting_full_description(url)
    description  = """Come join the McCoy Federal Credit Union team, a Credit Union that CARES about the communities we serve!\nPlease Note: This is an in-person position located in Orlando Florida, relocation expenses are not provided.\nAre you passionate about data and eager to start your career in data engineering? McCoy Federal Credit Union is looking for a talented and motivated Junior Data Engineer to join our Business Intelligence team!\nFull-time team members get health insurance, dental insurance, life insurance and long-term disability insurance for zero premium for individual coverage. We offer a 401k plan with a matching contribution, paid holidays, PTO time and a convenient work schedule.\nWhat will you do?\nBuild & Maintain Data Pipelines: Work with the Assistant VP of Business Intelligence to design and maintain reliable data pipelines for consistent data ingestion and processing.\nOptimize Data Infrastructure: Identify and implement improvements to enhance performance and scalability.\nEnsure Data Quality: Adhere to data governance policies to maintain data integrity and security.\nDevelop ETL Processes: Collaborate with others to create efficient ETL processes for data integration and transformation.\nSupport Cross-Functional Teams: Understand data requirements and implement solutions that meet business needs.\nMonitor & Troubleshoot: Proactively identify and resolve issues to ensure data availability and reliability.\nInnovate: Assist in evaluating and selecting new tools and technologies to enhance our data management capabilities.\nSupport Analytics: Provide clean, well-structured data to support analytics and reporting initiatives\nOur Junior Data Engineers work in person at our office located at 1900 McCoy Road, Orlando Fl. 32809\nWhat are We Looking For?\nEducation: Bachelor's degree in computer science, engineering, related field, or comparable work experience. Relevant certifications are a plus.\nSkills & Experience:\nKnowledge of data modeling, database design, and data warehousing concepts.\nExperience with cloud platforms (AWS, Azure, Google Cloud) is preferred.\nProficiency in SQL and scripting languages (Python, Java).\nFamiliarity with data integration tools (Apache Kafka, Apache NiFi, Talend) is a plus.\nStrong analytical, problem-solving, and communication skills.\nAbility to work effectively in a collaborative, team-oriented environment.\nAttitude: A proactive learner who stays current with industry trends and best practices in data engineering.\n If you're ready to kickstart your career in data engineering and make a meaningful impact, we want to hear from you! Apply now and become a vital part of McCoy Federal Credit Union's mission to deliver exceptional financial services."""
    
    assert full_description == description