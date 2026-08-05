import httpx

DEFAULT_TIMEOUT_SECONDS = 30.0


class GitHubTrackerClient:
    def __init__(
        self,
        client: httpx.Client | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._client = client
        self._timeout_seconds = timeout_seconds

    def fetch_markdown(self, url: str) -> str:
        headers = {
            "Accept": "text/plain",
            "User-Agent": "internship-digest/0.1",
        }

        try:
            if self._client is not None:
                response = self._client.get(
                    url,
                    headers=headers,
                    timeout=self._timeout_seconds,
                    follow_redirects=True,
                )
            else:
                response = httpx.get(
                    url,
                    headers=headers,
                    timeout=self._timeout_seconds,
                    follow_redirects=True,
                )

            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"Tracker returned HTTP {exc.response.status_code}: {url}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Could not connect to tracker: {url}") from exc

        return response.text
