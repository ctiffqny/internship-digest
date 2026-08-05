import httpx


def fetch_markdown(url: str) -> str:
    headers = {
        "User-Agent": "internship-digest/0.1",
        "Accept": "text/plain",
    }

    try:
        response = httpx.get(
            url,
            headers=headers,
            timeout=30,
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Failed to fetch tracker: {url}") from exc

    return response.text