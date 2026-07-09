"""Title Generator — deterministic document/file titles from the plan goal."""
import re

_MAX_TITLE_WORDS = 10


def document_title(goal: str) -> str:
    words = goal.strip().rstrip(".").split()
    title = " ".join(words[:_MAX_TITLE_WORDS])
    if len(words) > _MAX_TITLE_WORDS:
        title += "…"
    return title[:1].upper() + title[1:] if title else "Generated Report"


def file_slug(goal: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", goal.lower()).strip("-")
    return slug[:48] or "report"
