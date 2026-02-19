from __future__ import annotations

import logging
from typing import List

from openai import AzureOpenAI

from app.config import load_settings
from app.types import Chunk

logger = logging.getLogger(__name__)


class AzureEmbeddingClient:
    """
    wrapper for Azure OpenAI embeddings..
    """

    def __init__(self) -> None:
        settings = load_settings()
        self._deployment = settings.azure_openai_embedding_deployment

        self._client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of texts and validate embedding dimensionality.

        """
        response = self._client.embeddings.create(
            model=self._deployment,
            input=texts,
        )

        
        return [item.embedding for item in response.data]


def embed_chunks(chunks: List[Chunk], batch_size: int = 32) -> List[List[float]]:
    """
    Batch embed chunks.
    """
    client = AzureEmbeddingClient()
    vectors: List[List[float]] = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.content for c in batch]

        logger.info("Embedding batch %d-%d", i, i + len(batch))

        batch_vectors = client.embed_texts(texts)
        vectors.extend(batch_vectors)

    return vectors
