import os
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, HttpUrl, ValidationError


class ParserType(StrEnum):
    SIMPLIFY_HTML = "simplify_html"
    MARKDOWN_TABLE = "markdown_table"


class GitHubTrackerConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    url: HttpUrl
    parser: ParserType


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    github_trackers: list[GitHubTrackerConfig]


def get_default_runtime_directory() -> Path:
    return Path.home() / "internship-digest-runtime"


def get_runtime_directory() -> Path:
    configured_path = os.environ.get("INTERNSHIP_DIGEST_HOME")

    runtime_directory = (
        Path(configured_path).expanduser() if configured_path else get_default_runtime_directory()
    ).resolve()

    runtime_directory.mkdir(parents=True, exist_ok=True)
    return runtime_directory


def load_settings() -> Settings:
    settings_path = get_runtime_directory() / "settings.yaml"

    if not settings_path.is_file():
        raise RuntimeError(
            f"Settings file not found: {settings_path}\n"
            "Create it from config/settings.example.yaml."
        )

    try:
        with settings_path.open("r", encoding="utf-8") as file:
            raw_settings = yaml.safe_load(file) or {}

        return Settings.model_validate(raw_settings)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Invalid YAML in {settings_path}") from exc
    except ValidationError as exc:
        raise RuntimeError(f"Invalid settings in {settings_path}:\n{exc}") from exc
