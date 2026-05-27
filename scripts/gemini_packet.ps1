$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$files = @(
    "docs/PLAN.md",
    "docs/TASKS.md",
    "docs/PROGRESS.md",
    "docs/BOOTSTRAP.md",
    "docs/ARCHITECTURE.md",
    "docs/GEMINI_CONTRACT.md"
)

Write-Host "# Pacote de Revisao para Gemini"
Write-Host ""
Write-Host "Gerado em: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

foreach ($file in $files) {
    $path = Join-Path $root $file
    Write-Host ""
    Write-Host "## $file"
    Write-Host ""

    if (Test-Path $path) {
        Get-Content $path
    } else {
        Write-Host "Arquivo ausente."
    }
}

Write-Host ""
Write-Host "## Git Diff"
Write-Host ""

if (Get-Command git -ErrorAction SilentlyContinue) {
    Push-Location $root
    try {
        git diff -- README.md docs scripts
    } finally {
        Pop-Location
    }
} else {
    Write-Host "Git nao encontrado no PATH."
}
