from __future__ import annotations

import typer
from rich import print

from app.config import load_settings
from app.logging import setup_logging

app = typer.Typer(add_completion=False)


@app.callback()
def main(
    env_file: str = typer.Option(None, help="Optional path to .env file")
):
    """
    Backend Code for my Documentation Assistant work
    """
    settings = load_settings(env_file=env_file)
    setup_logging(settings.log_level)


@app.command()
def health():
    """
    Validate configuration and connectivity basics.
    """
    settings = load_settings()

    print("[green]Config OK[/green]")
    print(f"Search endpoint: {settings.azure_search_endpoint}")
    print(f"Search index:    {settings.azure_search_index}")
    print(f"AOAI endpoint:   {settings.azure_openai_endpoint}")
    print(f"Embed deploy:    {settings.azure_openai_embedding_deployment}")
    print(f"Chat deploy:     {settings.azure_openai_chat_deployment}")
    print(f"Embed dim:       {settings.embedding_dim}")


if __name__ == "__main__":
    app()
