from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_QUERY_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "ref",
    "source",
}


def normalize_url(url: str) -> str:
    """
    Return a canonical version of a URL.

    A canonical URL is the version we want the rest of the application
    to treat as the true identity of the page.

    Example:

        https://example.com/jobs/123?utm_source=github&ref=simplify

    becomes:

        https://example.com/jobs/123

    We currently normalize by:

    1. Lowercasing the scheme and hostname.
    2. Removing common tracking query parameters.
    3. Removing a trailing slash from the path.
    4. Removing fragments such as "#apply".
    """

    parts = urlsplit(url)

    filtered_query_parameters = [
        (key, value)
        for key, value in parse_qsl(
            parts.query,
            keep_blank_values=True,
        )
        if key.lower() not in TRACKING_QUERY_PARAMETERS
    ]

    normalized = urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/"),
            urlencode(filtered_query_parameters),
            "",
        )
    )

    return normalized
