"""D01 checks for the v1.8 package boundary.

These tests intentionally verify layout and importability only. Runtime
behavior belongs to the later Day nodes in the v1.8 development plan.
"""

from importlib import import_module
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parents[1] / "agent_platform"
EXPECTED_SUBPACKAGES = (
    "contracts",
    "runtime",
    "routing",
    "architectures",
    "collaboration",
    "conversations",
    "personas",
    "capability_packs",
    "integrations",
    "sandbox",
    "api",
    "worker",
)


def test_agent_platform_boundary_contains_expected_subpackages() -> None:
    assert PACKAGE_ROOT.is_dir()
    for name in EXPECTED_SUBPACKAGES:
        package = PACKAGE_ROOT / name
        assert package.is_dir(), name
        assert (package / "__init__.py").is_file(), name


def test_agent_platform_boundary_is_importable() -> None:
    root = import_module("agent_platform")
    assert set(EXPECTED_SUBPACKAGES).issubset(root.__all__)
    for name in EXPECTED_SUBPACKAGES:
        import_module(f"agent_platform.{name}")
