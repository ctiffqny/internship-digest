from internship_digest.config import ParserType
from internship_digest.sources.parsers import TrackerParser
from internship_digest.sources.simplify_parser import SimplifyTrackerParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[ParserType, TrackerParser] = {
            ParserType.SIMPLIFY_HTML: SimplifyTrackerParser(),
        }

    def get(self, parser_type: ParserType) -> TrackerParser:
        try:
            return self._parsers[parser_type]
        except KeyError as exc:
            raise RuntimeError(f"No parser registered for type: {parser_type}") from exc
