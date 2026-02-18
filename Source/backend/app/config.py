from __future__ import annotations

from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


class Settings(BaseModel):
    # Azure AI Search
    azure_search_endpoint: str = Field(..., alias="AZURE_SEARCH_ENDPOINT")
    azure_search_api_key: str = Field(..., alias="AZURE_SEARCH_API_KEY")
    azure_search_index: str = Field("fastapi-backend-code-v1", alias="AZURE_SEARCH_INDEX")

    # Azure OpenAI
    azure_openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field("2024-10-21", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_embedding_deployment: str = Field(..., alias="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    azure_openai_chat_deployment: str = Field(..., alias="AZURE_OPENAI_CHAT_DEPLOYMENT")

    # Embedding dimensions mathing embedding model
    embedding_dim: int = Field(1536, alias="EMBEDDING_DIM")

    # Runtime
    log_level: str = Field("INFO", alias="LOG_LEVEL")


def load_settings(env_file: str | None = None) -> Settings:
    # Load .env if present and then create Settings instance from environment variables
    load_dotenv(dotenv_path=env_file, override=False)
    data = {k: v for k, v in os.environ.items()}
    return Settings.model_validate(data)
