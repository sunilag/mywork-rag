from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    path: str
    start_line: int
    end_line: int
    symbol: str | None
    content: str
