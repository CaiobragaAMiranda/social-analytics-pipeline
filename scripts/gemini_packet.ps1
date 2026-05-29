$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$files = @(
    "docs/PLAN.md",
    "docs/TASKS.md",
    "docs/PROGRESS.md",
    "docs/BOOTSTRAP.md",
    "docs/ARCHITECTURE.md",
    "docs/AGENT_CONTRACTS.md"
)

Write-Output "# Pacote de Revisao Contratual"
Write-Output ""
Write-Output "Gerado em: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Output ""

foreach ($file in $files) {
    $path = Join-Path $root $file
    Write-Output ""
    Write-Output "## $file"
    Write-Output ""

    if (Test-Path $path) {
        Get-Content $path
    } else {
        Write-Output "Arquivo ausente."
    }
}

Write-Output ""
Write-Output "## Git Diff"
Write-Output ""

if (Get-Command git -ErrorAction SilentlyContinue) {
    Push-Location $root
    try {
        git diff -- .

        Write-Output ""
        Write-Output "## Git Staged Diff"
        Write-Output ""
        git diff --cached -- .

        Write-Output ""
        Write-Output "## Git Untracked Files"
        Write-Output ""
        $untracked = git ls-files --others --exclude-standard
        if ($null -eq $untracked -or $untracked.Count -eq 0) {
            Write-Output "No untracked files."
        } else {
            foreach ($file in $untracked) {
                $normalizedPath = $file -replace "\\", "/"
                Write-Output ""
                Write-Output "### $file"
                Write-Output ""

                if ($normalizedPath -like "docs/REVIEWS/*.md") {
                    Write-Output "Arquivo de review nao incluido automaticamente no pacote para evitar repetir logs extensos ou informacoes sensiveis. Revise manualmente antes de commitar."
                    continue
                }

                if (Test-Path $file) {
                    Get-Content $file
                } else {
                    Write-Output "File listed by Git but not found on disk."
                }
            }
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Output "Git nao encontrado no PATH."
}
