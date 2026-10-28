#!/usr/bin/env python3
"""Manage only Model Guide's marked block in global Codex instructions."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sys
import uuid

START = b"<!-- codex-model-guide:start -->"
END = b"<!-- codex-model-guide:end -->"


def locate(data):
    if START not in data and END not in data:
        return None
    if data.count(START) != 1 or data.count(END) != 1:
        raise ValueError("Ambiguous markers; review AGENTS.md manually before continuing.")
    start = data.index(START)
    end = data.index(END) + len(END)
    if end < start:
        raise ValueError("Invalid marker order; review AGENTS.md manually.")
    return start, end


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "uninstall", "status"])
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.codex_home.expanduser().resolve()
    target = root / "AGENTS.md"
    if target.is_symlink():
        raise ValueError("AGENTS.md is a symlink; manage its destination explicitly.")
    data = target.read_bytes() if target.exists() else b""
    span = locate(data)
    override = root / "AGENTS.override.md"
    if override.exists() and override.stat().st_size:
        print("Notice: AGENTS.override.md exists and may take precedence over AGENTS.md.")
    if args.action == "status":
        print(f"{'Enabled' if span else 'Not enabled'}: {target}")
        return
    if args.action == "install":
        policy = (Path(__file__).resolve().parents[1] / "policy.md").read_bytes().rstrip()
        block = START + b"\n\n" + policy + b"\n" + END
        if span:
            updated = data[:span[0]] + block + data[span[1]:]
        else:
            updated = data + block
    else:
        updated = data[:span[0]] + data[span[1]:] if span else data
    if updated == data:
        print(f"No change needed: {target}")
        return
    if args.dry_run:
        print(f"Would {args.action} Model Guide in {target}")
        if args.action == "install":
            print(policy.decode())
        return
    root.mkdir(parents=True, exist_ok=True)
    if target.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = root / f"AGENTS.md.model-guide-backup-{stamp}-{uuid.uuid4().hex[:8]}"
        shutil.copy2(target, backup)
        print(f"Backup: {backup}")
    target.write_bytes(updated)
    print(f"{args.action.capitalize()} complete: {target}")
    if args.action == "install":
        print("Routing applies to each actionable instruction, including follow-up tasks in existing chats.")
        print("Already-open chats may need to load the updated rule. Paste this into each existing chat:")
        print((Path(__file__).resolve().parents[1] / "activation-prompt.txt").read_text())
    else:
        print("Start a new chat or tell existing chats to stop using Model Guide's routing rule.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
