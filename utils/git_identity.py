"""Shared Git path policy for runtime/evaluation identity checks."""

from __future__ import annotations


# Documentation is deliberately excluded from Agent runtime identity. Markdown
# files may be updated after an evaluation without changing executable behavior.
CODE_IDENTITY_PATHSPEC = (
    ".",
    ":(exclude)results/**",
    ":(exclude)RAG_md/**",
    ":(exclude)*.md",
    ":(exclude)**/*.md",
)
