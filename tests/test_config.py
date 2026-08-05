from pathlib import Path

from internship_digest.config import get_runtime_directory


def test_runtime_directory_defaults_to_home(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("INTERNSHIP_DIGEST_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    runtime_directory = get_runtime_directory()

    assert runtime_directory == tmp_path / "internship-digest-runtime"
    assert runtime_directory.is_dir()


def test_runtime_directory_supports_override(
    monkeypatch,
    tmp_path: Path,
) -> None:
    custom_directory = tmp_path / "private-runtime"
    monkeypatch.setenv("INTERNSHIP_DIGEST_HOME", str(custom_directory))

    runtime_directory = get_runtime_directory()

    assert runtime_directory == custom_directory
    assert runtime_directory.is_dir()
