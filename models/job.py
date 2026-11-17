from dataclasses import asdict, dataclass

ALLOWED_CATEGORIES = {"backend", "frontend", "full-stack", "mobile", "ML/AI", "data", "infrastructure", "security", "quant", "hardware", "other"}

@dataclass(frozen=True)
class Job:
    company: str = ""
    role: str = ""
    location: str = ""
    date_posted: str = ""
    apply_link: str = ""
    source_job_id: str = ""
    category: str = "other"
    term: str = ""
    season: str = ""
    pay_range: str = ""
    work_mode: str = ""

    def to_dict(self): return asdict(self)

    def validate(self):
        if self.category not in ALLOWED_CATEGORIES: raise ValueError(f"invalid category: {self.category}")
        if self.work_mode not in {"", "remote", "hybrid", "on-site"}: raise ValueError(f"invalid work mode: {self.work_mode}")
        return self
