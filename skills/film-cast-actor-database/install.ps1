param([switch]$Force)

$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$skillDest = Join-Path (Join-Path $codexRoot 'skills') 'film-cast-actor-database'

if (Test-Path -LiteralPath $skillDest) {
    if (-not $Force) {
        throw "Already installed at $skillDest. Run ./install.ps1 -Force to replace it."
    }
    Remove-Item -LiteralPath $skillDest -Recurse -Force
}

New-Item -ItemType Directory -Path $skillDest -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $skillRoot 'SKILL.md') -Destination $skillDest
foreach ($folder in @('agents', 'references', 'templates')) {
    Copy-Item -LiteralPath (Join-Path $skillRoot $folder) -Destination $skillDest -Recurse
}
Write-Output "Installed film-cast-actor-database at $skillDest"
Write-Output 'Start a new Codex turn, then call $film-cast-actor-database.'
