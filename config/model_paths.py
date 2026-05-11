"""Centralized local model path resolution.

All local model paths are relative to the repo root (models/ directory).
Falls back to HuggingFace model names if local models are not available.
"""
from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_MODELS_DIR = _REPO_ROOT / "models"

BGE_M3_LOCAL = str(_MODELS_DIR / "bge-m3")
BGE_RERANKER_BASE_LOCAL = str(_MODELS_DIR / "bge-reranker-base")

BGE_M3_HF = "BAAI/bge-m3"
BGE_RERANKER_BASE_HF = "BAAI/bge-reranker-base"


def get_bge_m3_path() -> str:
    """Return local path if available, else HuggingFace model name."""
    return BGE_M3_LOCAL if (_MODELS_DIR / "bge-m3").exists() else BGE_M3_HF


def get_bge_reranker_path() -> str:
    """Return local path if available, else HuggingFace model name."""
    return BGE_RERANKER_BASE_LOCAL if (_MODELS_DIR / "bge-reranker-base").exists() else BGE_RERANKER_BASE_HF
