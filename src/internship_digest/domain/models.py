from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobOpening(BaseModel):
    model_config = ConfigDict(frozen=True)

    company: str = Field(min_length=1)
    title: str = Field(min_length=1)
    location: str | None = None
    url: HttpUrl
    source: str = Field(min_length=1)
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
