import html
import json
import re
from .base import BaseFetcher

class GreenhouseFetcher(BaseFetcher):
    @staticmethod
    def deduplicate_locations(value):
        locations = [part.strip() for part in (value or "").split(";") if part.strip()]
        return "; ".join(dict.fromkeys(locations))

    @classmethod
    def parse_api_response(cls, page, company):
        try:
            payload = json.loads(page)
        except json.JSONDecodeError as exc:
            raise ValueError("Greenhouse API returned invalid JSON") from exc
        jobs = []
        for item in payload.get("jobs", []):
            title = str(item.get("title", "")).strip()
            if not re.search(r'\bintern(?:ship)?\b', title, re.I): continue
            if re.search(r'\b(business operations|program management|customer success|product intern)\b', title, re.I): continue
            raw_description = html.unescape(str(item.get("content", "")))
            description = re.sub(r"<[^>]+>", " ", raw_description)
            description = re.sub(r"\s+", " ", description).strip()
            first_published = str(item.get("first_published", ""))
            jobs.append({"company": company, "role": title, "location": cls.deduplicate_locations((item.get("location") or {}).get("name", "")), "date_posted": first_published[:10] if first_published else "", "apply_link": str(item.get("absolute_url", "")), "source_job_id": str(item.get("id", "")), "description": description})
        return jobs

    @staticmethod
    def parse_listings(page, company, board_url):
        jobs = []
        pattern = r'\[([^\]]+)\]\((https?://[^)]+/jobs/(\d+)[^)]*)\)'
        for label, link, job_id in re.findall(pattern, page, re.I):
            parts = [re.sub(r'<[^>]+>', '', part).strip() for part in re.split(r'<br\s*/?>', label, flags=re.I)]
            parts = [part for part in parts if part]
            if not parts or not re.search(r'\bintern(?:ship)?\b', parts[0], re.I):
                continue
            if re.search(r'\b(business operations|program management|customer success|product intern)\b', parts[0], re.I):
                continue
            jobs.append({"company": company, "role": parts[0], "location": parts[1] if len(parts) > 1 else "", "apply_link": link, "source_job_id": job_id})
        return jobs

    def fetch(self):
        token_match = re.search(r"job-boards\.greenhouse\.io/([^/?#]+)", self.board_url)
        if not token_match: raise ValueError(f"Cannot determine Greenhouse board token from {self.board_url}")
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{token_match.group(1)}/jobs?content=true"
        return self.parse_api_response(str(self.client.fetch(api_url)), self.company)
