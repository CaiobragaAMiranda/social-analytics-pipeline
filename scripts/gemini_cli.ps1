$ErrorActionPreference = "Stop"

$node = "C:\Program Files\nodejs\node.exe"
$gemini = "$env:APPDATA\npm\node_modules\@google\gemini-cli\bundle\gemini.js"

if (-not (Test-Path $node)) {
    throw "Node.js nao encontrado em: $node"
}

if (-not (Test-Path $gemini)) {
    throw "Gemini CLI nao encontrado em: $gemini"
}

$stdin = [Console]::In.ReadToEnd()

if ([string]::IsNullOrWhiteSpace($stdin)) {
    & $node $gemini @args
} else {
    $stdin | & $node $gemini @args
}
