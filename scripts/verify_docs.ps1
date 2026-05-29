$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$requiredFiles = @(
    "README.md",
    "docs/PLAN.md",
    "docs/TASKS.md",
    "docs/PROGRESS.md",
    "docs/BOOTSTRAP.md",
    "docs/ARCHITECTURE.md",
    "docs/AGENT_CONTRACTS.md",
    "docs/DECISIONS/ADR-0001-repository-as-source-of-truth.md",
    "docs/REVIEWS/.gitkeep",
    "scripts/gemini_cli.ps1",
    "scripts/project_status.ps1",
    "scripts/verify_docs.ps1",
    "scripts/gemini_packet.ps1",
    "scripts/gemini_review.ps1",
    "scripts/chatgpt_review.ps1"
)

$missing = @()

foreach ($file in $requiredFiles) {
    $path = Join-Path $root $file
    if (-not (Test-Path $path)) {
        $missing += $file
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Falha: arquivos obrigatorios ausentes."
    $missing | ForEach-Object { Write-Host "- $_" }
    exit 1
}

$tasks = Get-Content (Join-Path $root "docs/TASKS.md") -Raw
$progress = Get-Content (Join-Path $root "docs/PROGRESS.md") -Raw
$contract = Get-Content (Join-Path $root "docs/AGENT_CONTRACTS.md") -Raw

if ($tasks -notmatch "TASK-001") {
    throw "TASK-001 nao encontrada em docs/TASKS.md"
}

if ($progress -notmatch "Fase atual:") {
    throw "Fase atual nao encontrada em docs/PROGRESS.md"
}

if ($contract -notmatch "Approved \| Approved with notes \| Changes requested") {
    throw "Rubrica de agentes nao encontrada ou incompleta."
}

Write-Host "Verificacao documental concluida com sucesso."
