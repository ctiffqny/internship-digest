import re
from collections.abc import Iterator

from bs4 import BeautifulSoup, Tag
from pydantic import HttpUrl

from internship_digest.domain import JobOpening
from internship_digest.utils import normalize_url

SECTION_PATTERN = re.compile(
    r"^##\s+(?P<heading>.+? Internship Roles)\s*$",
    flags=re.MULTILINE,
)

CATEGORY_NAMES = {
    "Software Engineering Internship Roles": "software_engineering",
    "Product Management Internship Roles": "product_management",
    "Data Science, AI & Machine Learning Internship Roles": "data_ai_ml",
    "Quantitative Finance Internship Roles": "quantitative_finance",
    "Hardware Engineering Internship Roles": "hardware_engineering",
}


class SimplifyTrackerParser:
    def parse(
        self,
        content: str,
        source_name: str,
    ) -> list[JobOpening]:
        jobs: list[JobOpening] = []

        for heading, section_html in self._iter_sections(content):
            category = self._category_from_heading(heading)
            jobs.extend(
                self._parse_table(
                    section_html=section_html,
                    category=category,
                    source_name=source_name,
                )
            )

        return jobs

    def _iter_sections(self, markdown: str) -> Iterator[tuple[str, str]]:
        matches = list(SECTION_PATTERN.finditer(markdown))

        for index, match in enumerate(matches):
            section_start = match.end()
            section_end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)

            heading = self._clean_heading(match.group("heading"))
            section_html = markdown[section_start:section_end]

            yield heading, section_html

    def _parse_table(
        self,
        section_html: str,
        category: str,
        source_name: str,
    ) -> list[JobOpening]:
        soup = BeautifulSoup(section_html, "html.parser")
        table = soup.find("table")

        if not isinstance(table, Tag):
            return []

        jobs: list[JobOpening] = []
        previous_company: str | None = None

        for row in table.find_all("tr"):
            cells = row.find_all("td")

            if len(cells) != 5:
                continue

            company = self._extract_company(cells[0], previous_company)

            if company is None:
                continue

            previous_company = company

            title = self._clean_text(cells[1])
            location = self._clean_text(cells[2]) or None
            application_url = self._extract_application_url(cells[3])
            age = self._clean_text(cells[4]) or None

            if not title or application_url is None:
                continue

            jobs.append(
                JobOpening(
                    company=company,
                    title=title,
                    location=location,
                    url=HttpUrl(
                        normalize_url(str(application_url))
                    ),
                    source=source_name,
                    category=category,
                    age=age,
                )
            )

        return jobs

    def _extract_company(
        self,
        cell: Tag,
        previous_company: str | None,
    ) -> str | None:
        text = self._clean_text(cell)

        if text == "↳":
            return previous_company

        company_link = cell.find("a")

        company = company_link.get_text(" ", strip=True) if company_link is not None else text

        company = company.removeprefix("🔥").strip()

        return company or None

    @staticmethod
    def _extract_application_url(cell: Tag) -> HttpUrl | None:
        links = [str(link["href"]) for link in cell.find_all("a", href=True)]

        if not links:
            return None

        selected_url = next(
            (link for link in links if "simplify.jobs/p/" not in link),
            links[0],
        )

        return HttpUrl(selected_url)

    @staticmethod
    def _clean_text(cell: Tag) -> str:
        return " ".join(cell.get_text(" ", strip=True).split())

    @staticmethod
    def _clean_heading(heading: str) -> str:
        return (
            heading.replace("💻", "")
            .replace("📱", "")
            .replace("🤖", "")
            .replace("📈", "")
            .replace("🔧", "")
            .strip()
        )

    @staticmethod
    def _category_from_heading(heading: str) -> str:
        return CATEGORY_NAMES.get(heading, "other")
