# ADR-0001 - Repository as Source of Truth

Status: Accepted

Date: 2026-05-27

## Context

The project is developed through collaboration between the user and AI agents. Long conversations can lose context, so project state must be recoverable from files.

## Decision

The repository is the source of truth for plan, tasks, progress, bootstrap, architecture and review rules.

## Consequences

Benefits:

- Work can resume from repository context.
- Reviewers can evaluate concrete diffs and documented intent.
- Less dependence on conversation memory.

Costs:

- Meaningful changes must update compact documentation.
- Sensitive local information must be actively kept out of public files.
