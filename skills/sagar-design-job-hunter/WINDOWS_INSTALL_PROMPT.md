# Paste this into Codex on the Windows laptop

```text
Install and run the public Codex skill from https://github.com/vamshicreates/sagar-design-job-hunter on this Windows computer.

Use the preinstalled $skill-installer workflow. Install the repository root (`--path .`) with the name `sagar-design-job-hunter` into my normal user Codex skills directory (normally `%USERPROFILE%\.codex\skills`). Do not install it inside my current project and do not overwrite an unrelated existing folder. If the target already contains this same skill, update it safely; otherwise stop and explain the conflict.

Before running it, inspect `references/windows-setup.md`. Detect a Python 3.9+ launcher by trying `py -3` first and then `python`. If Python is missing or too old, ask for my approval before installing Python 3.12 with the available Windows package manager. Do not install Node.js, npm, PyYAML, Chrome automation packages, PDF libraries, or any other dependency—the skill does not need them.

Create or use the user-writable workspace `%USERPROFILE%\Documents\Sagar-Job-Search`. From that workspace, run the installed `scripts\doctor.py --network` with the detected Python launcher. Continue only if it reports `status: READY`. If it reports `ACTION_NEEDED`, fix only the listed problem and rerun the doctor; do not bypass failed checks. A direct-Python network warning is acceptable when the terminal is sandboxed, but in that case verify with your own web/browser tool that both the GitHub repository and Behance profile are reachable before searching.

After the doctor passes, read the installed `SKILL.md` and its two job-search references directly so you can use the skill in this same task. Then run the first live search for Sagar Dabherao and return the best verified Hyderabad/Secunderabad industrial, physical-product, furniture, CMF, lighting, prototyping, or product-visualization roles, following the skill's five-job batch rules. Do not substitute software UI/UX jobs, generic graphic-design jobs, Bangalore roles, or unverified listings. Do not invent salary or experience. Save the batch history in the workspace, not inside the installed skill.

Finish by showing: the installed skill path, Python version, doctor status, state-file path, and the first verified job batch. Do not apply to any job or submit any form.
```
