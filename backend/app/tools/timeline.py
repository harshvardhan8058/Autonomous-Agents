"""Timeline Generator — derives an indicative delivery timeline from the plan."""
from app.schemas.models import PlannedTask
from app.tools.dates import offset_date

_WEEKS_PER_PRIORITY = {"high": 1, "medium": 2, "low": 3}


def build_timeline(tasks: list[PlannedTask]) -> list[dict[str, str]]:
    """Rows of {phase, priority, target} for the DOCX timeline table."""
    rows: list[dict[str, str]] = []
    cursor = 0
    for task in tasks:
        cursor += _WEEKS_PER_PRIORITY.get(task.priority, 2)
        rows.append(
            {
                "phase": task.title,
                "priority": task.priority.capitalize(),
                "target": offset_date(cursor),
            }
        )
    return rows
