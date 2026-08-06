import sys

from internship_digest.config import load_settings
from internship_digest.sources.github import GitHubTrackerClient
from internship_digest.sources.parser_registry import ParserRegistry

SAMPLE_LIMIT = 10


def run() -> None:
    settings = load_settings()
    client = GitHubTrackerClient()
    parser_registry = ParserRegistry()

    total_jobs = 0

    for tracker in settings.github_trackers:
        content = client.fetch_markdown(str(tracker.url))
        parser = parser_registry.get(tracker.parser)

        jobs = parser.parse(
            content=content,
            source_name=tracker.name,
        )

        total_jobs += len(jobs)

        print(f"\nTracker: {tracker.name}")
        print(f"Parser: {tracker.parser}")
        print(f"Parsed jobs: {len(jobs):,}")
        print("-" * 72)

        for job in jobs[:SAMPLE_LIMIT]:
            print(f"{job.company} — {job.title}")
            print(f"  Location: {job.location or 'Not provided'}")
            print(f"  Category: {job.category or 'Uncategorized'}")
            print(f"  Age: {job.age or 'Unknown'}")
            print(f"  Apply: {job.url}")
            print()

    print(f"Total parsed jobs: {total_jobs:,}")


def main() -> None:
    try:
        run()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
