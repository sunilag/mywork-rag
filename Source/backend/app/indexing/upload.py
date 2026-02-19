from __future__ import annotations

import logging
from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from app.config import load_settings
from app.types import Chunk

logger = logging.getLogger(__name__)


def get_search_client() -> SearchClient:
    settings = load_settings()
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=AzureKeyCredential(settings.azure_search_api_key),
    )


def upload_chunks(chunks: List[Chunk], vectors: List[List[float]]) -> None:
    """
    Upload chunk and embedding pairs into Azure AI Search.
    """

    if len(chunks) != len(vectors):
        raise ValueError("Chunks and vectors length mismatch.")

    client = get_search_client()

    docs = []
    for chunk, vector in zip(chunks, vectors):
        docs.append(
            {
                "chunk_id": chunk.chunk_id,
                "path": chunk.path,
                "symbol": chunk.symbol,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "content": chunk.content,
                "contentVector": vector,
            }
        )

    logger.info("Uploading %d documents to Azure AI Search", len(docs))
    result = client.upload_documents(documents=docs)

    failed = [r for r in result if not r.succeeded]
    if failed:
        raise RuntimeError(f"Failed to upload {len(failed)} documents.")

    logger.info("Upload complete.")
