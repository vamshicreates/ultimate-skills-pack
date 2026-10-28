# Skills Everywhere v0.1.0

An Agent Skill and local installer for sharing existing skill bundles across coding agents.

- Discover skills in existing agent folders and explicitly supplied collections.
- Register them through one local library and global symbolic links.
- Preserve existing skills and retain conflicting bundles under explicit variant names.
- Fingerprint supporting files and safely parse YAML metadata.
- Refresh automatically at login and every five minutes on macOS; use a foreground watcher on Linux/WSL.
- Inspect registration state and undo the installer's own global links.

Requires Python 3.10+, Git for the bootstrap, and macOS or Linux/WSL. The installer creates an isolated environment with PyYAML 6.0.3.

Filesystem behavior is checked in isolated homes. Cross-agent execution still depends on the receiving agent's capabilities. MCP tools, credentials, cloud sessions, and native Windows are outside the installer.

No personal or third-party skill collection is bundled.
