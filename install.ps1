<#
.SYNOPSIS
    Ultimate Skills Pack — Windows PowerShell Installer & Multi-Agent Bridge
.DESCRIPTION
    Installs 975+ agent skills into Claude Code, Antigravity, OpenCode/Codex, Cursor, Windsurf, or custom folders on Windows.
.EXAMPLE
    .\install.ps1 -All
    .\install.ps1 -Agent claude
    .\install.ps1 -Agent antigravity
    .\install.ps1 -Agent cursor -Local
    .\install.ps1 -Category video
    .\install.ps1 -Doctor
#>

param(
    [switch]$All,
    [string]$Agent = "",
    [string]$Category = "",
    [string]$Skill = "",
    [string]$Target = "",
    [switch]$Local,
    [ValidateSet("auto", "copy", "symlink")]
    [string]$Mode = "auto",
    [string]$Search = "",
    [string]$Info = "",
    [switch]$List,
    [switch]$Doctor,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Ultimate Skills Pack — Windows Installer & Agent Bridge" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# If Python is available, forward all arguments to install.py for identical universal execution
if ($PythonCmd) {
    Write-Host "[i] Python 3 detected. Running universal installer..." -ForegroundColor Green
    $PyArgs = @()
    if ($All) { $PyArgs += "--all" }
    if ($Agent) { $PyArgs += "--agent"; $PyArgs += $Agent }
    if ($Category) { $PyArgs += "--category"; $PyArgs += $Category }
    if ($Skill) { $PyArgs += "--skill"; $PyArgs += $Skill }
    if ($Target) { $PyArgs += "--target"; $PyArgs += $Target }
    if ($Local) { $PyArgs += "--local" }
    if ($Mode) { $PyArgs += "--mode"; $PyArgs += $Mode }
    if ($Search) { $PyArgs += "--search"; $PyArgs += $Search }
    if ($Info) { $PyArgs += "--info"; $PyArgs += $Info }
    if ($List) { $PyArgs += "--list" }
    if ($Doctor) { $PyArgs += "--doctor" }
    if ($DryRun) { $PyArgs += "--dry-run" }

    & python (Join-Path $ScriptDir "install.py") $PyArgs
    exit $LASTEXITCODE
}

# Native PowerShell fallback if Python is not installed
Write-Host "[i] Python not detected. Running native PowerShell installer fallback..." -ForegroundColor Yellow

$SkillsSource = Join-Path $ScriptDir "skills"
$ManifestPath = Join-Path $ScriptDir "skills-manifest.json"

if (-not (Test-Path $SkillsSource)) {
    Write-Error "[!] Skills source folder not found at: $SkillsSource"
}

$UserHome = $env:USERPROFILE
$AgentPaths = @{
    "claude"      = Join-Path $UserHome ".claude\skills"
    "antigravity" = Join-Path $UserHome ".gemini\config\skills"
    "gemini"      = Join-Path $UserHome ".gemini\config\skills"
    "codex"       = Join-Path $UserHome ".config\opencode\skills"
    "opencode"    = Join-Path $UserHome ".config\opencode\skills"
    "cursor"      = Join-Path $UserHome ".cursor\skills"
}

if ($Doctor) {
    Write-Host "`nSystem Diagnostics:" -ForegroundColor Yellow
    Write-Host "  OS Version:     $([System.Environment]::OSVersion)"
    Write-Host "  User Profile:   $UserHome"
    Write-Host "  Repo Root:      $ScriptDir"
    Write-Host "`nDetected Agent Directories:" -ForegroundColor Yellow
    foreach ($ag in $AgentPaths.Keys | Sort-Object) {
        $p = $AgentPaths[$ag]
        $status = if (Test-Path $p) { "FOUND" } else { "not found" }
        Write-Host "  - $($ag.PadRight(14)) -> $p [$status]"
    }
    exit 0
}

$Destinations = @()
if ($Target) {
    $Destinations += $Target
} elseif ($Local) {
    $Destinations += Join-Path (Get-Location) ".cursor\skills"
} elseif ($All -or $Agent -eq "all") {
    $Destinations += $AgentPaths["claude"]
    $Destinations += $AgentPaths["antigravity"]
    $Destinations += $AgentPaths["codex"]
    $Destinations += $AgentPaths["cursor"]
} elseif ($Agent -and $AgentPaths.ContainsKey($Agent.ToLower())) {
    $Destinations += $AgentPaths[$Agent.ToLower()]
} else {
    Write-Host "`nNo specific agent selected. Defaulting to all standard agent paths." -ForegroundColor Cyan
    $Destinations += $AgentPaths["claude"]
    $Destinations += $AgentPaths["antigravity"]
    $Destinations += $AgentPaths["codex"]
    $Destinations += $AgentPaths["cursor"]
}

$AllSkillDirs = Get-ChildItem -Path $SkillsSource -Directory
Write-Host "`nFound $($AllSkillDirs.Count) skills ready for installation." -ForegroundColor Green

foreach ($dest in $Destinations) {
    Write-Host "`n-> Installing into: $dest" -ForegroundColor Cyan
    if (-not (Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
    }

    $count = 0
    foreach ($s in $AllSkillDirs) {
        $destSkill = Join-Path $dest $s.Name
        if (Test-Path $destSkill) {
            Remove-Item -Path $destSkill -Recurse -Force -ErrorAction SilentlyContinue
        }

        $installed = $false
        if ($Mode -ne "copy") {
            try {
                New-Item -ItemType SymbolicLink -Path $destSkill -Target $s.FullName -Force -ErrorAction Stop | Out-Null
                $installed = $true
            } catch {
                # Fallback to directory copy on Windows
            }
        }
        if (-not $installed) {
            Copy-Item -Path $s.FullName -Destination $destSkill -Recurse -Force
        }
        $count++
        if ($count % 150 -eq 0 -or $count -eq $AllSkillDirs.Count) {
            Write-Host "   Progress: $count / $($AllSkillDirs.Count) skills installed..." -ForegroundColor Gray
        }
    }
    Write-Host " [✓] Completed installation of $count skills to $dest" -ForegroundColor Green
}

Write-Host "`n[✓] All installations completed successfully!" -ForegroundColor Green
