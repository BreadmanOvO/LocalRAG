"""v1.8 Agent Runtime platform package.

The v1.7 application remains in the repository's existing ``agent`` and
``core`` packages. New v1.8 Runtime code is introduced behind this boundary
and is migrated in vertical slices after the corresponding protocol is
accepted.
"""

__all__ = [
    "api",
    "architectures",
    "capability_packs",
    "collaboration",
    "conversations",
    "contracts",
    "integrations",
    "personas",
    "routing",
    "runtime",
    "sandbox",
    "worker",
]
