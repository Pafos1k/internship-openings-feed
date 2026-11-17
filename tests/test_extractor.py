from services.extractor import DeterministicExtractor

extractor = DeterministicExtractor()

def test_salary_formats():
    assert extractor.extract("Pay is $45.75 - $50/hour.")['pay_range'] == "$45.75 - $50/hour"
    assert extractor.extract("Compensation: USD 30 to USD 40 per hour.")['pay_range'] == "USD 30 to USD 40 per hour"
    assert extractor.extract("The expected hourly rate is 20 USD – 71 USD.")['pay_range'] == "20 USD – 71 USD"

def test_duration_and_seasons():
    result = extractor.extract("This is a 12-week Summer 2027 internship.")
    assert result["term"] == "12-week" and result["season"] == "Summer 2027"
    assert extractor.extract("Internship opportunity.", "Research Intern - Fall 2026")["season"] == "Fall 2026"

def test_work_modes():
    assert extractor.extract("This is a fully remote role.")['work_mode'] == "remote"
    assert extractor.extract("This is a hybrid position with three days in the office.")['work_mode'] == "hybrid"
    assert extractor.extract("This position is on-site in San Mateo.")['work_mode'] == "on-site"

def test_location_and_incidental_in_person_language_do_not_imply_on_site():
    assert extractor.extract("Located in Toronto. Interviews may be conducted in person.")['work_mode'] == ""

def test_missing_and_ambiguous_information_stays_empty():
    result = extractor.extract("Join our engineering team and learn from mentors.", "Engineering Intern")
    assert result["term"] == result["season"] == result["pay_range"] == result["work_mode"] == ""
    assert result["category"] == "other"

def test_categories():
    assert extractor.extract("Build APIs", "Backend Software Intern")["category"] == "backend"
    assert extractor.extract("Train models", "Machine Learning Intern")["category"] == "ML/AI"

def test_category_regressions_prioritize_specific_title_language():
    assert extractor.extract("Includes quantitative performance analysis.", "AI Software Intern")["category"] == "ML/AI"
    assert extractor.extract("Follow all security policies.", "Hardware Intern - AI HW & SoC")["category"] == "hardware"
    assert extractor.extract("Work on secure systems and hardware.", "NVIDIA 2027 Internships: Systems Software Engineering")["category"] == "infrastructure"
    assert extractor.extract("Security and hardware knowledge helpful.", "Quantitative Trading Research Intern")["category"] == "quant"
