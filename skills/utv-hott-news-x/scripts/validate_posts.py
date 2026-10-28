#!/usr/bin/env python3
"""Validate a UTV Hott News X draft without calling X or any external service."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


POST_LIMIT = 280
URL_LENGTH = 23
URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
MANDATORY_REPLY = (
    "Download the UTV Hott News app:\n"
    "Android: https://play.google.com/store/apps/details?id=com.mroads.reporterapp\n"
    "iPhone: https://apps.apple.com/us/app/its-utv-hott-news-telugu/id6755475182"
)


def estimated_x_length(text: str) -> int:
    """Estimate X length by counting every URL as its t.co length."""

    length = 0
    cursor = 0
    for match in URL_RE.finditer(text):
        length += len(text[cursor : match.start()])
        length += URL_LENGTH
        cursor = match.end()
    return length + len(text[cursor:])


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def load_payload(path: str) -> dict[str, Any]:
    if path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("draft JSON must contain an object")
    return value


def validate(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    content_format = payload.get("format")
    if content_format not in {"single", "thread"}:
        errors.append("format must be 'single' or 'thread'")

    posts = payload.get("posts")
    if not isinstance(posts, list) or not posts:
        errors.append("posts must be a non-empty array of strings")
        posts = []

    if content_format == "single" and len(posts) != 1:
        errors.append("single format must contain exactly one post")
    if content_format == "thread" and len(posts) < 2:
        errors.append("thread format must contain at least two posts")

    seen: set[str] = set()
    for index, post in enumerate(posts, start=1):
        if not isinstance(post, str) or not post.strip():
            errors.append(f"post {index} must be a non-empty string")
            continue
        estimated = estimated_x_length(post)
        if estimated > POST_LIMIT:
            errors.append(
                f"post {index} estimated length is {estimated}; limit is {POST_LIMIT}"
            )
        normalized = normalize(post)
        if normalized in seen:
            errors.append(f"post {index} duplicates an earlier post")
        seen.add(normalized)

    if payload.get("cta_reply") != MANDATORY_REPLY:
        errors.append("cta_reply does not exactly match the mandatory app reply")

    source_url = payload.get("source_url")
    if not isinstance(source_url, str) or not source_url.startswith(("http://", "https://")):
        warnings.append("source_url is missing or is not an HTTP(S) URL")

    warnings.append("Confirm final lengths and link rendering in the live X composer.")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a UTV Hott News X draft JSON file."
    )
    parser.add_argument("draft", help="Path to draft JSON, or - for stdin")
    args = parser.parse_args()

    try:
        payload = load_payload(args.draft)
        errors, warnings = validate(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1
    print("OK: draft passed offline validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
