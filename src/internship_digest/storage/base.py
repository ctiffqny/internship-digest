from typing import Protocol

from internship_digest.domain import JobOpening


class JobRepository(Protocol):
    """
    Interface implemented by any job storage system.

    The application currently uses SQLite, but this interface would also
    allow a PostgreSQL or in-memory implementation later.
    """

    def initialize(self) -> None:
        """Prepare storage before it is used."""

    def save(self, job: JobOpening) -> bool:
        """
        Save one job.

        Returns True when the job is new.
        """

    def save_many(
        self,
        jobs: list[JobOpening],
    ) -> list[JobOpening]:
        """Save many jobs and return only newly discovered ones."""

    def count(self) -> int:
        """Return the number of unique stored jobs."""
