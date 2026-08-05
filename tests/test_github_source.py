import httpx
import pytest

from internship_digest.sources.github import GitHubTrackerClient


def test_fetch_markdown_returns_response_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            text="# Internship Tracker",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as http_client:
        client = GitHubTrackerClient(client=http_client)

        result = client.fetch_markdown("https://example.com/README.md")

    assert result == "# Internship Tracker"


def test_fetch_markdown_raises_clean_error_for_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=404,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as http_client:
        client = GitHubTrackerClient(client=http_client)

        with pytest.raises(RuntimeError, match="HTTP 404"):
            client.fetch_markdown("https://example.com/missing.md")
