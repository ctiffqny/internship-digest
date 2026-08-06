import sys

from internship_digest.config import (
    get_runtime_directory,
    load_settings,
)
from internship_digest.domain import JobOpening
from internship_digest.sources.github import GitHubTrackerClient
from internship_digest.sources.parser_registry import ParserRegistry
from internship_digest.storage.sqlite import SQLiteJobRepository
from internship_digest.utils import normalize_url

SAMPLE_LIMIT = 10


def print_job(job: JobOpening) -> None:
    """
    Print one job in a readable format.

    Keeping presentation logic in a separate function makes run() easier
    to read and lets us replace terminal output with email HTML later.
    """

    print(f"{job.company} — {job.title}")
    print(f"  Location: {job.location or 'Not provided'}")
    print(f"  Category: {job.category or 'Uncategorized'}")
    print(f"  Age: {job.age or 'Unknown'}")
    print(f"  Apply: {normalize_url(str(job.url))}")
    print()


def run() -> None:
    """
    Execute one complete internship collection cycle.

    A cycle means:
    1. Load configuration.
    2. Fetch each tracker.
    3. Parse jobs.
    4. Store them.
    5. Print only newly discovered jobs.
    """

    settings = load_settings()

    tracker_client = GitHubTrackerClient()
    parser_registry = ParserRegistry()

    database_path = get_runtime_directory() / "jobs.sqlite3"

    job_repository = SQLiteJobRepository(database_path)
    job_repository.initialize()

    total_parsed_jobs = 0
    total_new_jobs = 0

    for tracker in settings.github_trackers:
        content = tracker_client.fetch_markdown(str(tracker.url))

        parser = parser_registry.get(tracker.parser)

        parsed_jobs = parser.parse(
            content=content,
            source_name=tracker.name,
        )

        new_jobs = job_repository.save_many(parsed_jobs)

        total_parsed_jobs += len(parsed_jobs)
        total_new_jobs += len(new_jobs)

        print()
        print(f"Tracker: {tracker.name}")
        print(f"Parser: {tracker.parser}")
        print(f"Parsed jobs: {len(parsed_jobs):,}")
        print(f"New jobs: {len(new_jobs):,}")
        print("-" * 72)

        for job in new_jobs[:SAMPLE_LIMIT]:
            print_job(job)

        remaining_jobs = len(new_jobs) - SAMPLE_LIMIT

        if remaining_jobs > 0:
            print(f"... and {remaining_jobs:,} more new jobs")

    print()
    print(f"Total parsed jobs: {total_parsed_jobs:,}")
    print(f"Total new jobs: {total_new_jobs:,}")
    print(f"Total jobs stored: {job_repository.count():,}")


def main() -> None:
    """
    Command-line entry point.

    RuntimeError represents expected operational errors, such as:
    - invalid configuration;
    - inaccessible tracker;
    - malformed tracker response.

    We show a concise message instead of exposing a large traceback to a
    normal user.
    """

    try:
        run()
    except RuntimeError as exc:
        print(
            f"Error: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
