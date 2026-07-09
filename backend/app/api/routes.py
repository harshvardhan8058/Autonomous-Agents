"""Public API — POST /agent, GET /documents, GET /documents/{id}, GET /health.

Routes are defined without the /api prefix; Vercel strips it before
forwarding to this service.
"""
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.agent.orchestrator import AgentOrchestrator
from app.schemas.models import AgentRequest, AgentResponse
from app.services.document_store import document_store
from app.utils.json_utils import LLMJSONError

router = APIRouter()


class DocumentItem(BaseModel):
    id: str
    filename: str
    download_url: str


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "autonomous-agent"}


@router.get("/documents", response_model=list[DocumentItem])
async def list_documents() -> list[DocumentItem]:
    """Return all previously generated documents so the UI can list them."""
    return [
        DocumentItem(
            id=doc_id,
            filename=path.name,
            download_url=f"/api/documents/{doc_id}",
        )
        for doc_id, path in document_store.list_all()
    ]


@router.post("/agent", response_model=AgentResponse)
async def run_agent(payload: AgentRequest) -> AgentResponse:
    try:
        orchestrator = AgentOrchestrator()
    except RuntimeError as exc:  # missing credentials
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    try:
        return await orchestrator.run(payload.request)
    except LLMJSONError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Model returned unparseable output after retry: {exc}",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error ({exc.response.status_code}).",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/documents/{doc_id}")
async def download_document(doc_id: str) -> FileResponse:
    path = document_store.resolve(doc_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return FileResponse(
        path,
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        filename=path.name,
    )
