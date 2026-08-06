from pathlib import Path

from internship_digest.sources.simplify_parser import SimplifyTrackerParser


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "simplify_sample.md"


def load_fixture() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_parser_extracts_all_jobs() -> None:
    parser = SimplifyTrackerParser(source_name="simplify-summer-2027")

    jobs = parser.parse(load_fixture())

    assert len(jobs) == 3


def test_parser_carries_forward_repeated_company() -> None:
    parser = SimplifyTrackerParser(source_name="simplify-summer-2027")

    jobs = parser.parse(load_fixture())

    assert jobs[0].company == "TikTok"
    assert jobs[1].company == "TikTok"


def test_parser_prefers_employer_application_url() -> None:
    parser = SimplifyTrackerParser(source_name="simplify-summer-2027")

    jobs = parser.parse(load_fixture())

    assert str(jobs[0].url) == "https://careers.example.com/tiktok-swe"


def test_parser_assigns_categories() -> None:
    parser = SimplifyTrackerParser(source_name="simplify-summer-2027")

    jobs = parser.parse(load_fixture())

    assert jobs[0].category == "software_engineering"
    assert jobs[1].category == "software_engineering"
    assert jobs[2].category == "product_management"


def test_parser_extracts_job_details() -> None:
    parser = SimplifyTrackerParser(source_name="simplify-summer-2027")

    jobs = parser.parse(load_fixture())
    product_job = jobs[2]

    assert product_job.company == "Microsoft"
    assert product_job.title == "Product Manager Intern"
    assert product_job.location == "Redmond, WA"
    assert product_job.age == "2d"
