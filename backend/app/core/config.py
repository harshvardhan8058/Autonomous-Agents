"""Runtime configuration resolved from environment variables."""
import os
from dataclasses import dataclass, field
from pathlib import Path

DOCUMENTS_DIR = Path(os.environ.get("DOCUMENTS_DIR", "/tmp/agent-documents"))


@dataclass(frozen=True)
class LLMSettings:
    """Provider settings. Prefers direct Groq; falls back to Vercel AI Gateway
    routing the same Groq model, so the agent runs with either key present."""

    base_url: str
    api_key: str
    model: str
    timeout: float = 60.0

    @staticmethod
    def resolve() -> "LLMSettings":
        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key:
            return LLMSettings(
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_key,
                model="llama-3.3-70b-versatile",
            )
        gateway_key = os.environ.get("AI_GATEWAY_API_KEY")
        if gateway_key:
            return LLMSettings(
                base_url="https://ai-gateway.vercel.sh/v1",
                api_key=gateway_key,
                model="groq/llama-3.3-70b-versatile",
            )
        raise RuntimeError(
            "No LLM credentials found. Set GROQ_API_KEY or AI_GATEWAY_API_KEY."
        )


@dataclass(frozen=True)
class AgentSettings:
    max_tasks: int = 8
    reflection_quality_threshold: float = 0.75
    max_improvement_passes: int = 1  # bounded self-correction, never loops
    llm: LLMSettings = field(default_factory=LLMSettings.resolve)


def get_settings() -> AgentSettings:
    return AgentSettings()
