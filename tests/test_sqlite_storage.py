from pathlib import Path

from internship_digest.domain import JobOpening
from internship_digest.storage.sqlite import (
    SQLiteJobRepository,
    create_job_fingerprint,
    normalize_url,
)


def make_job(
    url: str = "https://careers.example.com/jobs/123",
) -> JobOpening:
    """
    Create a reusable test job.

    Helper functions keep the individual tests focused on the behavior
    being tested rather than repeating large object constructors.
    """

    return JobOpening(
        company="Example Company",
        title="Software Engineer Intern",
        location="New York, NY",
        url=url,
        source="test-tracker",
        category="software_engineering",
        age="0d",
    )


def test_normalize_url_removes_tracking_parameters() -> None:
    url = "https://careers.example.com/jobs/123?utm_source=github&utm_campaign=summer"

    normalized_url = normalize_url(url)

    assert normalized_url == ("https://careers.example.com/jobs/123")


def test_fingerprint_is_stable_for_equivalent_urls() -> None:
    first_job = make_job("https://careers.example.com/jobs/123?utm_source=github")

    second_job = make_job("https://careers.example.com/jobs/123?utm_source=simplify")

    assert create_job_fingerprint(first_job) == create_job_fingerprint(second_job)


def test_save_returns_true_for_new_job(
    tmp_path: Path,
) -> None:
    repository = SQLiteJobRepository(tmp_path / "jobs.sqlite3")
    repository.initialize()

    was_inserted = repository.save(make_job())

    assert was_inserted is True
    assert repository.count() == 1


def test_save_returns_false_for_existing_job(
    tmp_path: Path,
) -> None:
    repository = SQLiteJobRepository(tmp_path / "jobs.sqlite3")
    repository.initialize()

    repository.save(make_job())
    was_inserted_again = repository.save(make_job())

    assert was_inserted_again is False
    assert repository.count() == 1


def test_save_many_returns_only_new_jobs(
    tmp_path: Path,
) -> None:
    repository = SQLiteJobRepository(tmp_path / "jobs.sqlite3")
    repository.initialize()

    first_job = make_job("https://careers.example.com/jobs/123")
    second_job = make_job("https://careers.example.com/jobs/456")

    first_result = repository.save_many([first_job, second_job])
    second_result = repository.save_many([first_job, second_job])

    assert len(first_result) == 2
    assert second_result == []
    assert repository.count() == 2
