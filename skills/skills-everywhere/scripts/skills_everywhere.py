#!/usr/bin/env python3
"""Share local Agent Skills across coding agents. Python 3.10+, macOS/Linux."""
from __future__ import annotations

import argparse
import contextlib
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import time

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required. Run install.sh, or: python3 -m pip install -r requirements.txt")

VERSION = "0.1.0"
AGENTS = {
    "agents": ".agents/skills",
    "codex": ".codex/skills",
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
    "antigravity": ".gemini/config/skills",
    "antigravity-legacy": ".gemini/antigravity/skills",
    "antigravity-cli": ".gemini/antigravity-cli/skills",
    "gemini": ".gemini/skills",
    "windsurf": ".codeium/windsurf/skills",
    "devin": ".config/devin/skills",
    "opencode": ".config/opencode/skills",
    "continue": ".continue/skills",
    "copilot": ".copilot/skills",
}
CACHES = [".codex/plugins/cache", ".claude/plugins", ".gemini/antigravity/builtin"]
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".DS_Store", ".pytest_cache"}
FRONT = re.compile(r"\A\ufeff?---[ \t]*\r?\n(.*?)\r?\n---(?:[ \t]*\r?\n|[ \t]*$)", re.S)
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LABEL = "local.skills-everywhere.sync"


class UniqueLoader(yaml.SafeLoader):
    """Reject ambiguous manifests rather than silently accepting duplicate keys."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError("Manifest keys must be unique strings")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def json_read(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else copy.deepcopy(default)


def atomic_text(path, text, private=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8") as output:
        if private:
            os.fchmod(output.fileno(), 0o600)
        output.write(text)
    temp.replace(path)


def json_write(path, data):
    atomic_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", private=True)


def slug(value):
    return (re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "skill")[:64].rstrip("-")


def manifest(path):
    text = path.read_text(encoding="utf-8")
    match = FRONT.match(text)
    if not match:
        raise ValueError("Missing YAML frontmatter")
    meta = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(meta, dict):
        raise ValueError("Frontmatter must be a mapping")
    for key in ("name", "description"):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            raise ValueError("Missing or invalid " + key)
    if len(meta["description"]) > 1024:
        raise ValueError("Description exceeds 1024 characters")
    return meta, text[match.end():]


def walk_skills(root, excluded):
    """Do not descend into generated links, app caches, or symlink cycles."""
    seen = set()
    if not root.is_dir():
        return
    for current, dirs, files in os.walk(root, followlinks=True):
        path = Path(current)
        try:
            real = path.resolve(strict=True)
        except (OSError, RuntimeError):
            dirs[:] = []
            continue
        if any(real.is_relative_to(p) for p in excluded) or real in seen:
            dirs[:] = []
            continue
        seen.add(real)
        keep = []
        for name in sorted(dirs):
            if name in SKIP or name.startswith(".") and name not in {".agents", ".agent", ".claude", ".codex", ".cursor"}:
                continue
            child = path / name
            if child.is_symlink():
                target = Path(os.path.abspath(child.parent / os.readlink(child)))
                if any(target.is_relative_to(p) for p in excluded):
                    continue
            keep.append(name)
        dirs[:] = keep
        if "SKILL.md" in files:
            yield real


def bundle_digest(source):
    """Include supporting files so identical prose cannot hide different scripts."""
    digest = hashlib.sha256()
    for current, dirs, files in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not d.startswith("."))
        for name in sorted(files):
            if name in SKIP or name.startswith("."):
                continue
            path = Path(current) / name
            digest.update(str(path.relative_to(source)).encode() + b"\0")
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
        for name in dirs:
            path = Path(current) / name
            if path.is_symlink():
                # A linked directory's destination is part of its identity.
                digest.update(str(path.relative_to(source)).encode() + b"->" + str(path.resolve()).encode())
    return digest.hexdigest()


class Library:
    def __init__(self, home, root, sources=None, agents=None, all_agents=None, include_caches=None):
        self.home, self.root = Path(home).resolve(), Path(root).resolve()
        self.config = json_read(self.root / "config.json", {"sources": [], "agents": None, "all_agents": False, "include_caches": False})
        if sources is not None:
            self.config["sources"] = list(dict.fromkeys(self.config["sources"] + [str(Path(p).expanduser().resolve()) for p in sources]))
        for key, value in {"agents": agents, "all_agents": all_agents, "include_caches": include_caches}.items():
            if value is not None:
                self.config[key] = value
        self.state = json_read(self.root / "state.json", {"links": {}, "files": {}})
        journal = self.root / "journal.jsonl"
        if journal.exists():
            for line in journal.read_text().splitlines():
                record = json.loads(line)
                if record["target"] is None:
                    self.state["links"].pop(record["path"], None)
                else:
                    self.state["links"][record["path"]] = record["target"]

    def targets(self):
        selected = self.config["agents"]
        return {name: self.home / relative for name, relative in AGENTS.items()
                if selected and name in selected or not selected and (
                    self.config["all_agents"] or name == "agents" or (self.home / relative).parent.is_dir())}

    def scan(self):
        roots = [self.root / "inbox", *[self.home / p for p in AGENTS.values()]]
        roots += [Path(p) for p in self.config["sources"]]
        if self.config["include_caches"]:
            roots += [self.home / p for p in CACHES]
        groups, skipped, seen = {}, [], set()
        excluded = [self.root / "definitions", self.root / "skills"]
        for root in roots:
            for source in walk_skills(root, excluded):
                if source in seen:
                    continue
                seen.add(source)
                try:
                    meta, body = manifest(source / "SKILL.md")
                    digest = bundle_digest(source)
                except (OSError, UnicodeError, ValueError, yaml.YAMLError) as error:
                    skipped.append({"source": str(source), "reason": str(error).splitlines()[0]})
                    continue
                name = slug(meta["name"])
                item = {"base_name": name, "source": str(source), "digest": digest, "metadata": meta, "body": body}
                groups.setdefault(name, {}).setdefault(digest, []).append(item)
        entries, used = [], set(groups)
        for name, versions in sorted(groups.items()):
            for number, copies in enumerate(versions.values()):
                item = copies[0]
                names = [name] if number == 0 else []
                if len(versions) > 1:
                    alias = name[:47].rstrip("-") + "-" + item["digest"][:16]
                    if alias in used:
                        raise ValueError("Generated skill alias collides with an existing name: " + alias)
                    used.add(alias)
                    names.append(alias)
                for install_name in names:
                    entries.append({**item, "name": install_name, "copies": [c["source"] for c in copies]})
        return entries, skipped

    def plan(self, entries, skipped):
        targets = {}
        for agent, root in self.targets().items():
            counts = {"add": 0, "managed": 0, "preserve": 0}
            for entry in entries:
                path = root / entry["name"]
                if not os.path.lexists(path):
                    counts["add"] += 1
                elif self.owned_link(path):
                    counts["managed"] += 1
                else:
                    counts["preserve"] += 1
            targets[agent] = {"path": str(root), **counts}
        return {"version": VERSION, "library": str(self.root), "skill_names": len({e["base_name"] for e in entries}),
                "definitions": len({(e["base_name"], e["digest"]) for e in entries}),
                "entries": len(entries), "targets": targets, "skipped": skipped}

    def owned_link(self, path):
        return path.is_symlink() and self.state["links"].get(str(path)) == os.readlink(path)

    def record_link(self, path, target):
        with (self.root / "journal.jsonl").open("a", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(json.dumps({"path": str(path), "target": str(target) if target is not None else None}) + "\n")

    def link(self, path, target):
        if os.path.lexists(path):
            if not self.owned_link(path):
                return
            if os.readlink(path) == str(target):
                return
            self.record_link(path, target)
            path.unlink()
        else:
            self.record_link(path, target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
        self.state["links"][str(path)] = str(target)

    def owned_file(self, path, text):
        digest = hashlib.sha256(text.encode()).hexdigest()
        previous = self.state["files"].get(str(path))
        if os.path.lexists(path):
            if path.is_symlink() or not path.is_file():
                raise ValueError("Refusing to replace an unmanaged path: " + str(path))
            current = hashlib.sha256(path.read_bytes()).hexdigest()
            if current != digest and current != previous:
                raise ValueError("Generated file was edited; preserving it: " + str(path))
        atomic_text(path, text)
        self.state["files"][str(path)] = digest

    def save(self):
        json_write(self.root / "state.json", self.state)
        (self.root / "journal.jsonl").unlink(missing_ok=True)

    def sync(self):
        entries, skipped = self.scan()
        report = self.plan(entries, skipped)
        for entry in entries:
            folder = self.root / "definitions" / entry["name"]
            folder.mkdir(parents=True, exist_ok=True)
            meta = dict(entry["metadata"], name=entry["name"])
            text = "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True) + "---\n" + entry["body"]
            self.owned_file(folder / "SKILL.md", text)
            assets = set()
            for child in Path(entry["source"]).iterdir():
                if child.name == "SKILL.md" or child.name in SKIP or child.name.startswith("."):
                    continue
                assets.add(child.name)
                self.link(folder / child.name, child)
            for p in list(self.state["links"]):
                old = Path(p)
                if old.parent == folder and old.name not in assets and self.owned_link(old):
                    self.record_link(old, None)
                    old.unlink()
                    del self.state["links"][p]
            self.link(self.root / "skills" / entry["name"], folder)
            for root in self.targets().values():
                self.link(root / entry["name"], self.root / "skills" / entry["name"])
        active = {self.root / "skills" / e["name"] for e in entries}
        active |= {r / e["name"] for r in self.targets().values() for e in entries}
        registration_roots = {self.root / "skills", *[self.home / p for p in AGENTS.values()]}
        active_definitions = {self.root / "definitions" / e["name"] for e in entries}
        for p in list(self.state["links"]):
            path = Path(p)
            obsolete_registration = path.parent in registration_roots and path not in active
            obsolete_asset = path.parent.parent == self.root / "definitions" and path.parent not in active_definitions
            if (obsolete_registration or obsolete_asset) and self.owned_link(path):
                self.record_link(path, None)
                path.unlink()
                del self.state["links"][p]
        self.save()
        catalog = [{k: v for k, v in e.items() if k not in {"metadata", "body"}} for e in entries]
        json_write(self.root / "catalog.json", {"entries": catalog, "skipped": skipped})
        json_write(self.root / "config.json", self.config)
        report["applied"] = True
        json_write(self.root / "last-sync.json", report)
        return report

    def status(self):
        catalog = json_read(self.root / "catalog.json", {"entries": []})
        missing = [p for p in self.state["links"] if not Path(p).exists()]
        replaced = [p for p in self.state["links"] if os.path.lexists(p) and not self.owned_link(Path(p))]
        return {"library": str(self.root), "entries": len(catalog["entries"]), "missing_links": missing,
                "changed_registrations": replaced, "targets": {k: str(v) for k, v in self.targets().items()}}

    def uninstall(self):
        removed, preserved = 0, []
        for p in list(self.state["links"]):
            path = Path(p)
            if path.is_relative_to(self.root):
                continue
            if self.owned_link(path):
                self.record_link(path, None)
                path.unlink()
                del self.state["links"][p]
                removed += 1
            elif os.path.lexists(path):
                preserved.append(p)
        self.save()
        return {"removed_global_links": removed, "changed_paths_preserved": preserved, "library_preserved": True}


@contextlib.contextmanager
def locked(root):
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (root / ".lock").open("a") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        yield


def service_path(home):
    return home / "Library/LaunchAgents" / (LABEL + ".plist")


def service_remove(library):
    path = service_path(library.home)
    if path.exists():
        data = plistlib.loads(path.read_bytes())
        if data.get("WorkingDirectory") != str(library.root):
            raise ValueError("A different library owns the automatic updater")
        result = subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{LABEL}"], capture_output=True)
        if result.returncode not in (0, 3, 36, 113):
            raise ValueError("Could not unload updater: " + result.stderr.decode().strip())
        path.unlink()


def service_install(library, interval):
    if sys.platform != "darwin":
        raise ValueError("Automatic login service currently supports macOS. On Linux use: watch --interval 300")
    if interval < 30:
        raise ValueError("Use a refresh interval of at least 30 seconds")
    path = service_path(library.home)
    logs = library.root / "logs"
    logs.mkdir(exist_ok=True)
    data = {"Label": LABEL, "ProgramArguments": [str(Path(sys.executable).resolve()), str(Path(__file__).resolve()),
            "--home", str(library.home), "--library", str(library.root), "sync"],
            "WorkingDirectory": str(library.root), "StartInterval": interval, "RunAtLoad": True,
            "StandardOutPath": str(logs / "sync.log"), "StandardErrorPath": str(logs / "error.log"),
            "ProcessType": "Background", "Nice": 10}
    if path.exists():
        if plistlib.loads(path.read_bytes()) != data:
            raise ValueError("A different updater already exists; remove it before changing its configuration")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(plistlib.dumps(data))
    domain = f"gui/{os.getuid()}"
    running = subprocess.run(["launchctl", "print", domain + "/" + LABEL], capture_output=True)
    if running.returncode:
        subprocess.run(["launchctl", "bootstrap", domain, str(path)], check=True)
    return {"automatic_sync": True, "interval_seconds": interval, "service": str(path)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home to inspect; useful for isolated validation")
    parser.add_argument("--library", type=Path, help="Local library (default: ~/.local/share/skills-everywhere)")
    parser.add_argument("--source", action="append", help="Additional trusted skill folder; may be repeated")
    parser.add_argument("--agents", help="Comma-separated target IDs; see agents command")
    parser.add_argument("--all-agents", action="store_const", const=True, default=None, help="Prepare every supported global folder")
    parser.add_argument("--include-plugin-caches", action="store_const", const=True, default=None)
    parser.add_argument("command", choices=["plan", "sync", "status", "agents", "watch", "watch-install", "watch-remove", "uninstall"])
    parser.add_argument("--interval", type=int, default=300)
    args = parser.parse_args(argv)
    if args.command == "agents":
        print(json.dumps(AGENTS, indent=2))
        return 0
    if sys.platform == "win32":
        parser.error("Use macOS, Linux, or WSL. Native Windows links are not supported in this release.")
    selected = args.agents.split(",") if args.agents else None
    if selected and set(selected) - set(AGENTS):
        parser.error("Unknown agent IDs: " + ", ".join(sorted(set(selected) - set(AGENTS))))
    root = (args.library or args.home / ".local/share/skills-everywhere").resolve()
    if args.command == "watch" and args.interval < 30:
        parser.error("Use a watch interval of at least 30 seconds")
    def get_library():
        return Library(args.home, root, args.source, selected, args.all_agents, args.include_plugin_caches)
    try:
        if args.command == "plan":
            library = get_library()
            entries, skipped = library.scan()
            result = library.plan(entries, skipped)
            result["applied"] = False
        elif args.command == "watch":
            while True:
                with locked(root):
                    print(json.dumps(get_library().sync()), flush=True)
                time.sleep(args.interval)
        else:
            if args.command in {"uninstall", "watch-remove"}:
                # Unload before taking the sync lock; otherwise launchd can kill a holder while we wait.
                service_remove(get_library()) if sys.platform == "darwin" else None
            with locked(root):
                library = get_library()
                if args.command == "sync":
                    result = library.sync()
                elif args.command == "status":
                    result = library.status()
                elif args.command == "watch-install":
                    result = service_install(library, args.interval)
                elif args.command == "watch-remove":
                    result = {"automatic_sync": False}
                else:
                    result = library.uninstall()
        print(json.dumps(result, indent=2))
        return int(bool(result.get("missing_links")))
    except (OSError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as error:
        print("skills-everywhere: " + str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
