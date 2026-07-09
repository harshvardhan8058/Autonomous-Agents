"""Document store — maps opaque document ids to files on disk.

Intentionally filesystem-backed (no database, per requirements). IDs are
validated against a strict pattern so the store can never serve paths
outside its root directory.
"""
import re
import uuid
from pathlib import Path

from app.core.config import DOCUMENTS_DIR
from app.tools.dates import timestamp_file

_ID_PATTERN = re.compile(r"^[a-z0-9-]{1,80}$")


class DocumentStore:
    def __init__(self, root: Path = DOCUMENTS_DIR) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def allocate(self, slug: str) -> tuple[str, Path]:
        doc_id = f"{slug}-{timestamp_file()}-{uuid.uuid4().hex[:6]}"
        return doc_id, self._root / f"{doc_id}.docx"

    def resolve(self, doc_id: str) -> Path | None:
        if not _ID_PATTERN.match(doc_id):
            return None
        path = (self._root / f"{doc_id}.docx").resolve()
        if path.parent != self._root.resolve() or not path.is_file():
            return None
        return path

    def list_all(self) -> list[tuple[str, Path]]:
        """Return all stored (doc_id, path) pairs sorted newest-first."""
        docs = sorted(self._root.glob("*.docx"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [(p.stem, p) for p in docs]


document_store = DocumentStore()
