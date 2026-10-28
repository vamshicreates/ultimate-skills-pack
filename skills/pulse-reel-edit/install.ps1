# pulse-reel-edit installer for Windows (PowerShell 5+).
#   powershell -ExecutionPolicy Bypass -File .\install.ps1              venv + packages + doctor
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -LinkSkills  also link into ~\.claude\skills, ~\.agents\skills, ~\.codex\skills
param([switch]$LinkSkills)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

function Invoke-Py([string]$cand, [string[]]$rest) {
  $parts = $cand.Split(" ")
  $pre = @()
  if ($parts.Length -gt 1) { $pre = $parts[1..($parts.Length - 1)] }
  & $parts[0] @pre @rest
}

$py = $null
foreach ($cand in @("py -3.13", "py -3.12", "py -3.11", "py -3.10", "python", "python3")) {
  try {
    Invoke-Py $cand @("-c", "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)") 2>$null
    if ($LASTEXITCODE -eq 0) { $py = $cand; break }
  } catch {}
}
if (-not $py) { Write-Host "Python 3.10+ not found. Install it from python.org and tick 'Add python.exe to PATH'."; exit 1 }
Write-Host "Using $py"

$vpy = Join-Path $Here ".venv\Scripts\python.exe"
if (-not (Test-Path $vpy)) {
  Invoke-Py $py @("-m", "venv", ".venv")
}
& $vpy -m pip install -q --upgrade pip
& $vpy -m pip install -q -r requirements.txt
& $vpy -m pip install -q -r requirements-titles.txt
if ($LASTEXITCODE -ne 0) { Write-Host "NOTE: rembg (titles behind the subject) did not install. Titles will sit in front." }

if ($LinkSkills) {
  foreach ($d in @("$HOME\.claude\skills", "$HOME\.agents\skills", "$HOME\.codex\skills")) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
    $tgt = Join-Path $d "pulse-reel-edit"
    if ((Resolve-Path $d).Path + "\pulse-reel-edit" -eq $Here) { continue }
    if (Test-Path $tgt) { Write-Host "  exists: $tgt" }
    else { New-Item -ItemType Junction -Path $tgt -Target $Here | Out-Null; Write-Host "  linked: $tgt" }
  }
}

& $vpy pulse.py doctor
Write-Host ""
Write-Host "Done. Python for this skill: $vpy"
Write-Host "FilmCraft (optional): claude mcp add filmcraft -- `"$env:LOCALAPPDATA\Programs\ArtCraft\FilmCraft\filmcraft-cli.exe`" mcp"
