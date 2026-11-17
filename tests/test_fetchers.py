from fetchers.greenhouse import GreenhouseFetcher
from fetchers.workday import WorkdayFetcher

def test_greenhouse_markdown_parser():
    page = "| [<br>AI Software Intern (Canada)<br>Toronto, Ontario, Canada<br>](https://job-boards.greenhouse.io/tenstorrentuniversity/jobs/5259347007) |"
    jobs = GreenhouseFetcher.parse_listings(page, "Tenstorrent", "unused")
    assert jobs == [{"company":"Tenstorrent", "role":"AI Software Intern (Canada)", "location":"Toronto, Ontario, Canada", "apply_link":"https://job-boards.greenhouse.io/tenstorrentuniversity/jobs/5259347007", "source_job_id":"5259347007"}]

def test_greenhouse_api_date_description_and_duplicate_locations():
    page = '''{"jobs":[{"id":5259347007,"title":"Systems Intern","absolute_url":"https://job-boards.greenhouse.io/x/jobs/5259347007","first_published":"2026-10-08T03:48:27-04:00","updated_at":"2026-10-09T09:02:19-04:00","location":{"name":"Toronto, Ontario, Canada; Toronto, Ontario, Canada; Vancouver, British Columbia, Canada"},"content":"&lt;p&gt;Explicit 12-week internship.&lt;/p&gt;"}]}'''
    jobs = GreenhouseFetcher.parse_api_response(page, "Tenstorrent")
    assert jobs[0]["date_posted"] == "2026-10-08"
    assert jobs[0]["location"] == "Toronto, Ontario, Canada; Vancouver, British Columbia, Canada"
    assert jobs[0]["description"] == "Explicit 12-week internship."

def test_workday_markdown_parser_and_false_positive():
    page = """### [Software Engineering Intern - 2027](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/China-Shanghai/Software-Engineering-Intern---2027_JR2026972?q=intern)
### [Director, International Tax](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA/Director_JR1?q=intern)"""
    jobs = WorkdayFetcher.parse_listings(page, "NVIDIA")
    assert len(jobs) == 1
    assert jobs[0]["source_job_id"] == "JR2026972"
    assert jobs[0]["location"] == ""

def test_workday_location_normalization_preserves_locality_names():
    assert WorkdayFetcher.normalize_location("US, CA, Santa Clara") == "Santa Clara, California, United States"
    assert WorkdayFetcher.normalize_location("Singapore, Pasir Panjang") == "Pasir Panjang, Singapore"

def test_workday_structured_metadata_preserves_date_id_and_multiple_locations():
    description = '''```json
{"jobLocation":[{"address":{"addressLocality":"US, CA, Santa Clara"}},{"address":{"addressLocality":"Singapore, Pasir Panjang"}}],"identifier":{"value":"JR123"},"datePosted":"2026-10-21"}
```'''
    assert WorkdayFetcher.parse_job_metadata(description) == {"location":"Santa Clara, California, United States; Pasir Panjang, Singapore", "date_posted":"2026-10-21", "source_job_id":"JR123"}
