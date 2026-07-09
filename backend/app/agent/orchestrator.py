"""Agent orchestrator — the single-agent pipeline.

Request → Planner → Executor → Reflection → DOCX → Response.
Each stage is an isolated module; the orchestrator only sequences them.
"""
import time

from app.core.config import get_settings
from app.core.llm import LLMClient
from app.documents.docx_generator import generate_docx
from app.executor.executor import Executor
from app.planner.planner import Planner
from app.reflection.reflector import Reflector
from app.schemas.models import AgentResponse, ExecutionSummary
from app.services.document_store import document_store
from app.tools.titles import file_slug


class AgentOrchestrator:
    def __init__(self) -> None:
        settings = get_settings()
        llm = LLMClient(settings.llm)
        self._planner = Planner(llm, settings)
        self._executor = Executor(llm)
        self._reflector = Reflector(llm, settings)

    async def run(self, request: str) -> AgentResponse:
        started = time.monotonic()

        plan = await self._planner.plan(request)
        executions = await self._executor.execute(plan)
        reflection = await self._reflector.reflect_and_improve(plan, executions)

        doc_id, path = document_store.allocate(file_slug(plan.goal))
        generate_docx(plan, executions, path)

        completed = sum(1 for e in executions if e.status == "completed")
        return AgentResponse(
            plan=plan,
            execution_summary=ExecutionSummary(
                total_tasks=len(executions),
                completed=completed,
                failed=len(executions) - completed,
                duration_ms=int((time.monotonic() - started) * 1000),
                reflection=reflection,
            ),
            executions=executions,
            document_id=doc_id,
            document_path=str(path),
            document_url=f"/api/documents/{doc_id}",
        )
