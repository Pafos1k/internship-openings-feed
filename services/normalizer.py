from models.job import Job
from services.extractor import classify

def normalize(raw, extraction=None):
    raw, extraction = raw or {}, extraction or {}
    job = Job(company=str(raw.get("company", "")), role=str(raw.get("role", "")), location=str(raw.get("location", "")), date_posted=str(raw.get("date_posted", "")), apply_link=str(raw.get("apply_link", "")), source_job_id=str(raw.get("source_job_id", "")), category=extraction.get("category") or classify(raw.get("role", ""), raw.get("description", "")), term=extraction.get("term", ""), season=extraction.get("season", ""), pay_range=extraction.get("pay_range", ""), work_mode=extraction.get("work_mode", ""))
    return job.validate()

def deduplicate(jobs):
    seen, result = set(), []
    for job in jobs:
        key = (job.company, job.source_job_id)
        if key not in seen: seen.add(key); result.append(job)
    return result
