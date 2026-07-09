"""Executor — runs planned tasks sequentially, producing document sections."""
import time

from pydantic import ValidationError

from app.core.llm import LLMClient
from app.schemas.models import Plan, PlannedTask, Section, TaskExecution

_SYSTEM = """You are the execution module of an autonomous document-writing agent.
Write ONE polished report section for the task you are given, consistent with
the overall goal and the sections already written.

Return ONLY a JSON object:
{
  "heading": "Section heading",
  "paragraphs": ["2-4 substantive paragraphs of professional prose"],
  "bullets": ["0-6 concise bullet points, only if they add value"]
}
No markdown syntax inside strings. No prose outside the JSON."""


class Executor:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def execute(self, plan: Plan) -> list[TaskExecution]:
        executions: list[TaskExecution] = []
        written: list[str] = []
        for task in plan.tasks:
            executions.append(await self._run_task(plan, task, written))
        return executions

    async def _run_task(
        self, plan: Plan, task: PlannedTask, written: list[str]
    ) -> TaskExecution:
        started = time.monotonic()
        context = ", ".join(written) if written else "none yet"
        user = (
            f"Goal: {plan.goal}\n"
            f"Sections already written: {context}\n\n"
            f"Task {task.id} ({task.priority} priority): {task.title}\n"
            f"Requirements: {task.description}"
        )
        try:
            data = await self._llm.complete_json(_SYSTEM, user, temperature=0.4)
            section = Section.model_validate(data)
        except (ValidationError, ValueError, Exception) as exc:  # noqa: BLE001
            return TaskExecution(
                task_id=task.id,
                title=task.title,
                status="failed",
                duration_ms=int((time.monotonic() - started) * 1000),
                error=str(exc)[:300],
            )
        written.append(section.heading)
        return TaskExecution(
            task_id=task.id,
            title=task.title,
            status="completed",
            duration_ms=int((time.monotonic() - started) * 1000),
            section=section,
        )
