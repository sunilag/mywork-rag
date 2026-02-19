# Backend Code Documentation Assistant (CLI)
# Overview

This project implements a Code Documentation Assistant for the backend of the fastapi/full-stack-fastapi-template repository.

It ingests the backend source code, builds a vector index using Azure AI Search, and allows developers to ask natural language questions such as:

“Where is authentication implemented?”

“Where is the FastAPI app created?”

“How are database sessions managed?”

The assistant retrieves relevant code chunks and generates grounded answers using Azure OpenAI, always citing file paths and line ranges.

The goal was not just to build a working RAG system, but to structure it in a way that reflects production-grade engineering practices.


# Quick Setup
# Prerequisites

Python 3.10+

Azure AI Search instance

Azure OpenAI resource with:

Embedding deployment (e.g., text-embedding-3-small)

Chat deployment (e.g., gpt-4o)

# Environment Variables

Create a .env file with below contents:

    AZURE_SEARCH_ENDPOINT=https://<your-search>.search.windows.net
    
    AZURE_SEARCH_API_KEY=<key>
    
    AZURE_SEARCH_INDEX=<indexname>
    
    AZURE_OPENAI_ENDPOINT=https://<your-aoai>.openai.azure.com
    
    AZURE_OPENAI_API_KEY=<key>
    
    AZURE_OPENAI_API_VERSION=<yyyy-mm-dd>
    
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=<embedding-deploy-name>
    
    AZURE_OPENAI_CHAT_DEPLOYMENT=<chat-deploy-name>
    
    EMBEDDING_DIM=<dimensions>
    
# Install
create virtual environment with dependencies or pip install -r requirements.txt

# Create Index
python -m app.cli create-index

# Index code base 
Indexed backend code of this repo https://github.com/fastapi/full-stack-fastapi-template

python -m app.cli index /full/path/to/local/cloned/path/full-stack-fastapi-template

# Ask Questions on the indexed code base

python -m app.cli ask "Where is authentication implemented?"

Optional debugging options:
python -m app.cli --azure-debug ask "Where is authentication implemented?" --debug

# Architecture Overview

  # Indexing Pipeline

  <img width="327" height="257" alt="image" src="https://github.com/user-attachments/assets/4512c0b1-0e8d-461f-a825-b9ae81dd1da2" />

  # Retrieval Pipeline

  <img width="438" height="333" alt="image" src="https://github.com/user-attachments/assets/8aa548ce-1533-4abc-b617-f5ced5715043" />


# RAG / LLM Approach & Design Decisions

Scope: Backend-Only

Intentionally indexed only backend/app and excluded alembic migrations,email templates,generated artifacts

This improves retrieval precision and reduces noise.

# Chunking Strategy

Instead of regular fixed-size chunking used top-level class and def blocks when possible, fallback to fixed-size chunks with overlap, preserved start_line and end_line for precise citations

Why or Reasoning behind is:

    Developer questions are symbol-oriented.
    
    Function-level chunks preserve semantic cohesion.
    
    Precise line ranges improve explainability and reduce hallucination risk.

# Embedding Model Choice

selected text-embedding-3-small because:

    Good performance-to-cost ratio
    
    Suitable for a small-to-medium codebase (~1.6k LOC)
    
    Easy to upgrade to larger models if needed
    
    The embedding dimension is configurable via environment variable.

# Vector Database Choice

Azure AI Search was chosen because:

    Managed vector index (HNSW)
    
    Enterprise-ready
    
    Easy scaling
    
    Supports hybrid search (future enhancement)

# Retrieval Strategy

Vector similarity search (top-k)

Per-file diversity guard (limit chunks per file)

Deterministic temperature=0 for answer generation

The diversity guard prevents over-concentration on a single file.

# Prompt & Guardrails

System prompt enforces:

    Use only provided code context
    
    Cite path:start-end
    
    Explicitly say if answer is not found
    
    Do not invent behavior

Thus reduces hallucination risks.

# Observability

Structured logging

    Azure HTTP logs disabled by default
    
    --azure-debug flag for troubleshooting
    
    --debug flag shows retrieved chunks

This keeps normal usage clean while allowing deep inspection when needed.

# Productionization Strategy

To deploy this in production:

# Indexing

    Trigger re-indexing via Git webhook
    
    Incremental indexing using file diffs
    
    Store metadata for version control

# Security

    Replace API keys with Managed Identity
    
    Store secrets in Azure Key Vault
    
    Use Private Endpoints

# Scalability

    Separate indexing service from query API
    
    Host retrieval behind FastAPI or App Service
    
    Add caching for frequent queries

# Quality Controls

    Add automated evaluation suite
    
    Track retrieval precision metrics
    
    Monitor embedding drift over time

# Engineering Standards

Clear separation between indexing and retrieval modules

Deterministic chunk IDs

Idempotent index creation

Batch embedding

Config via environment variables

Minimal external dependencies

Structured logging

CLI designed for extensibility


# How I Used AI Tools

AI coding assistants were used for:

    Exploring Azure SDK patterns
    
    Prototyping chunking approaches
    
    Reviewing alternative architectural options

All major design decisions, tradeoffs, and production considerations were manually evaluated and refined. Generated snippets were reviewed and refactored for clarity and maintainability.


# What I Would Improve With More Time

Add react based UI frontend - Reuse open source codebase to get head start like https://github.com/microsoft/sample-app-aoai-chatGPT

Integrate with SSO & RBAC - IDP , oauth2

Hybrid lexical + vector search

Reranking layer

Automated evaluation scoring

REST API interface

Unit tests and integration tests

Streaming responses



