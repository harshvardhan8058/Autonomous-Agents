"""Planner — turns a raw user request into a structured, validated Plan."""
from pydantic import ValidationError

from app.core.config import AgentSettings
from app.core.llm import LLMClient
from app.schemas.models import Plan

_SYSTEM = """You are the planning module of an autonomous document-writing agent.
Decompose the user's request into a concrete execution plan whose tasks each
produce one section of a professional report.

Return ONLY a JSON object:
{
  "goal": "one-sentence restatement of the objective",
  "assumptions": ["explicit assumptions you are making"],
  "tasks": [
    {"id": 1, "title": "Section title", "description": "what this section must cover", "priority": "high|medium|low"}
  ],
  "confidence": 0.0-1.0
}

Rules:
- 3 to {max_tasks} tasks, ordered logically (overview first, details, then conclusions).
- Task titles must read as report section headings.
- Do not include an executive summary task; the agent adds it separately.
- No prose outside the JSON."""


class Planner:
    def __init__(self, llm: LLMClient, settings: AgentSettings) -> None:
        self._llm = llm
        self._settings = settings

    async def plan(self, request: str) -> Plan:
        data = await self._llm.complete_json(
            _SYSTEM.replace("{max_tasks}", str(self._settings.max_tasks)),
            request,
        )
        try:
            plan = Plan.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Planner returned an invalid plan: {exc}") from exc
        plan.tasks = plan.tasks[: self._settings.max_tasks]
        return plan
