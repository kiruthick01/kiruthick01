#!/usr/bin/env python3
"""Decide whether the profile art should be regenerated today.

Only signal a refresh when GitHub shows real contribution activity on
today's or yesterday's calendar cell. This keeps the workflow from
committing on days with zero real activity, which was creating fake
lone-green-square commits during otherwise inactive stretches.
"""
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_PATH = REPO_ROOT / "data" / "contributions.json"


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    recent = data["days"][-2:]
    has_activity = any(d["count"] > 0 for d in recent)

    print(f"Recent days: {recent} -> has_activity={has_activity}")

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a") as f:
            f.write(f"has_activity={'true' if has_activity else 'false'}\n")


if __name__ == "__main__":
    main()
