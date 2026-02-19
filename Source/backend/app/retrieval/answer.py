from __future__ import annotations

from typing import List

from openai import AzureOpenAI

from app.config import load_settings


def build_context(chunks: List[dict]) -> str:
    sections = []
    for i, ch in enumerate(chunks, 1):
        sections.append(
            f"[Source {i}] {ch['path']}:{ch['start_line']}-{ch['end_line']}\n"
            f"{ch['content']}\n"
        )
    return "\n\n".join(sections)


def generate_answer(question: str, chunks: List[dict]) -> str:
    """
        Generate an answer grounded in retrieved code chunks.
    """
    settings = load_settings()

    client = AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_endpoint=settings.azure_openai_endpoint,
    )

    context = build_context(chunks)

    system_prompt = (
        "You are a backend code assistant.\n"
        "Use ONLY the provided code context to answer.\n"
        "If the answer cannot be found in the provided code, say:\n"
        "'I could not find this in the indexed backend code.'\n"
        "Always cite sources using the format: path:start-end.\n"
        "Do not invent files, functions, or behavior."
    )

    user_prompt = f"""
Question:
{question}

Code Context:
{context}
"""

    response = client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    return response.choices[0].message.content
