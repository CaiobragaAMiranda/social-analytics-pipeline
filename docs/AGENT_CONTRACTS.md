# Contratos de Agentes (Gemini & ChatGPT)

Este documento define os papeis e rubricas de revisao quando o projeto e desenvolvido por multiplos agentes de IA.

## Dinamica de Agentes

O papel de "Desenvolvedor" e "Revisor" alterna dependendo do canal de comunicacao utilizado:

1.  **Canal Codex (ChatGPT):**
    *   **Desenvolvedor:** ChatGPT.
    *   **Revisor Contratual:** Gemini.
    *   **Fluxo:** O ChatGPT implementa a task e solicita a revisao via `scripts/gemini_review.ps1`.

2.  **Canal Gemini CLI (Gemini):**
    *   **Desenvolvedor:** Gemini.
    *   **Revisor Contratual:** ChatGPT.
    *   **Fluxo:** O Gemini implementa a task e solicita a revisao via `scripts/chatgpt_review.ps1`.

## Rubrica de Revisao

Independentemente do agente revisor, a rubrica deve ser seguida rigorosamente. Para cada problema encontrado, incluir obrigatoriamente:
- **Severidade:** baixa | media | alta | critica
- **Arquivo afetado:** <caminho-relativo>
- **Evidencia objetiva:** <trecho-ou-log> (sem valores sensiveis)
- **Risco pratico:** <impacto-real>
- **Acao recomendada:** <como-corrigir>

Rubrica de conformidade:

1. A task pertence ao plano?
2. Os criterios de aceite foram cumpridos?
3. A documentacao foi atualizada?
4. O bootstrap continua correto?
5. Existem mudancas fora do escopo?
6. Existem riscos tecnicos nao registrados?
7. Existem testes ou justificativa para ausencia de testes?
8. O progresso foi registrado de forma retomavel?
9. As mudancas propostas foram comunicadas diretamente ao usuario antes da implementacao?
10. A task executada corresponde a uma proposta aprovada ou a uma continuidade solicitada pelo usuario?
11. O diff, os logs ou a documentacao expuseram caminhos locais absolutos, chaves, tokens, segredos, credenciais, dados reais, IPs, portas, hosts internos ou qualquer informacao desnecessaria para um repositorio publico?

## Regras de Aprovacao

*   **Approved:** Todos os criterios atendidos, sem riscos bloqueantes, documentacao coerente.
*   **Approved with notes:** Aceitavel, mas com recomendacoes de melhoria nao bloqueantes.
*   **Changes requested:** Criterios nao cumpridos, mudanca fora de escopo, falta documentacao, quebra de bootstrap ou vazamento de informacao sensivel.

## Prompt Base para Revisor (ChatGPT ou Gemini)

```text
Voce e o avaliador contratual deste projeto.

Avalie se a mudanca atual cumpre a task declarada, se pertence ao plano de trabalho, se a documentacao foi atualizada e se o bootstrap continua valido.

Como o repositorio e publico, verifique explicitamente se o diff, a documentacao ou os logs expuseram caminhos absolutos locais, chaves de API, tokens, segredos, credenciais, dados reais, IPs, portas, hosts internos ou qualquer informacao desnecessaria para consumo publico.

Se identificar algum vazamento sensivel, reporte o problema sem repetir o valor exato. Cite apenas o tipo de informacao, o arquivo e, se necessario, use placeholders como <caminho-local>, <token>, <ip-interno> ou <porta-local>.

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
```
