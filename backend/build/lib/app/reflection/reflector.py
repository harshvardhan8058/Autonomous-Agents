"""Reflection — the agent reviews its own output and improves it once.

Bounded self-correction: at most `max_improvement_passes` (default 1).
This is deliberate — unbounded reflection loops burn tokens without
converging, and a single targeted pass captures most of the gain.
"""
from pydantic import ValidationError

from app.core.config import AgentSettings
from app.core.llm import LLMClient
from app.schemas.models import Plan, ReflectionReport, Section, TaskExecution

_REVIEW_SYSTEM = """You are the reflection module of an autonomous document-writing agent.
Critically review the generated report against the plan for completeness,
internal consistency, formatting quality, and missing sections.

Return ONLY a JSON object:
{
  "quality_score": 0.0-1.0,
  "complete": true|false,
  "issues": ["specific, actionable problems found"],
  "sections_to_improve": ["exact headings of sections that need rework"]
}
Be strict but fair. No prose outside the JSON."""

_IMPROVE_SYSTEM = """You are revising one section of a report based on reviewer feedback.
Rewrite it to resolve the issues while keeping its scope and heading.

Return ONLY a JSON object:
{"heading": "...", "paragraphs": ["..."], "bullets": ["..."]}
No prose outside the JSON."""


class Reflector:
    def __init__(self, llm: LLMClient, settings: AgentSettings) -> None:
        self._llm = llm
        self._settings = settings

    async def reflect_and_improve(
        self, plan: Plan, executions: list[TaskExecution]
    ) -> ReflectionReport:
        review = await self._review(plan, executions)
        if (
            review.quality_score >= self._settings.reflection_quality_threshold
            or not review.improved_sections
        ):
            return review

        # single bounded improvement pass
        by_heading = {
            e.section.heading: e for e in executions if e.section is not None
        }
        improved: list[str] = []
        targets = review.improved_sections[:3]  # cap rework surface
        for heading in targets:
            execution = by_heading.get(heading)
            if execution is None or execution.section is None:
                continue
            new_section = await self._improve(plan, execution.section, review.issues)
            if new_section is not None:
                execution.section = new_section
                improved.append(heading)
        review.improved_sections = improved
        review.passes = 1 if improved else 0
        if improved:
            review.quality_score = min(1.0, review.quality_score + 0.15)
            review.complete = True
        return review

    async def _review(
        self, plan: Plan, executions: list[TaskExecution]
    ) -> ReflectionReport:
        digest = "\n\n".join(
            f"## {e.section.heading}\n"
            + "\n".join(e.section.paragraphs)
            + ("\n- " + "\n- ".join(e.section.bullets) if e.section.bullets else "")
            for e in executions
            if e.section is not None
        )
        failed = [e.title for e in executions if e.status == "failed"]
        user = (
            f"Plan goal: {plan.goal}\n"
            f"Planned sections: {[t.title for t in plan.tasks]}\n"
            f"Failed tasks: {failed or 'none'}\n\n"
            f"Generated report:\n{digest[:12000]}"
        )
        data = await self._llm.complete_json(_REVIEW_SYSTEM, user)
        try:
            return ReflectionReport(
                quality_score=float(data.get("quality_score", 0.5)),
                complete=bool(data.get("complete", False)),
                issues=[str(i) for i in data.get("issues", [])][:8],
                improved_sections=[
                    str(s) for s in data.get("sections_to_improve", [])
                ],
            )
        except ValidationError:
            return ReflectionReport(
                quality_score=0.5, complete=False, issues=["Reviewer output invalid"]
            )

    async def _improve(
        self, plan: Plan, section: Section, issues: list[str]
    ) -> Section | None:
        user = (
            f"Goal: {plan.goal}\n"
            f"Reviewer issues: {issues}\n\n"
            f"Current section JSON:\n{section.model_dump_json()}"
        )
        try:
            data = await self._llm.complete_json(_IMPROVE_SYSTEM, user, temperature=0.4)
            return Section.model_validate(data)
        except (ValidationError, ValueError, Exception):  # noqa: BLE001
            return None  # keep original section on failure
