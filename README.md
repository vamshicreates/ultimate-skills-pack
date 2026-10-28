# ⚡ Ultimate Skills Pack for Coding Agents

[![Skills Count](https://img.shields.io/badge/skills-975%2B-blueviolet?style=for-the-badge&logo=sparkles)](SKILLS_DIRECTORY.md)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D4?style=for-the-badge&logo=windows)](install.py)
[![Agents](https://img.shields.io/badge/agents-Claude%20%7C%20Antigravity%20%7C%20Codex%20%7C%20Cursor%20%7C%20Windsurf%20%7C%20Roo-brightgreen?style=for-the-badge)](skills-manifest.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **The definitive, production-grade library of 975+ Agent Skills bundled into a single repository.**  
> Built for **Windows**, **macOS**, and **Linux**, with 1-click cross-platform installers for **Claude Code**, **Google Antigravity / Gemini CLI**, **OpenCode / OpenAI Codex**, **Cursor**, **Windsurf**, and **Roo/Cline**.

---

## 🌟 Why Ultimate Skills Pack?

Modern AI coding agents (Claude Code, Cursor, Antigravity, OpenCode, Windsurf) are only as capable as the instructions and domain workflows provided to them. Until now, skills have been fragmented across disparate directories, agent-specific formats, broken symlinks, and Unix-only paths that fail on Windows.

**Ultimate Skills Pack** solves this once and for all:
- **975+ Curated Skills**: Deduplicated, normalized, and categorized across 13 domains.
- **100% Cross-Platform**: Native support for **Windows (NTFS)**, **macOS**, and **Linux**. Zero forbidden characters (no `:` colons in folder names), normalized line endings, and sanitized paths.
- **Multi-Agent Bridge**: Symlink or copy skills directly into any agent’s discovery directory with a single command.
- **Automatic Fallback on Windows**: When Windows Developer Mode / symlink privileges are not enabled, the installer seamlessly falls back to directory copies without errors.
- **Zero External Dependencies**: Universal installer runs on pure standard Python 3, native PowerShell, or POSIX bash.

---

## 🚀 Quickstart

### 🪟 Windows (PowerShell or Batch)

Clone and install all skills into all detected coding agents in seconds:

```powershell
# In PowerShell (Run as Administrator or standard user):
git clone https://github.com/vamshicreates/ultimate-skills-pack.git
cd ultimate-skills-pack

# Install into all detected coding agents:
.\install.ps1 -All

# Or install for a specific agent:
.\install.ps1 -Agent claude
.\install.ps1 -Agent antigravity
.\install.ps1 -Agent cursor -Local
```

Or simply double-click **`install.bat`** or run:
```cmd
install.bat --all
```

---

### 🍎 macOS / 🐧 Linux / WSL

```bash
git clone https://github.com/vamshicreates/ultimate-skills-pack.git
cd ultimate-skills-pack

# Universal 1-click installation:
./install.sh --all

# Or target specific agent:
python3 install.py --agent claude
python3 install.py --agent antigravity
python3 install.py --agent codex
python3 install.py --agent cursor --local
```

---

## 🤖 Supported Coding Agents & Paths

| Agent | Default Discovery Path | Installer Flag | Mode |
| :--- | :--- | :--- | :---: |
| **Anthropic Claude Code** | `~/.claude/skills` | `--agent claude` | Global / Local |
| **Google Antigravity / Gemini CLI** | `~/.gemini/config/skills` | `--agent antigravity` | Global / Local |
| **OpenCode / OpenAI Codex** | `~/.config/opencode/skills` | `--agent codex` | Global / Local |
| **Cursor IDE** | `.cursor/skills/` + `.cursorrules` | `--agent cursor` | Project Local |
| **Windsurf IDE** | `.windsurf/skills/` + `.windsurfrules` | `--agent windsurf` | Project Local |
| **Roo Code / Cline** | `.clinerules` | `--agent roo` | Project Local |
| **GitHub Copilot / Aider** | Reads `SKILLS_DIRECTORY.md` & `skills/` | `--target <dir>` | Project Local |

---

## 🗂️ Category Overview (975 Skills)

Explore the full catalogue with clickable links in [**SKILLS_DIRECTORY.md**](SKILLS_DIRECTORY.md).

```
Ultimate Skills Pack (975 Skills)
├── 🎬 Video & Motion Graphics (192 skills)     -> Remotion, Hyperframes, 20 Motion Styles, DaVinci, Premiere
├── 🛠️ Productivity & Tools (123 skills)       -> Defuddle, MinERU, JSON Canvas, Knap, Obsidian, PDF, Automation
├── 💻 Coding & Architecture (114 skills)       -> Systematic Debugging, Clean Code, Refactoring UI, TDD, DDIA
├── 🎨 UI/UX & Design (110 skills)             -> Frontend Design, Emil Design Engineering, Stitch, Figma, Shadcn
├── 📈 Marketing & Growth (91 skills)           -> SEO Suite, Viral Hooks, LinkedIn Writer, Cold Email, CRO
├── 🧠 AI & Agent Engineering (74 skills)       -> Agents SDK, Subagent Dev, Reasoning Traces, Hindsight Memory
├── 🌐 Web & Fullstack (57 skills)              -> Next.js App Router, React, Vite, SWR, Turborepo, Satori
├── 🧬 Science & Bioinformatics (46 skills)     -> AlphaFold, PubChem, ChEMBL, UniProt, ClinVar, GTEx, HPA
├── 📱 Creator & Social (44 skills)             -> Carousels, YouTube Uploader, X Writer, PostOnce, Canva DNA
├── 🏢 Business & Operations (43 skills)        -> MVP Scope, Pricing Strategy, Pitch Deck, First Customers, Job Hunter
├── ☁️ Cloud & DevOps (43 skills)              -> Cloudflare Workers, Durable Objects, Vercel Deploy, Firebase
├── 🎵 Audio & Music (23 skills)               -> Whisper Transcriber, Sound Effects, Voicebox, Lyric Video Producer
└── 🎥 Filmmaking & Story (15 skills)           -> Film to Screenplay, Script Doctor, Screenplay Storyboards
```

---

## 💎 Flagship Skills Spotlight

### 1. Coding, Clean Architecture & Debugging
- **[`systematic-debugging`](skills/systematic-debugging/SKILL.md)**: 4-phase root-cause debugging protocol before proposing any code changes.
- **[`clean-code`](skills/clean-code/SKILL.md)**: Software craft principles, naming, function decomposition, and code smell identification.
- **[`refactoring-ui`](skills/refactoring-ui/SKILL.md)**: Tactful visual design improvements for developers.
- **[`test-driven-development`](skills/test-driven-development/SKILL.md)**: Strict TDD workflow with red-green-refactor cycles.
- **[`using-git-worktrees`](skills/using-git-worktrees/SKILL.md)**: Safe isolated branch and worktree management.

### 2. Video Editing & Motion Graphics
- **[`remotion`](skills/remotion/SKILL.md)** & **[`remotion-best-practices`](skills/remotion-best-practices/SKILL.md)**: Complete programmatic video suite in React.
- **[`hyperframes`](skills/hyperframes/SKILL.md)**: Autonomous frame-by-frame video and animation engine.
- **`20 Motion Graphics Styles`**:
  [`motion-bauhaus`](skills/motion-bauhaus/SKILL.md), [`motion-isometric`](skills/motion-isometric/SKILL.md), [`motion-retro-vhs`](skills/motion-retro-vhs/SKILL.md), [`motion-blueprint`](skills/motion-blueprint/SKILL.md), [`motion-neon-glow`](skills/motion-neon-glow/SKILL.md), [`motion-split-flap`](skills/motion-split-flap/SKILL.md), [`motion-holographic`](skills/motion-holographic/SKILL.md), [`motion-clay-3d`](skills/motion-clay-3d/SKILL.md), [`motion-kinetic-type`](skills/motion-kinetic-type/SKILL.md), and more.
- **[`davinci-color-dna`](skills/davinci-color-dna/SKILL.md)** & **[`premiere-editing-dna`](skills/premiere-editing-dna/SKILL.md)**: NLE automation, style matching, ASC-CDL, and timeline builds.
- **Creator Editing Styles**: Vox, Johnny Harris, Ali Abdaal, MagnatesMedia, Devin Jatho, Maximize, Imperial, Iman Gadzhi.

### 3. AI Agent Systems & Memory
- **[`agents-sdk`](skills/agents-sdk/SKILL.md)**: Cloudflare Agents SDK expert architecture and durable agent workflows.
- **[`subagent-driven-development`](skills/subagent-driven-development/SKILL.md)**: Parallel dispatch and isolated task execution for multi-agent workflows.
- **[`hindsight-cloud`](skills/hindsight-cloud/SKILL.md)** & **[`hindsight-local`](skills/hindsight-local/SKILL.md)**: Long-term persistent memory banks and cognitive recall for AI agents.
- **[`reasoning-trace-optimizer`](skills/reasoning-trace-optimizer/SKILL.md)**: Debug reasoning drift, context degradation, and tool confusion.
- **[`seedance-2-0-prompter`](skills/seedance-2-0-prompter/SKILL.md)** & **[`veo-3-2-prompter`](skills/veo-3-2-prompter/SKILL.md)**: State-of-the-art multimodal video generation prompt engines.

### 4. Fullstack, Web & Cloud
- **[`nextjs`](skills/nextjs/SKILL.md)**: Next.js App Router, Server Actions, PPR, and performance optimization.
- **[`cloudflare-one`](skills/cloudflare-one/SKILL.md)** & **[`durable-objects`](skills/durable-objects/SKILL.md)**: Edge architecture, state coordination, and Zero Trust.
- **[`deploy-to-vercel`](skills/deploy-to-vercel/SKILL.md)** & **[`vercel-api`](skills/vercel-api/SKILL.md)**: CI/CD, cron jobs, edge functions, and routing.
- **[`firebase-firestore`](skills/firebase-firestore/SKILL.md)** & **[`firestore-rules-creation`](skills/firestore-rules-creation/SKILL.md)**: Security rules authoring and live data logic.

### 5. Science & Research
- **[`biomolecular-structure-viewer`](skills/biomolecular-structure-viewer/SKILL.md)**: Interactive sidecar visualization for 3D PDB biomolecules.
- **[`alphafold-database-fetch-and-analyze`](skills/alphafold-database-fetch-and-analyze/SKILL.md)**: AlphaFold protein structure analysis and residue mapping.
- **[`pubchem-database`](skills/pubchem-database/SKILL.md)** & **[`chembl-database`](skills/chembl-database/SKILL.md)**: Chemical informatics, SMILES queries, and bioactivity discovery.

---

## 🛠️ Universal CLI Guide (`install.py`)

The bundled `install.py` provides complete management of your skills library:

```bash
# 1. Run diagnostic check (checks OS, Python, symlink permissions, agent detection)
python install.py --doctor

# 2. Search for skills by keyword
python install.py --search "debugging"
python install.py --search "remotion"
python install.py --search "seo"

# 3. View detailed skill metadata and description
python install.py --info systematic-debugging
python install.py --info hyperframes

# 4. List all categories and counts
python install.py --list

# 5. Filter installation by category
python install.py --category video --agent claude
python install.py --category coding-and-architecture --agent cursor --local

# 6. Install specific skills
python install.py --skill clean-code,systematic-debugging,refactoring-ui --agent claude

# 7. Force copy mode (useful on Windows without Developer Mode)
python install.py --all --mode copy

# 8. Dry run (preview without modifying files)
python install.py --all --dry-run
```

---

## 🪟 Windows NTFS Compatibility Details

Windows filesystems (NTFS/FAT32) have strict constraints compared to Unix filesystems:
1. **Forbidden Characters**: Characters `< > : " / \ | ? *` cannot be present in file or folder names. All skills have been strictly sanitized (e.g. `stitch::manage-design-system` is canonicalized to `stitch-manage-design-system`).
2. **Symlink Privileges**: Standard non-administrator Windows accounts cannot create symbolic links unless Windows Developer Mode is enabled. The `install.py` and `install.ps1` scripts detect this automatically and fall back to full directory copies cleanly.
3. **Line Endings**: `.gitattributes` enforces standard LF for code/markdown and CRLF for `.bat` / `.ps1` files to prevent script execution issues.

---

## 🤝 Contributing

We welcome additions, enhancements, and new domain skills!
1. Fork the repository.
2. Add your skill directory under `skills/<your-skill-name>/` with a valid `SKILL.md` (including `name` and `description` in YAML frontmatter).
3. Run `python install.py --doctor` to verify formatting.
4. Submit a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

Developed with ❤️ by **[Vamshi Creates](https://github.com/vamshicreates)**.
