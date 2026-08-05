from internship_digest.config import load_settings
from internship_digest.sources.github import fetch_markdown


def main() -> None:
    settings = load_settings()

    for tracker in settings.github_trackers:
        markdown = fetch_markdown(str(tracker.url))

        print(f"Tracker: {tracker.name}")
        print(f"Downloaded {len(markdown):,} characters")
        print(markdown[:500])
        print()


if __name__ == "__main__":
    main()