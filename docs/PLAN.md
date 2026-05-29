# Plano de Trabalho

## Objetivo

Construir um pipeline de analytics social capaz de extrair dados de plataformas sociais, manter historico, normalizar metricas em um schema unico, validar qualidade e orquestrar execucoes periodicas.

## Principios

- O repositorio e a fonte da verdade.
- Toda task deve ter criterios de aceite.
- Toda mudanca relevante deve atualizar documentacao.
- O Revisor avalia por contrato: plano, task, diff, testes e progresso.
- O projeto deve permanecer demonstravel mesmo quando APIs reais bloquearem acesso.

## Fase 0 - Governanca do projeto

Foco: criar o sistema operacional do projeto.

Entregaveis:

- Documentacao base.
- Backlog inicial.
- Script de status.
- Script de verificacao documental.
- Scripts para gerar pacotes de revisao contratual para Gemini ou ChatGPT.

## Fase 1 - Nucleo MVP e autenticacao

Foco: provar que dados podem ser extraidos, preservados e normalizados corretamente.

Entregaveis:

- Mapeamento inicial de APIs e limitacoes.
- Providers reais ou mockados.
- Camada raw para salvar JSON bruto.
- Schema unico para metricas sociais.
- Transformacoes testadas.
- Carga local em PostgreSQL via Docker.

## Fase 2 - Orquestracao e historico

Foco: automatizar o fluxo e permitir backfill.

Entregaveis:

- Airflow via Docker Compose.
- DAGs por fonte.
- Agendamento quinzenal.
- Catchup historico.
- Parametros por intervalo de dados.

## Fase 3 - Resiliencia e alertas

Foco: sobreviver a falhas comuns sem intervencao constante.

Entregaveis:

- Retries com backoff.
- Tratamento de rate limit.
- Alertas para tokens expirados.
- Dead Letter Queue para registros invalidos.
- Idempotencia de carga.

## Fase 4 - Qualidade e escala

Foco: aumentar confianca e preparar crescimento.

Entregaveis:

- Validacao com Great Expectations ou alternativa equivalente.
- Testes unitarios e mocks de APIs.
- Metricas do pipeline.
- Rate limiter por provider.
- Avaliacao de async ou CeleryExecutor quando houver volume real.

## Fora de escopo inicial

- Dashboard analitico completo.
- Integracao paga com APIs antes de validar mocks.
- Infraestrutura cloud.
- CI/CD completo antes do MVP local.
