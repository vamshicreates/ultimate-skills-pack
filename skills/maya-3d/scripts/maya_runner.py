#!/usr/bin/env python3
"""Launch and verify a Maya scene-building job on Windows or macOS."""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback


def mayapy_candidates() -> list[Path]:
    candidates: list[Path] = []
    override = os.environ.get("MAYA_PYTHON_EXECUTABLE")
    if override:
        candidates.append(Path(override).expanduser())
    on_path = shutil.which("mayapy")
    if on_path:
        candidates.append(Path(on_path))
    patterns = (
        r"C:\Program Files\Autodesk\Maya*\bin\mayapy.exe",
        "/Applications/Autodesk/maya*/Maya.app/Contents/bin/mayapy",
    )
    for pattern in patterns:
        candidates.extend(Path(p) for p in sorted(glob.glob(pattern), reverse=True))
    return list(dict.fromkeys(p.resolve() for p in candidates if p.is_file()))


def _asset_issues(cmds, project: Path) -> list[str]:
    issues: list[str] = []
    for node_type, attribute in (("file", "fileTextureName"), ("imagePlane", "imageName")):
        for node in cmds.ls(type=node_type) or []:
            plug = f"{node}.{attribute}"
            if not cmds.objExists(plug):
                continue
            value = cmds.getAttr(plug)
            if not value:
                continue
            if "<UDIM>" in value or "<f>" in value:
                issues.append(f"Sequence needs manual asset check: {plug} -> {value}")
                continue
            path = Path(value)
            if not path.is_absolute():
                path = Path(cmds.workspace(expandName=value))
            if not path.is_file():
                issues.append(f"Missing asset: {plug} -> {value}")
            elif project not in path.resolve().parents:
                issues.append(f"External asset path: {plug} -> {value}")
    return issues


def _worker(job_path: Path, project: Path) -> int:
    report_path = project / "maya_report.json"
    report: dict[str, object] = {"status": "failed", "job": str(job_path), "project": str(project)}
    initialized = False
    try:
        import maya.standalone

        maya.standalone.initialize(name="python")
        initialized = True
        import maya.cmds as cmds

        report["maya_version"] = cmds.about(version=True)
        for folder in ("scenes", "sourceimages", "images"):
            (project / folder).mkdir(parents=True, exist_ok=True)
        if (project / "workspace.mel").exists():
            cmds.workspace(str(project), openWorkspace=True)
        else:
            cmds.workspace(str(project), newWorkspace=True)
            cmds.workspace(str(project), openWorkspace=True)
            for name in ("scenes", "sourceimages", "images"):
                cmds.workspace(fileRule=(name, name))
            cmds.workspace(saveWorkspace=True)
        cmds.file(new=True, force=True)

        spec = importlib.util.spec_from_file_location("maya_scene_job", job_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load job: {job_path}")
        sys.path.insert(0, str(job_path.parent))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        build = getattr(module, "build", None)
        if not callable(build):
            raise TypeError("Job must define build(project_dir: Path) -> Path")
        scene = Path(build(project)).resolve()
        if scene.suffix.lower() not in (".ma", ".mb"):
            raise ValueError("Job must return a .ma or .mb scene path")
        if project != scene and project not in scene.parents:
            raise ValueError("Native scene must be saved inside the project")
        if not scene.is_file() or scene.stat().st_size == 0:
            raise RuntimeError(f"Native scene was not saved: {scene}")

        cmds.file(new=True, force=True)
        cmds.file(str(scene), open=True, force=True, prompt=False)
        meshes = [
            item for item in (cmds.ls(type="mesh", long=True) or [])
            if not cmds.getAttr(f"{item}.intermediateObject")
        ]
        if not meshes:
            raise RuntimeError("Saved scene reopened but contains no renderable mesh")
        issues = _asset_issues(cmds, project)
        report.update(
            status="passed" if not issues else "needs_review",
            scene=str(scene),
            renderable_meshes=len(meshes),
            cameras=cmds.ls(type="camera") or [],
            asset_issues=issues,
        )
        print(json.dumps(report, indent=2))
        return 0 if not issues else 2
    except Exception as exc:
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()
        print(report["traceback"], file=sys.stderr)
        return 1
    finally:
        project.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if initialized:
            try:
                maya.standalone.uninitialize()
            except Exception:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true", help="List available mayapy executables")
    parser.add_argument("--mayapy", type=Path, help="Explicit mayapy executable")
    parser.add_argument("--job", type=Path, help="Python file exposing build(project_dir)")
    parser.add_argument("--project", type=Path, help="Maya project output directory")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.probe:
        print(json.dumps({"platform": sys.platform, "mayapy": [str(p) for p in mayapy_candidates()]}, indent=2))
        return 0
    if not args.job or not args.project:
        parser.error("--job and --project are required unless --probe is used")
    job = args.job.expanduser().resolve()
    project = args.project.expanduser().resolve()
    if not job.is_file():
        parser.error(f"Job does not exist: {job}")
    if args.worker:
        return _worker(job, project)
    candidates = mayapy_candidates()
    executable = args.mayapy.expanduser().resolve() if args.mayapy else next(iter(candidates), None)
    if executable is None or not executable.is_file():
        parser.error("Maya mayapy not found; install Maya or pass --mayapy PATH")
    command = [str(executable), str(Path(__file__).resolve()), "--worker", "--job", str(job), "--project", str(project)]
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
