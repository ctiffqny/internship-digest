import os
from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl


class GitHubTrackerConfig(BaseModel):
    name: str
    url: HttpUrl


class Settings(BaseModel):
    github_trackers: list[GitHubTrackerConfig]


from pathlib import Path
import os

def get_runtime_directory() -> Path:
    runtime_directory = Path(
        os.environ.get(
            "INTERNSHIP_DIGEST_HOME",
            str(Path.home() / "internship-digest-runtime"),
        )
    ).expanduser().resolve()

    runtime_directory.mkdir(parents=True, exist_ok=True)

    return runtime_directory


def load_settings() -> Settings:
    settings_path = get_runtime_directory() / "settings.yaml"

    if not settings_path.exists():
        raise RuntimeError(f"Settings file not found: {settings_path}")

    with settings_path.open("r", encoding="utf-8") as file:
        raw_settings = yaml.safe_load(file)

    return Settings.model_validate(raw_settings)