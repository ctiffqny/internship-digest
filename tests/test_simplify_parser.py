from pathlib import Path

import pytest

from internship_digest.domain import JobOpening
from internship_digest.sources.simplify_parser import SimplifyTrackerParser

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "simplify_sample.md"


def load_fixture() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


@pytest.fixture
def parsed_jobs() -> list[JobOpening]:
    parser = SimplifyTrackerParser()

    return parser.parse(
        content=load_fixture(),
        source_name="simplify-summer-2027",
    )


def test_parser_extracts_all_jobs(
    parsed_jobs: list[JobOpening],
) -> None:
    assert len(parsed_jobs) == 3


def test_parser_carries_forward_repeated_company(
    parsed_jobs: list[JobOpening],
) -> None:
    assert parsed_jobs[0].company == "TikTok"
    assert parsed_jobs[1].company == "TikTok"


def test_parser_prefers_employer_application_url(
    parsed_jobs: list[JobOpening],
) -> None:
    assert str(parsed_jobs[0].url) == ("https://careers.example.com/tiktok-swe")


def test_parser_assigns_categories(
    parsed_jobs: list[JobOpening],
) -> None:
    assert parsed_jobs[0].category == "software_engineering"
    assert parsed_jobs[1].category == "software_engineering"
    assert parsed_jobs[2].category == "product_management"


def test_parser_extracts_job_details(
    parsed_jobs: list[JobOpening],
) -> None:
    product_job = parsed_jobs[2]

    assert product_job.company == "Microsoft"
    assert product_job.title == "Product Manager Intern"
    assert product_job.location == "Redmond, WA"
    assert product_job.age == "2d"
