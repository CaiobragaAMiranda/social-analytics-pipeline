$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$reviewsDir = Join-Path $root "docs/REVIEWS"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reviewPath = Join-Path $reviewsDir "review-$timestamp.md"

if (-not (Test-Path $reviewsDir)) {
    New-Item -ItemType Directory -Path $reviewsDir | Out-Null
}

$packet = & (Join-Path $PSScriptRoot "gemini_packet.ps1") | Out-String

$instruction = @"
Voce e o avaliador contratual deste projeto.

Modo obrigatorio: avaliador textual.

Nao use ferramentas.
Nao rode comandos.
Nao tente acessar arquivos diretamente.
Nao tente chamar shell, terminal, run_shell_command, grep_search ou qualquer outra tool.
Avalie somente o texto recebido neste prompt.

Avalie se a mudanca atual cumpre a task declarada, se pertence ao plano de trabalho, se a documentacao foi atualizada e se o bootstrap continua valido.

Use a rubrica de docs/GEMINI_CONTRACT.md.

Responda em Markdown com:
- Resultado: Approved | Approved with notes | Changes requested
- Evidencias
- Problemas encontrados
- Recomendacoes
- Decisao final

Pacote de revisao:
"@

$inputText = "$instruction`n`n$packet"
$review = $inputText | & (Join-Path $PSScriptRoot "gemini_cli.ps1") --skip-trust --approval-mode plan --prompt "Revise o pacote recebido via stdin. Nao use ferramentas. Responda somente com a avaliacao contratual textual." --output-format text

$header = @"
# Gemini Review

Gerado em: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@

Set-Content -Path $reviewPath -Value ($header + ($review | Out-String)) -Encoding UTF8

Write-Host "Revisao salva em: $reviewPath"
Write-Host ""
Get-Content $reviewPath
