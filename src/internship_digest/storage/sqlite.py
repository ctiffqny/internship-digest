import hashlib
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from internship_digest.domain import JobOpening

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
    Return a consistent version of a job URL.

    Job links often include analytics parameters such as:

        ?utm_source=github&utm_campaign=internships

    Those parameters do not identify a different job. Removing them helps
    us recognize that two slightly different-looking links point to the
    same posting.
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

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/"),
            urlencode(filtered_query_parameters),
            "",
        )
    )


def create_job_fingerprint(job: JobOpening) -> str:
    """
    Create a stable identifier for a job opening.

    We use the normalized application URL because it is normally the most
    reliable unique identifier for a job.

    SHA-256 converts that URL into a fixed-length value suitable for use as
    a database primary key.
    """

    normalized_url = normalize_url(str(job.url))

    fingerprint_material = normalized_url

    return hashlib.sha256(fingerprint_material.encode("utf-8")).hexdigest()


class SQLiteJobRepository:
    """
    Store internship listings in a local SQLite database.

    The repository hides database-specific code from the rest of the
    application. Other parts of the program only need to know that they can
    save jobs and retrieve newly discovered jobs.
    """

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        """
        Open a database connection.

        row_factory lets us access result columns by name, such as
        row["company"], instead of only by numeric position.
        """

        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row

        return connection

    def initialize(self) -> None:
        """
        Create the jobs table if it does not already exist.

        This method is safe to call every time the program starts because
        CREATE TABLE IF NOT EXISTS does nothing when the table already exists.
        """

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    fingerprint TEXT PRIMARY KEY,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    location TEXT,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT,
                    age TEXT,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                )
                """
            )

    def save(self, job: JobOpening) -> bool:
        """
        Insert a job when it is new, or update last_seen when it already exists.

        Returns:
            True when this job was inserted for the first time.
            False when the job was already stored.
        """

        fingerprint = create_job_fingerprint(job)
        timestamp = job.discovered_at.isoformat()

        with self._connect() as connection:
            existing_job = connection.execute(
                """
                SELECT fingerprint
                FROM jobs
                WHERE fingerprint = ?
                """,
                (fingerprint,),
            ).fetchone()

            if existing_job is not None:
                connection.execute(
                    """
                    UPDATE jobs
                    SET
                        last_seen = ?,
                        age = ?
                    WHERE fingerprint = ?
                    """,
                    (
                        timestamp,
                        job.age,
                        fingerprint,
                    ),
                )

                return False

            connection.execute(
                """
                INSERT INTO jobs (
                    fingerprint,
                    company,
                    title,
                    location,
                    url,
                    source,
                    category,
                    age,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fingerprint,
                    job.company,
                    job.title,
                    job.location,
                    normalize_url(str(job.url)),
                    job.source,
                    job.category,
                    job.age,
                    timestamp,
                    timestamp,
                ),
            )

        return True

    def save_many(
        self,
        jobs: list[JobOpening],
    ) -> list[JobOpening]:
        """
        Save several jobs and return only those that were newly inserted.

        This method makes the calling code simpler:

            new_jobs = repository.save_many(parsed_jobs)
        """

        new_jobs: list[JobOpening] = []

        for job in jobs:
            if self.save(job):
                new_jobs.append(job)

        return new_jobs

    def count(self) -> int:
        """Return the total number of unique jobs stored."""

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM jobs
                """
            ).fetchone()

        if row is None:
            return 0

        return int(row["total"])

    def iter_jobs(self) -> Iterator[sqlite3.Row]:
        """
        Yield every stored job from newest to oldest.

        We may use this later for debugging, reporting, or generating a
        dashboard.
        """

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM jobs
                ORDER BY first_seen DESC
                """
            ).fetchall()

        yield from rows
