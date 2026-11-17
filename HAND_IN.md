# Hand-in Notes

## Built

Implemented a modular CLI with authenticated String Web Access, Tenstorrent Greenhouse and NVIDIA Workday fetchers, deterministic Python extraction, normalized validation, deduplication, JSON output, logging, README, tests, and MIT license.

## Checks

Run `pytest -q` before submission. The checked-in tests cover salary, duration, season, work-mode, category, missing fields, duplicates, and explicit API failures without live credentials.

## Known gaps

Live execution still requires both API keys. Career-page HTML can change; pagination and run-to-run change detection are not included.

## Failure case

The test `test_api_failure_is_explicit` simulates a failed String request. The client raises `StringWebAccessError` after the configured retries so the caller can log the source failure instead of silently returning fake data.

## Manual review example

Deterministic extraction uses conservative regular expressions and keywords. Descriptions without explicit pay, duration, season, or work arrangement leave those fields empty rather than inferring them.
