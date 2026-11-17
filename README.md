# Internship Openings Feed

A small Python CLI that retrieves public internship career pages through authenticated String Web Access, normalizes listings from Tenstorrent University Jobs (Greenhouse) and NVIDIA (Workday), deterministically extracts description fields with Python, and writes `output/jobs.json` plus a readable table.

## Setup

```bash
unzip internship-feed.zip
cd internship-feed
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export STRING_WEB_ACCESS_API_KEY="your_key"
python3 main.py
```

Set `STRING_WEB_ACCESS_API_KEY` in `.env` or the shell. The integration uses `POST https://request.usestring.ai/v1/fetch`, sends `Authorization: Bearer <key>`, and reads page content from the documented `data` field. No credentials are logged. Extraction is fully deterministic and has no external LLM dependency.

## Architecture

`fetchers/` contains source-specific discovery, `services/string_client.py` owns HTTP/retries, `services/normalizer.py` owns validation/classification/deduplication, and `services/extractor.py` contains a modular deterministic extractor. A failed source is logged and does not prevent other sources from completing.

## Tests

Run `pytest -q`. Tests use fakes and saved values; no live API calls are required.

## Limitations

Career pages change markup, so source parsers may need maintenance. The current implementation does not yet paginate or compare runs. Empty fields remain empty; the extractor never invents compensation, term, season, or work mode.
