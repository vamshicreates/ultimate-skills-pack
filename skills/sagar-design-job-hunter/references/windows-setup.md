# Windows setup and dependency check

Use this reference only for installation, upgrades, or device troubleshooting.

## Requirements

- Codex Desktop or another agent host that supports `SKILL.md` skills
- Python 3.9 or newer for `scripts/batch_state.py`
- Live web search or browser access in the agent host for current job discovery
- Outbound HTTPS access to GitHub and job/portfolio sites

The skill does **not** require Node.js, npm, Chrome automation, PyYAML, a PDF library, a resume parser, or any third-party Python package. Git is optional because the system `skill-installer` downloads public GitHub repositories directly and uses Git only as a fallback.

## Recommended installation

Use the preinstalled `$skill-installer` system skill to install the repository root:

- Repository: `vamshicreates/sagar-design-job-hunter`
- Path: `.`
- Installed name: `sagar-design-job-hunter`
- Destination: the normal user Codex skills directory, typically `%USERPROFILE%\.codex\skills`

Do not clone the skill inside an unrelated project. If the target directory already exists, do not overwrite it blindly. Confirm it is this same skill, then update it safely or stop and report the conflict.

## Select Python on Windows

Try launchers in this order:

1. `py -3`
2. `python`

Confirm the selected interpreter is Python 3.9 or newer. If Python is absent, ask before installing it. A typical Windows package-manager command is `winget install --exact --id Python.Python.3.12`, but availability and organizational policy vary.

## Verify after installation

From a normal user-writable job-search workspace, run:

```powershell
$SkillPath = Join-Path $env:USERPROFILE ".codex\skills\sagar-design-job-hunter"
py -3 (Join-Path $SkillPath "scripts\doctor.py") --network
```

If `py` is unavailable but `python` works, replace `py -3` with `python`.

Expected result: JSON with `"status": "READY"`, all required files set to `true`, an empty `third_party_python_packages_required` array, and a successful batch-state check. A failed direct Python network probe appears as a warning because sandboxed terminals may block it; separately verify that the agent's web or browser tool can open the GitHub repository and Behance profile.

## State location

Run the skill from a dedicated job-search workspace such as `%USERPROFILE%\Documents\Sagar-Job-Search`. The helper creates `.job-hunter\sagar-design-job-hunter\state.json` under the current workspace. This keeps feedback history separate from the installed skill and survives skill updates.

## Load behavior

Newly installed skills are normally discovered on the next Codex turn. For an immediate first run in the same task, the agent may read the installed `SKILL.md` directly after the doctor succeeds. Future turns can invoke `$sagar-design-job-hunter` normally.
