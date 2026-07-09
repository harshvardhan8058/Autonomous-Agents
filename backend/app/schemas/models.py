"""Pydantic contracts for the agent pipeline and public API."""
from typing import Literal

from pydantic import BaseModel, Field

# ---------- request ----------


class AgentRequest(BaseModel):
    request: str = Field(min_length=3, max_length=4000)


# ---------- planner ----------


class PlannedTask(BaseModel):
    id: int
    title: str
    description: str
    priority: Literal["high", "medium", "low"] = "medium"


class Plan(BaseModel):
    goal: str
    assumptions: list[str]
    tasks: list[PlannedTask]
    confidence: float = Field(ge=0.0, le=1.0)


# ---------- executor ----------


class Section(BaseModel):
    heading: str
    paragraphs: list[str] = []
    bullets: list[str] = []


class TaskExecution(BaseModel):
    task_id: int
    title: str
    status: Literal["completed", "failed"]
    duration_ms: int
    section: Section | None = None
    error: str | None = None


# ---------- reflection ----------


class ReflectionReport(BaseModel):
    quality_score: float = Field(ge=0.0, le=1.0)
    complete: bool
    issues: list[str]
    improved_sections: list[str] = []
    passes: int = 0


# ---------- response ----------


class ExecutionSummary(BaseModel):
    total_tasks: int
    completed: int
    failed: int
    duration_ms: int
    reflection: ReflectionReport


class AgentResponse(BaseModel):
    request: str = ""          # echoed back for reference in demos
    plan: Plan
    execution_summary: ExecutionSummary
    executions: list[TaskExecution]
    document_id: str
    document_path: str
    document_url: str


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
