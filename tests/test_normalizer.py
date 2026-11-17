from models.job import Job
from services.normalizer import classify, deduplicate, normalize

def test_classification_and_missing_values():
    assert classify("Software Engineering Intern, Backend") == "backend"
    job = normalize({"company":"Acme", "role":"Design Intern", "source_job_id":"1"})
    assert job.pay_range == "" and job.category == "other"

def test_duplicate_detection():
    a = Job(company="A", source_job_id="1")
    assert len(deduplicate([a, a, Job(company="A", source_job_id="2")])) == 2
