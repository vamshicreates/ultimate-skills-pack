#!/usr/bin/env python3
"""Rank likely screenplay files in a local project directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".fdx", ".fountain", ".txt"}
PREFERRED_WORDS = ("locked", "lock", "final", "shooting", "production")
EXCLUDED_PARTS = {".git", "node_modules", "vendor", "dist", "build", "output"}


def candidate_score(path: Path) -> tuple[int, float]:
    name = path.stem.casefold()
    word_score = sum(1 for word in PREFERRED_WORDS if word in name)
    return word_score, path.stat().st_mtime


def discover(root: Path) -> list[dict[str, object]]:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in SUPPORTED_EXTENSIONS:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        candidates.append(path)

    candidates.sort(key=candidate_score, reverse=True)
    results: list[dict[str, object]] = []
    for rank, path in enumerate(candidates, start=1):
        stat = path.stat()
        results.append(
            {
                "rank": rank,
                "path": str(path.resolve()),
                "format": path.suffix.casefold().lstrip("."),
                "size_bytes": stat.st_size,
                "modified_epoch": stat.st_mtime,
                "preferred_name_matches": [
                    word for word in PREFERRED_WORDS if word in path.stem.casefold()
                ],
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Project directory to scan")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    print(json.dumps({"root": str(root), "candidates": discover(root)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
