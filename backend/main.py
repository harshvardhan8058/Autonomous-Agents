"""Autonomous AI Agent — FastAPI entrypoint."""
import fastapi
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = fastapi.FastAPI(
    title="Autonomous AI Agent",
    description="Plans, executes, self-reviews, and produces professional DOCX reports.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
