import json
import re
from .base import BaseFetcher

class WorkdayFetcher(BaseFetcher):
    US_STATES = {"CA": "California", "TX": "Texas", "WA": "Washington", "NY": "New York", "MA": "Massachusetts", "CO": "Colorado"}

    @classmethod
    def normalize_location(cls, value):
        value = re.sub(r"\s+", " ", (value or "")).strip()
        us = re.fullmatch(r"US,\s*([A-Z]{2}),\s*(.+)", value)
        if us: return f"{us.group(2)}, {cls.US_STATES.get(us.group(1), us.group(1))}, United States"
        country_first = re.fullmatch(r"(Singapore|China|Switzerland|Japan|Taiwan),\s*(.+)", value)
        if country_first: return f"{country_first.group(2)}, {country_first.group(1)}"
        return value

    @classmethod
    def parse_job_metadata(cls, description):
        match = re.search(r"```json\s*(\{.*?\})\s*```", description or "", re.S | re.I)
        if not match: return {}
        try: data = json.loads(match.group(1))
        except json.JSONDecodeError: return {}
        locations = data.get("jobLocation", [])
        if isinstance(locations, dict): locations = [locations]
        normalized = []
        for item in locations:
            locality = ((item or {}).get("address") or {}).get("addressLocality", "")
            if locality: normalized.append(cls.normalize_location(locality))
        identifier = data.get("identifier") or {}
        return {"location": "; ".join(dict.fromkeys(normalized)), "date_posted": str(data.get("datePosted", "")), "source_job_id": str(identifier.get("value", ""))}

    @staticmethod
    def parse_listings(page, company):
        jobs = []
        pattern = r'\[([^\]]+)\]\((https?://[^)]+/job/[^)]+)\)'
        for title, link in re.findall(pattern, page, re.I):
            title = re.sub(r'<[^>]+>', '', title).strip()
            if not re.search(r'\bintern(?:ship)?s?\b', title, re.I):
                continue
            match = re.search(r'_(JR[\w-]+)(?:\?|$)', link, re.I)
            source_id = match.group(1) if match else link.split('?', 1)[0].rstrip('/').rsplit('/', 1)[-1]
            jobs.append({"company": company, "role": title, "location": "", "apply_link": link, "source_job_id": source_id})
        return jobs

    def fetch(self):
        page = str(self.client.fetch(self.board_url, execute_js=True))
        jobs = self.parse_listings(page, self.company)
        for job in jobs:
            # The search page needs browser rendering, but Workday job detail URLs
            # expose their structured job data without it. Avoid five-credit
            # browser fetches when a normal String fetch returns the same source.
            job["description"] = str(self.client.fetch(job["apply_link"]))
            metadata = self.parse_job_metadata(job["description"])
            for field in ("location", "date_posted"):
                if metadata.get(field): job[field] = metadata[field]
            if metadata.get("source_job_id") and metadata["source_job_id"].upper() == job["source_job_id"].upper():
                job["source_job_id"] = metadata["source_job_id"]
        return jobs
