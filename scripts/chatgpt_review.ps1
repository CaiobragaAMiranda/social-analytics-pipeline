$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$reviewsDir = Join-Path $root "docs/REVIEWS"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reviewPath = Join-Path $reviewsDir "chatgpt-review-$timestamp.md"

if (-not (Test-Path $reviewsDir)) {
    New-Item -ItemType Directory -Path $reviewsDir | Out-Null
}

$packet = & (Join-Path $PSScriptRoot "gemini_packet.ps1") | Out-String

$instruction = @"
Voce e o avaliador contratual deste projeto (ChatGPT).

Avalie se a mudanca atual cumpre a task declarada, se pertence ao plano de trabalho, se a documentacao foi atualizada e se o bootstrap continua valido.

Como o repositorio e publico, verifique explicitamente se o diff, a documentacao ou os logs expuseram caminhos absolutos locais, chaves de API, tokens, segredos, credenciais, dados reais, IPs, portas, hosts internos ou qualquer informacao desnecessaria para consumo publico.

Se identificar algum vazamento sensivel, reporte o problema sem repetir o valor exato. Cite apenas o tipo de informacao, o arquivo e, se necessario, use placeholders como `<caminho-local>`, `<token>`, `<ip-interno>` ou `<porta-local>`.

Use a rubrica de docs/AGENT_CONTRACTS.md.

Responda em Markdown com:
- Resultado: Approved | Approved with notes | Changes requested
- Evidencias
- Problemas encontrados
- Recomendacoes
- Decisao final

Para cada problema encontrado, inclua obrigatoriamente:
- Severidade: baixa | media | alta | critica
- Arquivo afetado: <caminho-relativo>
- Evidencia objetiva: <trecho-ou-log>
- Risco pratico: <impacto-real>
- Acao recomendada: <como-corrigir>

Pacote de revisao:
"@

$inputText = "$instruction`n`n$packet"

# Tenta localizar o Codex CLI no PATH.
$codexPath = Get-Command codex -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source

if ($codexPath) {
    Write-Host "Iniciando revisao automatizada com Codex (ChatGPT) via $codexPath..."
    $inputPath = Join-Path $env:TEMP "chatgpt-review-input-$timestamp.md"
    Set-Content -Path $inputPath -Value $inputText -Encoding UTF8
    
    try {
        # Chama o codex exec passando o pacote via stdin e solicita a revisao textual
        $review = Get-Content $inputPath -Raw | & $codexPath exec --ephemeral -
    } finally {
        Remove-Item $inputPath -ErrorAction SilentlyContinue
    }
} else {
    Write-Warning "Codex CLI nao encontrado no PATH ou em locais conhecidos. O pacote de revisao sera salvo para uso manual."
    $review = "--- PACOTE PARA REVISAO MANUAL ---`n`n$inputText"
}

$header = @"
# ChatGPT Review

Gerado em: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@

Set-Content -Path $reviewPath -Value ($header + ($review | Out-String)) -Encoding UTF8

Write-Host "Revisao/Pacote salvo em: $reviewPath"
