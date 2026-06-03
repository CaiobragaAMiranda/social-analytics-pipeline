$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$tasksPath = Join-Path $root "docs/TASKS.md"
$progressPath = Join-Path $root "docs/PROGRESS.md"

function Get-FirstMatch {
    param(
        [string] $Path,
        [string] $Pattern
    )

    if (-not (Test-Path $Path)) {
        return "Missing file: $Path"
    }

    $match = Select-String -Path $Path -Pattern $Pattern | Select-Object -First 1
    if ($null -eq $match) {
        return "Not found"
    }

    return $match.Line.Trim()
}

$currentPhase = Get-FirstMatch -Path $progressPath -Pattern "^Current phase:"
$currentTask = Get-FirstMatch -Path $progressPath -Pattern "^Current task:"
$generalStatus = Get-FirstMatch -Path $progressPath -Pattern "^Overall status:"
$taskStatus = Get-FirstMatch -Path $tasksPath -Pattern "^Status:"

Write-Host "Project status"
Write-Host "-----------------"
Write-Host $currentPhase
Write-Host $currentTask
Write-Host $generalStatus
Write-Host "Task status: $($taskStatus -replace '^Status:\s*', '')"
Write-Host ""
Write-Host "Main documents"
Write-Host "---------------------"

@(
    "README.md",
    "SKILLS.md",
    "docs/PLAN.md",
    "docs/TASKS.md",
    "docs/PROGRESS.md",
    "docs/BOOTSTRAP.md",
    "docs/ARCHITECTURE.md",
    "docs/AGENT_CONTRACTS.md"
) | ForEach-Object {
    $path = Join-Path $root $_
    $marker = if (Test-Path $path) { "ok" } else { "missing" }
    Write-Host "$marker $_"
}
