from internship_digest.utils import normalize_url


def test_normalize_url_removes_tracking_parameters() -> None:
    url = "https://careers.example.com/jobs/123?utm_source=github&utm_campaign=summer"

    result = normalize_url(url)

    assert result == "https://careers.example.com/jobs/123"


def test_normalize_url_keeps_non_tracking_parameters() -> None:
    url = "https://careers.example.com/search?location=hong-kong&utm_source=github"

    result = normalize_url(url)

    assert result == ("https://careers.example.com/search?location=hong-kong")


def test_normalize_url_removes_fragment() -> None:
    url = "https://careers.example.com/jobs/123#apply"

    result = normalize_url(url)

    assert result == "https://careers.example.com/jobs/123"


def test_normalize_url_removes_trailing_slash() -> None:
    url = "https://careers.example.com/jobs/123/"

    result = normalize_url(url)

    assert result == "https://careers.example.com/jobs/123"


def test_normalize_url_is_idempotent() -> None:
    url = "https://careers.example.com/jobs/123/?utm_source=github"

    normalized_once = normalize_url(url)
    normalized_twice = normalize_url(normalized_once)

    assert normalized_once == normalized_twice
