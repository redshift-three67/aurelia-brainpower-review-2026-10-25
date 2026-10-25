"""
LLM Integration für Morphic Engine V1.

Unterstützt lokale LLM-Modelle via Ollama.
"""

from .ollama_client import (
    OllamaClient,
    get_ollama_client,
    generate_description_cached,
)

__all__ = [
    "OllamaClient",
    "get_ollama_client",
    "generate_description_cached",
]
