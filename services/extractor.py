import re

from models.job import ALLOWED_CATEGORIES


class ExtractionError(ValueError):
    pass


def _first(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text or "", re.I)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" .,:;()")
    return ""


def extract_term(text):
    return _first([r"\b(\d+\s*(?:-|–|to)?\s*\d*\s*(?:weeks?|months?))\b", r"\b(full[- ]time\s+for\s+\d+\s+weeks?)\b"], text)


def extract_season(text):
    value = _first([r"\b((?:spring|summer|fall|autumn|winter)\s+20\d{2})\b", r"\b(20\d{2}\s+(?:spring|summer|fall|autumn|winter))\b"], text)
    return value.title() if value else ""


def extract_pay_range(text):
    patterns = [r"([\d,]+(?:\.\d+)?\s*USD\s*(?:-|–|to)\s*[\d,]+(?:\.\d+)?\s*USD(?:\s*(?:per hour|/\s*hour|hourly|per year|/\s*year|annually))?)", r"((?:US\$|\$)\s?[\d,]+(?:\.\d+)?\s*(?:-|–|to)\s*(?:US\$|\$)?\s?[\d,]+(?:\.\d+)?\s*(?:per hour|/\s*hour|hourly|per year|/\s*year|annually)?)", r"((?:US\$|\$)\s?[\d,]+(?:\.\d+)?\s*(?:per hour|/\s*hour|hourly|per year|/\s*year|annually))", r"((?:USD\s*)?[\d,]+(?:\.\d+)?\s*(?:-|–|to)\s*(?:USD\s*)?[\d,]+(?:\.\d+)?\s*(?:per hour|/\s*hour|hourly|per year|/\s*year|annually))"]
    return _first(patterns, text)


def extract_work_mode(text):
    lower = (text or "").lower()
    if re.search(r"\b(remote[- ]first|fully remote|100% remote|work remotely|remote (?:role|position)|position is remote)\b", lower): return "remote"
    if re.search(r"\b(hybrid (?:role|position|work|schedule|arrangement)|position is hybrid|work(?:ing)? in a hybrid|\d+ days? (?:per week )?(?:in|at) (?:the )?office)\b", lower): return "hybrid"
    if re.search(r"\b(on[- ]site (?:role|position|work)|onsite (?:role|position|work)|position is on[- ]site|work on[- ]site|required to work on[- ]site)\b", lower): return "on-site"
    return ""


def classify(role, description=""):
    title = (role or "").lower()
    title_rules = [
        (r"\b(quantitative (?:trading|research|researcher|developer)|quant (?:trader|research|researcher|developer))\b", "quant"),
        (r"\b(cybersecurity|cyber security|application security|information security|security engineer)\b", "security"),
        (r"\b(hardware|silicon|chip design|soc|asic|dft|circuit design|risc-v|cpu|physical design)\b", "hardware"),
        (r"\b(machine learning|deep learning|reinforcement learning|generative ai|artificial intelligence|ai software|ai engineering|ai intern|robotics)\b", "ML/AI"),
        (r"\b(full[- ]stack)\b", "full-stack"), (r"\b(front[- ]?end|ui engineer|web frontend)\b", "frontend"),
        (r"\b(back[- ]?end|server[- ]side)\b", "backend"), (r"\b(android|ios|mobile)\b", "mobile"),
        (r"\b(infrastructure|systems software|systems engineering|platform engineering|devops|site reliability|compiler|performance engineering|perf engineering|cloud)\b", "infrastructure"),
        (r"\b(data engineer|data science|analytics engineer)\b", "data"),
    ]
    for pattern, category in title_rules:
        if re.search(pattern, title): return category
    body = (description or "").lower()
    description_rules = [(r"\b(quantitative trading|quantitative research|algorithmic trading)\b", "quant"), (r"\b(cybersecurity|cyber security|application security|information security)\b", "security"), (r"\b(machine learning|deep learning|reinforcement learning|neural networks?)\b", "ML/AI"), (r"\b(front[- ]end development|react|vue\.js|angular)\b", "frontend"), (r"\b(back[- ]end development|server[- ]side development)\b", "backend"), (r"\b(mobile development|android development|ios development)\b", "mobile"), (r"\b(infrastructure engineering|systems engineering|site reliability|devops)\b", "infrastructure"), (r"\b(hardware design|silicon design|chip design|soc design|asic design)\b", "hardware")]
    for pattern, category in description_rules:
        if re.search(pattern, body): return category
    return "other"


class DeterministicExtractor:
    def extract(self, description, role=""):
        result = {"term": extract_term(description), "season": extract_season(f"{role} {description}"), "pay_range": extract_pay_range(description), "work_mode": extract_work_mode(description), "category": classify(role, description)}
        if result["category"] not in ALLOWED_CATEGORIES: raise ExtractionError("invalid category")
        return result
