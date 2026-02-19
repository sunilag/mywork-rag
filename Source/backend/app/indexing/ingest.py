from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


EXCLUDE_DIRS = {
    "alembic",
    "email-templates",
    "__pycache__",
}

EXCLUDE_FILES = {
    "somefilesyouwanttoexclude.extension",
}


def iter_python_files(repo_root: Path) -> Iterable[Path]:
    """
    Get Python source files under backend/app with exlcusion files.
    """
    backend_app = repo_root / "backend" / "app"
    if not backend_app.is_dir():
        raise ValueError(f"Expected backend/app under {repo_root}, found nothing")

    for path in backend_app.rglob("*.py"):
        # Exclude directories
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in EXCLUDE_FILES:
            continue
        yield path


def read_file(path: Path) -> list[str]:
    """
    Read file as list of lines.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("Skipping non-UTF8 file: %s", path)
        return []
    return text.splitlines()
