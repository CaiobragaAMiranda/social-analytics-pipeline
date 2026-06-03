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
$node = (Get-Command node -ErrorAction Stop).Source
$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCommand) {
    $npmCommand = Get-Command npm -ErrorAction Stop
}
$npmRoot = & $npmCommand.Source root -g
if (-not $npmRoot) {
    throw "Nao foi possivel localizar o diretorio global do npm."
}

function ConvertTo-ProcessArgument {
    param([string] $Value)

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    return '"' + ($Value -replace '"', '\"') + '"'
}

$gemini = Join-Path $npmRoot "@google\gemini-cli\bundle\gemini.js"
$inputPath = Join-Path $env:TEMP "gemini-review-input-$timestamp.md"
$previousNoRelaunch = $env:GEMINI_CLI_NO_RELAUNCH
$previousUseGca = $env:GOOGLE_GENAI_USE_GCA
$previousAccessToken = $env:GOOGLE_CLOUD_ACCESS_TOKEN
$env:GEMINI_CLI_NO_RELAUNCH = "1"

$oauthCredsPath = Join-Path $env:USERPROFILE ".gemini/oauth_creds.json"
if (Test-Path $oauthCredsPath) {
    try {
        $oauthCreds = Get-Content $oauthCredsPath -Raw | ConvertFrom-Json
        if ($oauthCreds.access_token) {
            $env:GOOGLE_GENAI_USE_GCA = "true"
            $env:GOOGLE_CLOUD_ACCESS_TOKEN = $oauthCreds.access_token
        }
    } catch {
        Write-Warning "Nao foi possivel carregar as credenciais OAuth locais do Gemini: $($_.Exception.Message)"
    }
}

Set-Content -Path $inputPath -Value $inputText -Encoding UTF8

try {
    $geminiArgs = @(
        $gemini,
        "--skip-trust",
        "--approval-mode", "plan",
        "--prompt", "Revise o pacote recebido via stdin. Nao use ferramentas. Responda somente com a avaliacao contratual textual.",
        "--output-format", "text"
    )
    $processInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $processInfo.FileName = $node
    $processInfo.Arguments = ($geminiArgs | ForEach-Object { ConvertTo-ProcessArgument $_ }) -join " "
    $processInfo.RedirectStandardInput = $true
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false

    $geminiProcess = [System.Diagnostics.Process]::new()
    $geminiProcess.StartInfo = $processInfo
    [void] $geminiProcess.Start()
    $geminiProcess.StandardInput.Write((Get-Content -Path $inputPath -Encoding UTF8 -Raw))
    $geminiProcess.StandardInput.Close()
    $stdout = $geminiProcess.StandardOutput.ReadToEnd()
    $stderr = $geminiProcess.StandardError.ReadToEnd()
    $geminiProcess.WaitForExit()
    $geminiExitCode = $geminiProcess.ExitCode
    $reviewOutput = @($stdout, $stderr)
} finally {
    $env:GEMINI_CLI_NO_RELAUNCH = $previousNoRelaunch
    $env:GOOGLE_GENAI_USE_GCA = $previousUseGca
    $env:GOOGLE_CLOUD_ACCESS_TOKEN = $previousAccessToken
    Remove-Item -LiteralPath $inputPath -ErrorAction SilentlyContinue
}

$review = $reviewOutput | Out-String
$review = $review -replace [regex]::Escape($root), "<project-root>"
$review = $review -replace [regex]::Escape(($root -replace "\\", "/")), "<project-root>"
if ($env:USERPROFILE) {
    $review = $review -replace [regex]::Escape($env:USERPROFILE), "<user-home>"
    $review = $review -replace [regex]::Escape(($env:USERPROFILE -replace "\\", "/")), "<user-home>"
}
if ($env:TEMP) {
    $review = $review -replace [regex]::Escape($env:TEMP), "<temp-dir>"
    $review = $review -replace [regex]::Escape(($env:TEMP -replace "\\", "/")), "<temp-dir>"
}

if ($geminiExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($review)) {
    $blockedReviewTemplate = @'
Resultado: Changes requested

## Evidencias

- Gemini CLI did not return a valid contractual review.
- Exit code: {{EXIT_CODE}}

## Problemas encontrados

### Gemini review could not be completed

- Severidade: alta
- Arquivo afetado: scripts/gemini_review.ps1
- Evidencia objetiva: Gemini CLI returned no valid review output.
- Risco pratico: The project could incorrectly treat an unreviewed change as contractually approved.
- Acao recomendada: Refresh Gemini CLI authentication and rerun scripts/gemini_review.ps1 before considering the contractual review complete.

## Recomendacoes

- Run `gemini auth login` or the locally required Gemini CLI authentication flow.
- Rerun `scripts/gemini_review.ps1`.
- Do not commit docs/REVIEWS output unless it has been manually checked for sensitive information.

## Decisao final

Changes requested until Gemini authentication is restored and a valid review is produced.

## Raw Tool Output Sanitized

```text
{{RAW_REVIEW}}
```
'@
    $review = $blockedReviewTemplate.Replace("{{EXIT_CODE}}", [string] $geminiExitCode).Replace("{{RAW_REVIEW}}", $review)
}

$header = @"
# Gemini Review

Gerado em: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@

Set-Content -Path $reviewPath -Value ($header + ($review | Out-String)) -Encoding UTF8

Write-Host "Revisao salva em: $reviewPath"
Write-Host ""
Get-Content $reviewPath
