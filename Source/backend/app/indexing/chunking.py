from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, List

from app.types import Chunk


def _make_chunk_id(path: Path, start_line: int, end_line: int, content: str) -> str:
    """
    Generate a deterministic chunk identifier.

    The hash includes file path, line range, and content so that:
    - Re-indexing the same code produces stable IDs
    - Modified code results in new chunk IDs
    """
    h = hashlib.sha1()
    h.update(str(path).encode("utf-8"))
    h.update(str(start_line).encode("utf-8"))
    h.update(str(end_line).encode("utf-8"))
    h.update(content.encode("utf-8"))
    return h.hexdigest()


def chunk_python_file(path: Path, lines: list[str], max_lines: int = 220, overlap: int = 30) -> List[Chunk]:
    """
    Chunk a Python file into semantically meaningful units.

    Strategy:
      1. Prefer top-level class/def blocks (structure-aware chunking).
      2. If blocks are too large, split with overlap.
      3. Fallback to fixed-size chunking if no top-level symbols found.
    """
    
    if not lines:
        return []

    chunks: List[Chunk] = []

    # identify top-level class and def blocks.
    block_starts: list[tuple[int, str | None]] = []  # (line_idx, symbol_name)
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent == 0 and (stripped.startswith("def ") or stripped.startswith("class ")):
            # Extract function or class names: e.g: def foo( ... ): or class foo( ... ):
            symbol = stripped.split()[1].split("(")[0].split(":")[0]
            block_starts.append((i, symbol))

    if block_starts:
        # Append at EOF for end-boundary calculation
        block_starts.append((len(lines), None))

        for (start_idx, symbol), (next_start_idx, _) in zip(block_starts, block_starts[1:]):
            if symbol is None:
                break
            block_lines = lines[start_idx:next_start_idx]
            # for huge blocks.
            start_line_num = start_idx + 1
            end_line_num = next_start_idx

            if len(block_lines) <= max_lines:
                content = "\n".join(block_lines)
                chunk_id = _make_chunk_id(path, start_line_num, end_line_num, content)
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        path=str(path),
                        start_line=start_line_num,
                        end_line=end_line_num,
                        symbol=symbol,
                        content=content,
                    )
                )
            else:
                # split by maximum lines for huge big block along with overlaps
                offset = 0
                while offset < len(block_lines):
                    sub = block_lines[offset : offset + max_lines]
                    sub_start_line = start_line_num + offset
                    sub_end_line = min(start_line_num + offset + len(sub) - 1, end_line_num)
                    content = "\n".join(sub)
                    chunk_id = _make_chunk_id(path, sub_start_line, sub_end_line, content)
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            path=str(path),
                            start_line=sub_start_line,
                            end_line=sub_end_line,
                            symbol=symbol,
                            content=content,
                        )
                    )
                    if offset + max_lines >= len(block_lines):
                        break
                    offset += max_lines - overlap

        return chunks

    # for no top-level blocks follow fix size chunking 
    chunks = []
    i = 0
    n = len(lines)
    while i < n:
        block = lines[i : i + max_lines]
        start_line_num = i + 1
        end_line_num = min(i + len(block), n)
        content = "\n".join(block)
        chunk_id = _make_chunk_id(path, start_line_num, end_line_num, content)
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                path=str(path),
                start_line=start_line_num,
                end_line=end_line_num,
                symbol=None,
                content=content,
            )
        )
        if i + max_lines >= n:
            break
        i += max_lines - overlap

    return chunks


def chunk_repo_python_files(paths: Iterable[Path]) -> list[Chunk]:
    """
    Apply chunking across multiple Python files.
    """
    from app.indexing.ingest import read_file  # local import to avoid cycles

    all_chunks: list[Chunk] = []
    for path in paths:
        lines = read_file(path)
        file_chunks = chunk_python_file(path, lines)
        all_chunks.extend(file_chunks)
    return all_chunks
