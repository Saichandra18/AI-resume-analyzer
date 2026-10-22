"""Experience headers come in several layouts; all must parse the same way."""

from app.section_parser import parse_experience_entries


def _job(*header):
    return parse_experience_entries(list(header) + ["\u2022 Did the work."])[0]


def test_title_line_then_company_location_dates_line():
    job = _job("Freelance LLM Trainer", "Outlier | Remote, India | Sep 2023 \u2013 Present")

    assert job["title"] == "Freelance LLM Trainer"
    assert job["company"] == "Outlier"
    assert job["location"] == "Remote, India"
    assert job["dates"] == "Sep 2023 \u2013 Present"


def test_title_dash_company_with_glued_date_then_location_line():
    job = _job("Freelance LLM Trainer \u2013 OutlierSep 2023 \u2013 Present", "Remote, India")

    assert job["title"] == "Freelance LLM Trainer"
    assert job["company"] == "Outlier"
    assert job["location"] == "Remote, India"
    assert job["dates"] == "Sep 2023 \u2013 Present"


def test_everything_on_one_pipe_separated_line():
    job = _job("Senior Engineer | Acme Corp | Jan 2020 \u2013 Present")

    assert (job["title"], job["company"], job["dates"]) == (
        "Senior Engineer", "Acme Corp", "Jan 2020 \u2013 Present",
    )
    assert job["location"] == ""


def test_dates_on_their_own_line():
    job = _job("Data Analyst \u2013 Acme", "Jan 2022 \u2013 Present")

    assert job["title"] == "Data Analyst"
    assert job["company"] == "Acme"
    assert job["dates"] == "Jan 2022 \u2013 Present"


def test_company_without_location():
    job = _job("Trainer", "Outlier | Sep 2023 \u2013 Present")

    assert job["company"] == "Outlier"
    assert job["location"] == ""
    assert job["dates"] == "Sep 2023 \u2013 Present"


def test_two_jobs_with_two_line_headers_stay_separate():
    jobs = parse_experience_entries([
        "Data Analyst",
        "Acme Corp | Pune, India | Jan 2022 \u2013 Present",
        "\u2022 Built dashboards.",
        "Intern",
        "Beta Labs | Remote | Jun 2021 \u2013 Dec 2021",
        "\u2022 Cleaned data.",
    ])

    assert [(j["title"], j["company"], j["location"]) for j in jobs] == [
        ("Data Analyst", "Acme Corp", "Pune, India"),
        ("Intern", "Beta Labs", "Remote"),
    ]
    assert jobs[1]["dates"] == "Jun 2021 \u2013 Dec 2021"
