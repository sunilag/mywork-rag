from __future__ import annotations

import logging
from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from openai import AzureOpenAI

from app.config import load_settings

logger = logging.getLogger(__name__)

def _limit_per_file(chunks: List[dict], max_per_file: int = 3) -> List[dict]:
        """
        Limit number of chunks per file avoding weak answers.
        """
        file_counts = {}
        filtered = []

        for ch in chunks:
            path = ch["path"]
            file_counts[path] = file_counts.get(path, 0)

            if file_counts[path] < max_per_file:
                filtered.append(ch)
                file_counts[path] += 1

        return filtered

class RetrievalService:
    def __init__(self) -> None:
        settings = load_settings()

        self._settings = settings

        self._search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=AzureKeyCredential(settings.azure_search_api_key),
        )

        self._aoai = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )

    def _embed_query(self, query: str) -> List[float]:
        response = self._aoai.embeddings.create(
            model=self._settings.azure_openai_embedding_deployment,
            input=query,
        )
        return response.data[0].embedding
    
    

    def search(self, query: str, k: int = 8) -> List[dict]:
        """
        Search and return top k relevant chunks.
        """
        vector = self._embed_query(query)

        vector_query = VectorizedQuery(
            vector=vector,
            k_nearest_neighbors=k,
            fields="contentVector",
        )

        results = self._search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["chunk_id", "path", "start_line", "end_line", "content", "symbol"],
        )

        chunks = []
        for r in results:
            chunks.append(dict(r))

        return _limit_per_file(chunks)

    
    

