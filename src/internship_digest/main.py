import sys

from internship_digest.config import load_settings
from internship_digest.sources.github import GitHubTrackerClient


def run() -> None:
    settings = load_settings()
    client = GitHubTrackerClient()

    for tracker in settings.github_trackers:
        markdown = client.fetch_markdown(str(tracker.url))

        print(f"Tracker: {tracker.name}")
        print(f"Downloaded: {len(markdown):,} characters")
        print(f"First line: {markdown.splitlines()[0] if markdown else '(empty)'}")
        print()


def main() -> None:
    try:
        run()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
