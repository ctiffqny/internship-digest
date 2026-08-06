from typing import Protocol

from internship_digest.domain import JobOpening


class TrackerParser(Protocol):
    def parse(
        self,
        content: str,
        source_name: str,
    ) -> list[JobOpening]:
        """Parse tracker content into normalized job openings."""
