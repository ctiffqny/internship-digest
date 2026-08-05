from typing import Protocol

from internship_digest.domain import JobOpening


class JobRepository(Protocol):
    def initialize(self) -> None:
        """Prepare persistent storage."""

    def save(self, job: JobOpening) -> bool:
        """
        Save or update a job.

        Returns True when the job is newly discovered.
        """
