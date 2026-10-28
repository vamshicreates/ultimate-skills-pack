# Indian Film Crew Options

Codex skill for proposing two crew packages from the live Indian Film Technician Database. The repository also includes a blank [Excel template](assets/Indian_Film_Technician_Template.xlsx) with 114 role tabs.

## Install

Clone this repository into the Codex skills directory, or copy the repository folder there. Keep the folder name `indian-film-crew-options`.

**macOS**

```sh
git clone https://github.com/vamshicreates/indian-film-crew-options.git "$HOME/.codex/skills/indian-film-crew-options"
```

**Windows PowerShell**

```powershell
git clone https://github.com/vamshicreates/indian-film-crew-options.git "$env:USERPROFILE\.codex\skills\indian-film-crew-options"
```

Use `$indian-film-crew-options` with a film brief and budget. The skill reads the live Google Sheet through the Google Drive connector each time. The included Excel workbook is a blank offline template, not a synchronized copy of the live database.
