import sys

from internship_digest.config import load_settings
from internship_digest.sources.github import GitHubTrackerClient
from internship_digest.sources.simplify_parser import SimplifyTrackerParser


SAMPLE_LIMIT = 10


def run() -> None:
    settings = load_settings()
    client = GitHubTrackerClient()

    total_jobs = 0

    for tracker in settings.github_trackers:
        markdown = client.fetch_markdown(str(tracker.url))
        parser = SimplifyTrackerParser(source_name=tracker.name)
        jobs = parser.parse(markdown)

        total_jobs += len(jobs)

        print(f"\nTracker: {tracker.name}")
        print(f"Parsed jobs: {len(jobs):,}")
        print("-" * 72)

        for job in jobs[:SAMPLE_LIMIT]:
            print(f"{job.company} — {job.title}")
            print(f"  Location: {job.location or 'Not provided'}")
            print(f"  Category: {job.category}")
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
