from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """
    Represents a single retrievable unit of code.

    A Chunk is the atomic indexing unit stored in Azure AI Search.
    It preserves both semantic content and structural metadata so that:

    - Retrieval can return meaningful, symbol-level context
    - Answers can cite exact file locations (path + line range)
    - Re-indexing remains deterministic via chunk_id
    """
    chunk_id: str
    path: str
    start_line: int
    end_line: int
    symbol: str | None
    content: str
