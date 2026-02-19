from __future__ import annotations

import logging
from dataclasses import dataclass

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IndexSpec:
    name: str
    embedding_dim: int
    vector_profile_name: str = "default-profile"
    hnsw_algo_name: str = "hnsw-efx"



def get_index_client(endpoint: str, api_key: str) -> SearchIndexClient:
    return SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))


def build_index(spec: IndexSpec) -> SearchIndex:
    fields = [
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, key=True),
        SearchableField(
            name="path",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="symbol",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
            analyzer_name="en.lucene",
        ),
        SimpleField(name="start_line", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SimpleField(name="end_line", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
            analyzer_name="en.lucene",
        ),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=spec.embedding_dim,
            vector_search_profile_name=spec.vector_profile_name,
        ),
    ]

    algo_name = spec.hnsw_algo_name  # e.g. "hnsw-efx"

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name=algo_name)
        ],
        profiles=[
            VectorSearchProfile(
                name=spec.vector_profile_name,
                algorithm_configuration_name=algo_name,
            )
        ],
    )

    return SearchIndex(
        name=spec.name,
        fields=fields,
        vector_search=vector_search,
    )



def ensure_index(client: SearchIndexClient, spec: IndexSpec) -> None:
    # create if missing else validate if dimensions match.
    try:
        existing = client.get_index(spec.name)
        
        vec_field = next((f for f in existing.fields if f.name == "contentVector"), None)
        if not vec_field:
            raise RuntimeError("Existing index missing 'contentVector' field.")
        if getattr(vec_field, "vector_search_dimensions", None) != spec.embedding_dim:
            raise RuntimeError(
                f"Index '{spec.name}' exists but embedding_dim mismatch: "
                f"index={vec_field.vector_search_dimensions} vs expected={spec.embedding_dim}. "
                "Create a new index name or re-create the index."
            )
        logger.info("Index already exists and is compatible: %s", spec.name)
        return
    except Exception:
        # If get_index fails  create it like first time scenerio.
        # If it fails for another reason, we still show it after create attempt fails.
        pass

    index = build_index(spec)
    client.create_index(index)
    logger.info("Created index: %s", spec.name)
