#!/usr/bin/env python3
"""
Ultimate Skills Pack — Universal Cross-Platform Installer & Agent Bridge
Supports: Windows, macOS, Linux
Supported Agents: Claude Code, Antigravity, OpenCode/Codex, Cursor, Windsurf, Roo/Cline
Zero external dependencies (pure Python 3 standard library).
"""

import os
import sys
import argparse
import platform
import shutil
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / 'skills'
MANIFEST_FILE = REPO_ROOT / 'skills-manifest.json'

IS_WINDOWS = sys.platform == 'win32'
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

HOME = Path.home()

AGENT_DEFAULT_PATHS = {
    'claude': HOME / '.claude' / 'skills',
    'antigravity': HOME / '.gemini' / 'config' / 'skills',
    'gemini': HOME / '.gemini' / 'config' / 'skills',
    'codex': HOME / '.config' / 'opencode' / 'skills',
    'opencode': HOME / '.config' / 'opencode' / 'skills',
    'cursor': HOME / '.cursor' / 'skills',
}

def load_manifest():
    if not MANIFEST_FILE.exists():
        print(f"[!] Error: {MANIFEST_FILE} not found.")
        sys.exit(1)
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def can_symlink():
    test_link = REPO_ROOT / '.symlink_test.tmp'
    target = REPO_ROOT / 'README.md'
    if not target.exists():
        return False
    try:
        if test_link.exists() or test_link.is_symlink():
            test_link.unlink()
        test_link.symlink_to(target)
        test_link.unlink()
        return True
    except OSError:
        return False

def link_or_copy(src_dir: Path, dest_dir: Path, mode: str = 'auto'):
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    if dest_dir.exists() or dest_dir.is_symlink():
        if dest_dir.is_symlink():
            dest_dir.unlink()
        elif dest_dir.is_dir():
            shutil.rmtree(dest_dir)
        else:
            dest_dir.unlink()

    if mode == 'copy':
        shutil.copytree(src_dir, dest_dir)
        return 'copied'

    try:
        # Try symlinking (relative or absolute)
        dest_dir.symlink_to(src_dir.resolve(), target_is_directory=True)
        return 'symlinked'
    except OSError:
        # Fallback to copy on Windows when SeCreateSymbolicLinkPrivilege is absent
        shutil.copytree(src_dir, dest_dir)
        return 'copied (symlink fallback)'

def run_doctor():
    print("=" * 60)
    print(" Ultimate Skills Pack — System Diagnostic & Compatibility Doctor")
    print("=" * 60)
    print(f" OS:                {platform.system()} ({platform.release()})")
    print(f" Platform:          {sys.platform}")
    print(f" Python Version:    {platform.python_version()}")
    print(f" User Home:         {HOME}")
    print(f" Skills Repo Root:  {REPO_ROOT}")
    print(f" Total Skills:      {len(list(SKILLS_DIR.iterdir())) if SKILLS_DIR.exists() else 0}")
    print(f" Native Symlinks:   {'Available (Full Privileges)' if can_symlink() else 'Restricted (Automatic Copy Fallback)'}")
    print("-" * 60)
    print(" Detected Agent Directories on this System:")
    found_any = False
    for agent, path in sorted(AGENT_DEFAULT_PATHS.items()):
        status = "FOUND" if path.exists() else "not found"
        print(f"   - {agent:<14} -> {path} [{status}]")
        if path.exists():
            found_any = True
    if not found_any:
        print("   (No agent folders detected yet; install will create standard paths automatically.)")
    print("=" * 60)

def search_skills(query: str, manifest: dict):
    q = query.lower()
    matches = []
    for s in manifest.get('skills', []):
        if q in s['name'].lower() or q in s['category'].lower() or q in s.get('description', '').lower():
            matches.append(s)
    return matches

def display_info(skill_name: str, manifest: dict):
    skill = next((s for s in manifest.get('skills', []) if s['name'].lower() == skill_name.lower()), None)
    if not skill:
        print(f"[!] Skill '{skill_name}' not found.")
        return
    print("=" * 65)
    print(f" Skill:       {skill['name']}")
    print(f" Category:    {skill['category']}")
    print(f" Path:        {skill['path']}")
    print(f" Files:       {skill['files_count']} (scripts: {'yes' if skill['has_scripts'] else 'no'}, refs: {'yes' if skill['has_references'] else 'no'})")
    print(f" Agents:      {', '.join(skill.get('compatibility', []))}")
    print(f" Platforms:   {', '.join(skill.get('platforms', []))}")
    print("-" * 65)
    print(f" Description:\n {skill.get('description', 'N/A')}")
    print("=" * 65)

def install_skills(skills_to_install, target_dir: Path, mode: str = 'auto', dry_run: bool = False):
    target_dir.mkdir(parents=True, exist_ok=True)
    success = 0
    errors = 0
    method_used = None

    print(f"\n Installing {len(skills_to_install)} skill(s) into: {target_dir}")
    if dry_run:
        print(" [DRY RUN MODE — No files will be modified]")

    for idx, skill in enumerate(skills_to_install, 1):
        name = skill['name']
        src = SKILLS_DIR / name
        dst = target_dir / name
        if not src.exists():
            print(f" [!] Missing source directory: {src}")
            errors += 1
            continue

        if dry_run:
            print(f"   [dry-run] Would install {name} -> {dst}")
            success += 1
            continue

        res = link_or_copy(src, dst, mode=mode)
        method_used = res
        success += 1
        if idx % 100 == 0 or idx == len(skills_to_install):
            print(f"   Progress: {idx}/{len(skills_to_install)} skills installed ({res})...")

    print(f"\n Done! Successfully installed {success} skills into {target_dir} ({method_used or 'completed'}).")
    if errors:
        print(f" Encountered {errors} error(s).")

def generate_cursor_rules(target_dir: Path, skills):
    """Generates a master .cursorrules or .cursor/rules guide file for Cursor."""
    rules_path = target_dir / '.cursorrules'
    lines = [
        "# Cursor Rules — Ultimate Skills Pack Integration",
        "",
        "You have access to the Ultimate Skills Pack loaded in `.cursor/skills/`.",
        "When tackling a task, proactively consult the corresponding specialized skill definition under `.cursor/skills/<skill-name>/SKILL.md`.",
        "",
        "### Key High-Priority Skills by Domain:",
        "- **Clean Code & Refactoring**: `.cursor/skills/clean-code`, `.cursor/skills/refactoring-ui`",
        "- **Debugging**: `.cursor/skills/systematic-debugging`, `.cursor/skills/systematic-debugging`",
        "- **Fullstack & Next.js**: `.cursor/skills/nextjs`, `.cursor/skills/swr`, `.cursor/skills/turborepo`",
        "- **Cloudflare & Vercel**: `.cursor/skills/cloudflare-one`, `.cursor/skills/deploy-to-vercel`",
        "- **UI & Design**: `.cursor/skills/frontend-design`, `.cursor/skills/emil-design-eng`, `.cursor/skills/shadcn-ui`",
        "- **Video & Animation**: `.cursor/skills/remotion`, `.cursor/skills/hyperframes`, `.cursor/skills/motion-isometric`",
        "- **AI & Agents**: `.cursor/skills/agents-sdk`, `.cursor/skills/hindsight-cloud`",
        "",
        f"*Total installed skills: {len(skills)}.*"
    ]
    with open(rules_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f" Generated Cursor integration rule at: {rules_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Ultimate Skills Pack Installer & Multi-Agent Bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py --all                           # Install all skills to all detected agents
  python install.py --agent claude                  # Install all skills to Claude Code (~/.claude/skills)
  python install.py --agent antigravity             # Install to Google Antigravity / Gemini CLI
  python install.py --agent cursor --local          # Install to current project's .cursor/skills
  python install.py --category video --agent claude # Install video skills to Claude Code
  python install.py --search "debugging"            # Search available skills
  python install.py --doctor                        # Run system & permission diagnostics
        """
    )
    parser.add_argument('--all', action='store_true', help='Install all skills to all detected coding agents')
    parser.add_argument('--agent', choices=['claude', 'antigravity', 'gemini', 'codex', 'opencode', 'cursor', 'all'],
                        help='Target agent to install skills for')
    parser.add_argument('--category', help='Install only skills in this category (or comma-separated categories)')
    parser.add_argument('--skill', help='Install specific skill by name (or comma-separated names)')
    parser.add_argument('--target', type=Path, help='Custom destination path')
    parser.add_argument('--local', action='store_true', help='Install to local project directory instead of home')
    parser.add_argument('--mode', choices=['auto', 'symlink', 'copy'], default='auto',
                        help='Installation mode: symlink, copy, or auto (default)')
    parser.add_argument('--search', help='Search skills by keyword')
    parser.add_argument('--info', help='Display details of a specific skill')
    parser.add_argument('--list', action='store_true', help='List all categories and counts')
    parser.add_argument('--doctor', action='store_true', help='Run environment and permission diagnostics')
    parser.add_argument('--dry-run', action='store_true', help='Simulate installation without touching files')

    args = parser.parse_args()
    manifest = load_manifest()
    all_skills = manifest.get('skills', [])

    if args.doctor:
        run_doctor()
        return

    if args.list:
        print("\n=== Ultimate Skills Pack Categories ===")
        for cat, count in sorted(manifest.get('categories', {}).items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat:<26}: {count} skills")
        print(f"\nTotal: {manifest.get('total_skills', 0)} skills across {len(manifest.get('categories', {}))} categories.")
        return

    if args.search:
        results = search_skills(args.search, manifest)
        print(f"\nFound {len(results)} skill(s) matching '{args.search}':")
        for s in results:
            print(f"  • {s['name']:<30} [{s['category']}]")
            print(f"    {s.get('description', '')[:100]}...")
        return

    if args.info:
        display_info(args.info, manifest)
        return

    # Determine skills filter
    selected_skills = all_skills
    if args.category:
        cats = [c.strip().lower() for c in args.category.split(',')]
        selected_skills = [s for s in selected_skills if s['category'].lower() in cats]
        print(f"Filtered by category ({args.category}): {len(selected_skills)} skills matched.")

    if args.skill:
        names = [n.strip().lower() for n in args.skill.split(',')]
        selected_skills = [s for s in selected_skills if s['name'].lower() in names]
        print(f"Filtered by skill name: {len(selected_skills)} skills matched.")

    if not selected_skills:
        print("[!] No skills matched your criteria.")
        return

    # Determine target directories
    targets = []
    if args.target:
        targets.append(args.target)
    elif args.local:
        agent = args.agent or 'claude'
        if agent in ['claude']:
            targets.append(Path.cwd() / '.claude' / 'skills')
        elif agent in ['antigravity', 'gemini']:
            targets.append(Path.cwd() / '.gemini' / 'skills')
        elif agent in ['cursor']:
            target_p = Path.cwd() / '.cursor' / 'skills'
            targets.append(target_p)
            if not args.dry_run:
                generate_cursor_rules(Path.cwd(), selected_skills)
        elif agent in ['codex', 'opencode']:
            targets.append(Path.cwd() / '.codex' / 'skills')
        else:
            targets.append(Path.cwd() / 'skills')
    elif args.all or args.agent == 'all':
        for ag, p in AGENT_DEFAULT_PATHS.items():
            if ag in ['gemini', 'opencode']:  # avoid duplicate paths
                continue
            targets.append(p)
    elif args.agent:
        p = AGENT_DEFAULT_PATHS.get(args.agent)
        if p:
            targets.append(p)
        else:
            print(f"[!] Unknown agent: {args.agent}")
            return
    else:
        # Default interactive behavior if no flags provided: prompt user or default to all detected
        print("\n=== Ultimate Skills Pack Installer ===")
        print("No specific --agent or --target specified.")
        print("Available options:")
        print("  1) Install to ALL detected Coding Agents (Claude Code, Antigravity, OpenCode, Cursor)")
        print("  2) Install to Claude Code (~/.claude/skills)")
        print("  3) Install to Google Antigravity (~/.gemini/config/skills)")
        print("  4) Install to OpenCode / Codex (~/.config/opencode/skills)")
        print("  5) Install locally to current project directory (.cursor/skills, .claude/skills)")
        print("  6) Run Diagnostic Doctor (--doctor)")
        choice = input("\nSelect an option [1-6] (default: 1): ").strip() or "1"
        if choice == "1":
            targets = [AGENT_DEFAULT_PATHS['claude'], AGENT_DEFAULT_PATHS['antigravity'], AGENT_DEFAULT_PATHS['codex'], AGENT_DEFAULT_PATHS['cursor']]
        elif choice == "2":
            targets = [AGENT_DEFAULT_PATHS['claude']]
        elif choice == "3":
            targets = [AGENT_DEFAULT_PATHS['antigravity']]
        elif choice == "4":
            targets = [AGENT_DEFAULT_PATHS['codex']]
        elif choice == "5":
            targets = [Path.cwd() / '.claude' / 'skills', Path.cwd() / '.cursor' / 'skills']
        elif choice == "6":
            run_doctor()
            return
        else:
            print("[!] Invalid option.")
            return

    # Run installation
    for t in targets:
        install_skills(selected_skills, t, mode=args.mode, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
