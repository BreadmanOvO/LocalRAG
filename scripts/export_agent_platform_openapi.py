"""Export the deterministic v1.8 OpenAPI schema for the frontend client."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "frontend" / "openapi.json"
sys.path.insert(0, str(ROOT))

from agent_platform.api import create_app


def main() -> None:
    schema = create_app().openapi()
    TARGET.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
