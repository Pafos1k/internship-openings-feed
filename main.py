import json, logging, os
from collections import Counter
from config import *
from fetchers.greenhouse import GreenhouseFetcher
from fetchers.workday import WorkdayFetcher
from services.string_client import StringClient
from services.normalizer import normalize, deduplicate
from services.extractor import DeterministicExtractor, ExtractionError

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main():
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing: raise SystemExit("Missing required environment variable(s): " + ", ".join(missing))
    client, extractor, jobs = StringClient(STRING_WEB_ACCESS_API_KEY, timeout=REQUEST_TIMEOUT), DeterministicExtractor(), []
    fetchers = [GreenhouseFetcher(client, "Tenstorrent", SOURCES["Tenstorrent"]), WorkdayFetcher(client, "NVIDIA", SOURCES["NVIDIA"])]
    for fetcher in fetchers:
        try:
            raw_jobs = fetcher.fetch(); logging.info("%s: fetched %d openings", fetcher.company, len(raw_jobs))
            for raw in raw_jobs:
                try: jobs.append(normalize(raw, extractor.extract(raw.get("description", ""), raw.get("role", ""))))
                except (ExtractionError, ValueError) as exc: logging.warning("%s extraction skipped: %s", raw.get("role", "unknown"), exc); jobs.append(normalize(raw))
        except Exception as exc: logging.error("%s source failed: %s", fetcher.company, exc)
    jobs = deduplicate(jobs)
    os.makedirs("output", exist_ok=True)
    with open("output/jobs.json", "w") as f: json.dump([job.to_dict() for job in jobs], f, indent=2)
    print(f"Fetched {len(jobs)} openings")
    counts = Counter(job.company for job in jobs)
    for company in sorted(counts): print(f"{company}: {counts[company]} openings")
    print("Company | Role | Location | Category | Term | Compensation | Work mode")
    for j in jobs: print(f"{j.company} | {j.role} | {j.location} | {j.category} | {j.term} | {j.pay_range} | {j.work_mode}")
    fields = ("company", "role", "location", "date_posted", "apply_link", "source_job_id", "category", "term", "season", "pay_range", "work_mode")
    missing = {field: sum(not getattr(job, field) for job in jobs) for field in fields}
    print("Missing fields: " + ", ".join(f"{field}={count}" for field, count in missing.items()))

if __name__ == "__main__": main()
