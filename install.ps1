[CmdletBinding()]
param(
    [string]$Destination,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Destination)) {
    $codexHome = $env:CODEX_HOME
    if ([string]::IsNullOrWhiteSpace($codexHome)) {
        $codexHome = Join-Path $env:USERPROFILE ".codex"
    }
    $Destination = Join-Path $codexHome "skills"
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "daily-work-planner"
$manifest = Join-Path $source "SKILL.md"

if (-not (Test-Path -LiteralPath $manifest)) {
    throw "Cannot find SKILL.md at $manifest. Run this script from the repository root."
}

New-Item -ItemType Directory -Path $Destination -Force | Out-Null
$resolvedDestination = (Resolve-Path -LiteralPath $Destination).Path
$target = Join-Path $resolvedDestination "daily-work-planner"

if (Test-Path -LiteralPath $target) {
    if (-not $Force) {
        throw "Target already exists: $target. Re-run with -Force to replace it."
    }
    $resolvedTarget = (Resolve-Path -LiteralPath $target).Path
    if (-not $resolvedTarget.StartsWith($resolvedDestination)) {
        throw "Refusing to remove target outside destination: $resolvedTarget"
    }
    Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
}

Copy-Item -LiteralPath $source -Destination $resolvedDestination -Recurse -Force

Write-Host "Installed Daily Work Planner skill to:"
Write-Host $target
Write-Host ""
Write-Host "Restart Codex, then use: Use `$daily-work-planner to plan my work session."
