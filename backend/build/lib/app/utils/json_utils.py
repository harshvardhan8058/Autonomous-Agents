"""Tolerant JSON extraction for LLM responses."""
import json
import re
from typing import Any


class LLMJSONError(ValueError):
    """Raised when a model response cannot be parsed as JSON."""


_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def extract_json(text: str) -> dict[str, Any]:
    """Parse a JSON object out of raw model output.

    Handles code fences and leading/trailing prose. Raises LLMJSONError
    so callers can trigger a single structured retry.
    """
    candidate = text.strip()
    fence = _FENCE.search(candidate)
    if fence:
        candidate = fence.group(1)
    else:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start != -1 and end > start:
            candidate = candidate[start : end + 1]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise LLMJSONError(f"Malformed JSON from model: {exc}") from exc
    if not isinstance(parsed, dict):
        raise LLMJSONError("Model returned JSON that is not an object.")
    return parsed
