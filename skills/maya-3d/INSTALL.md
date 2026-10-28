# Install Maya 3D for Codex

This is a Codex skill. Autodesk Maya is a separate application and must be installed and licensed to create or verify a native scene. No Maya plug-in is installed by this package.

The Three.js blockout and review application requires Node.js `20.19` or newer in the supported Vite range. From `viewer/`, run `npm install` once after installing or updating the skill.

## macOS

Place the `maya-3d` folder at `${CODEX_HOME:-$HOME/.codex}/skills/maya-3d`. On the Mac where this skill was built, that path is already linked to the workspace copy. Start a new Codex chat and invoke `$maya-3d` with an image or scene brief.

## Windows

Extract the zip so its `maya-3d` folder is at `%CODEX_HOME%\skills\maya-3d` if `CODEX_HOME` is set, or `%USERPROFILE%\.codex\skills\maya-3d` otherwise. Start a new Codex chat and invoke `$maya-3d` with an image or scene brief.

## Check Maya execution

Run `python scripts/maya_runner.py --probe` from the skill folder. It should list an installed `mayapy`. If Maya is in a custom location, pass `--mayapy` when running a job or set `MAYA_PYTHON_EXECUTABLE` to the executable path. The skill can still write the Maya build script when Maya is unavailable, but native scene and render validation then remain pending.
