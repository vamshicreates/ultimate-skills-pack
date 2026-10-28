# Film cast actor database skill

A portable Codex skill that takes a film title or IMDb link, researches its credited cast and each performer's recent work, and publishes a sourced actor database to a connected Google Sheet.

## Install

Requirements: Codex, Git, and a connected Google Drive/Sheets capability if you want direct cloud output. No Google credentials are included in this repository.

**macOS / Linux**

```bash
git clone https://github.com/vamshicreates/film-cast-actor-database-skill.git
cd film-cast-actor-database-skill
./install.sh
```

**Windows PowerShell**

```powershell
git clone https://github.com/vamshicreates/film-cast-actor-database-skill.git
cd film-cast-actor-database-skill
./install.ps1
```

The installer copies this folder to `${CODEX_HOME}/skills/film-cast-actor-database` or `~/.codex/skills/film-cast-actor-database`. It refuses to overwrite an existing installation unless `--force` (shell) or `-Force` (PowerShell) is given. Start a new Codex turn after installation.

## Connect Google Sheets

In Codex, connect the Google Drive app or another Google Sheets writer and sign in to the Google account that should own the output. Confirm the assistant can create and edit a Sheet in that account. Then call the skill with a film title or URL:

```text
Use $film-cast-actor-database for Pushpa: The Rise (2021).
Publish the results to my connected Google Sheet account.
```

The skill writes a native Google Sheet when a connected writer is available. Each machine or Codex account needs its own Google authorization; installing the skill does not copy an account connection. If no cloud writer is connected, the skill creates a local workbook and reports that cloud publishing is unavailable.

## Output template

[`templates/actor_database_template.xlsx`](templates/actor_database_template.xlsx) is a blank, formatted two-tab workbook. The two CSV files in `templates/` document the exact headers for integrations that prefer CSV:

- **Actors:** name, potential roles, real age, checked date, Instagram URL, source URL.
- **Film evidence:** up to three recent released feature-film credits per actor, in separate rows, with character, note, and IMDb/source URL.

The template is intentionally blank so it can be reused for any film. A completed run returns its own Google Sheet URL to the requester.

## Updating

Pull changes in the cloned repository and run the installer again with `--force` or `-Force`. The live Google Sheets created with the skill are independent of the installed files.
