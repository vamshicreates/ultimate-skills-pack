#!/usr/bin/env python3
"""Check whether this skill can run on the current Windows/macOS/Linux device."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List


MINIMUM_PYTHON = (3, 9)
NETWORK_TARGETS = {
    "github_repository": "https://github.com/vamshicreates/sagar-design-job-hunter",
    "behance_profile": "https://www.behance.net/sagardabherao",
}


def check_network(url: str) -> Dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 SagarDesignJobHunterDoctor/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            return {"reachable": True, "status": response.status}
    except urllib.error.HTTPError as exc:
        # A 4xx response still proves DNS, TLS, and outbound HTTPS work. Behance
        # may challenge non-browser clients, so report the status without failing.
        return {"reachable": exc.code < 500, "status": exc.code}
    except Exception as exc:  # Network failures differ across Windows versions.
        return {"reachable": False, "error": f"{type(exc).__name__}: {exc}"}


def run_batch_helper(skill_root: Path) -> Dict[str, object]:
    helper = skill_root / "scripts" / "batch_state.py"
    with tempfile.TemporaryDirectory(prefix="sagar-job-hunter-doctor-") as temp_dir:
        result = subprocess.run(
            [sys.executable, str(helper), "--state-dir", temp_dir, "show"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "error": result.stderr.strip() or None,
    }


def build_report(include_network: bool) -> Dict[str, object]:
    skill_root = Path(__file__).resolve().parent.parent
    required_files = [
        "SKILL.md",
        "agents/openai.yaml",
        "references/candidate-profile.md",
        "references/job-batch-method.md",
        "references/windows-setup.md",
        "scripts/batch_state.py",
        "scripts/doctor.py",
    ]
    files = {name: (skill_root / name).is_file() for name in required_files}
    python_ok = sys.version_info >= MINIMUM_PYTHON

    write_test_ok = False
    write_test_error = None
    try:
        with tempfile.TemporaryDirectory(prefix="sagar-job-hunter-write-") as temp_dir:
            probe = Path(temp_dir) / "probe.json"
            probe.write_text("{}\n", encoding="utf-8")
            write_test_ok = probe.read_text(encoding="utf-8") == "{}\n"
    except Exception as exc:
        write_test_error = f"{type(exc).__name__}: {exc}"

    helper = run_batch_helper(skill_root) if python_ok and all(files.values()) else {"ok": False, "skipped": True}
    network = {name: check_network(url) for name, url in NETWORK_TARGETS.items()} if include_network else {}
    network_ok = all(item.get("reachable") for item in network.values()) if include_network else True
    ready = python_ok and all(files.values()) and write_test_ok and bool(helper.get("ok"))

    actions: List[str] = []
    if not python_ok:
        actions.append("Install Python 3.9 or newer, then rerun this doctor.")
    if not all(files.values()):
        actions.append("Reinstall the skill because required files are missing.")
    if not write_test_ok:
        actions.append("Run from a user-writable job-search folder.")
    if python_ok and not helper.get("ok"):
        actions.append("Reinstall or repair scripts/batch_state.py.")
    warnings: List[str] = []
    if include_network and not network_ok:
        warnings.append(
            "Direct Python HTTPS is restricted. This is not a local runtime failure; "
            "verify that the agent's web or browser tool can reach live job sites."
        )

    return {
        "status": "READY" if ready else "ACTION_NEEDED",
        "platform": platform.platform(),
        "windows": os.name == "nt",
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "minimum": ".".join(map(str, MINIMUM_PYTHON)),
            "ok": python_ok,
        },
        "skill_root": str(skill_root),
        "required_files": files,
        "temporary_write_test": {"ok": write_test_ok, "error": write_test_error},
        "batch_state_helper": helper,
        "network": network,
        "third_party_python_packages_required": [],
        "agent_capabilities_required": ["live web search or browser access"],
        "actions": actions,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="Also check outbound HTTPS to the source sites")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON")
    args = parser.parse_args()
    report = build_report(args.network)
    print(json.dumps(report, indent=None if args.compact else 2, ensure_ascii=True))
    return 0 if report["status"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
