[CmdletBinding()]
param(
    [ValidateSet("codex", "generic")]
    [string]$Agent = "codex",
    [string]$Destination,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Destination)) {
    if ($Agent -eq "codex") {
        $codexHome = $env:CODEX_HOME
        if ([string]::IsNullOrWhiteSpace($codexHome)) {
            $codexHome = Join-Path $env:USERPROFILE ".codex"
        }
        $Destination = Join-Path $codexHome "skills"
    } else {
        $agentHome = $env:AGENT_SKILLS_HOME
        if ([string]::IsNullOrWhiteSpace($agentHome)) {
            $agentHome = Join-Path $env:USERPROFILE ".agent-skills"
        }
        $Destination = $agentHome
    }
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

Write-Host "Installed Daily Work Planner skill for '$Agent' to:"
Write-Host $target
Write-Host ""
if ($Agent -eq "codex") {
    Write-Host "Restart Codex, then use: Use `$daily-work-planner to plan my work session."
} else {
    Write-Host "Point your agent at one of these entrypoints:"
    Write-Host "  - $target\AGENTS.md  (generic agent instructions)"
    Write-Host "  - $target\SKILL.md   (OpenAI/Codex skill format)"
    Write-Host ""
    Write-Host "If your agent supports local tools, allow Python to run scripts from:"
    Write-Host "  $target\scripts"
}
