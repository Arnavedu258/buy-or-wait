"""
============================================================
RAG PACKAGE
============================================================

Retrieval-Augmented Generation Layer

Purpose
-------
Provides semantic retrieval for financial messages before
LLM explanation generation.

Pipeline
--------
CSV Messages
      │
      ▼
Embedding Engine
      │
      ▼
Vector Store
      │
      ▼
Retriever
      │
      ▼
Prompt Builder
      │
      ▼
Finance LLM
============================================================
"""

from .embedding import EmbeddingEngine
from .vector_store import VectorStore
from .retriever import SemanticRetriever
from .prompt_builder import PromptBuilder

__version__ = "1.0.0"

__all__ = [
    "EmbeddingEngine",
    "VectorStore",
    "SemanticRetriever",
    "PromptBuilder",
]