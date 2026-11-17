import os

STRING_API_URL = "https://request.usestring.ai/v1/fetch"
STRING_WEB_ACCESS_API_KEY = os.getenv("STRING_WEB_ACCESS_API_KEY", "")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))

SOURCES = {
    # Greenhouse public board (the board URL is also the official careers source).
    "Tenstorrent": "https://job-boards.greenhouse.io/tenstorrentuniversity/",
    # Workday-hosted official careers search page; no Greenhouse/Lever dependency.
    "NVIDIA": "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite?q=intern",
}

REQUIRED_ENV = ("STRING_WEB_ACCESS_API_KEY",)
