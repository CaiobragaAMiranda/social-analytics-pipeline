# Agent Contracts

This project can be developed by Codex/ChatGPT or Gemini, but every meaningful change should be reviewable from repository context.

## Roles

When Codex implements:

- Developer: Codex/ChatGPT.
- Contract reviewer: Gemini when available.
- Fallback reviewers: GitHub Actions, CodeRabbit and user review.
- CodeRabbit usage follows `docs/REVIEW_POLICY.md`.

When Gemini implements:

- Developer: Gemini.
- Contract reviewer: ChatGPT/Codex when available.

## Required Review Questions

Reviewers should check:

1. Does the change belong to the work plan?
2. Does it match the current task?
3. Were acceptance criteria met?
4. Were docs and bootstrap updated when needed?
5. Are there out-of-scope changes?
6. Are tests present, or is the lack of tests justified?
7. Can the next session resume from the repository state?
8. Did the developer explain proposed changes before coding?
9. Did the diff expose secrets, local paths, real payloads, IPs, ports, credentials, hosts or expanded DSNs?

## Finding Format

Each problem must include:

- Severity: low | medium | high | critical
- Affected file: `<relative-path>`
- Objective evidence: safe excerpt or log summary
- Practical risk: real impact
- Recommended action: concrete fix

## Decision Labels

- Approved
- Approved with notes
- Changes requested

## Base Reviewer Prompt

```text
You are the contractual reviewer for this project.

Evaluate whether the current change matches the declared task, belongs to the work plan, updates documentation when needed and keeps bootstrap instructions valid.

Because the repository is public, explicitly check whether the diff, documentation or logs expose local absolute paths, API keys, tokens, secrets, credentials, real payloads, IPs, ports, internal hosts or expanded DSNs.

If sensitive information appears, report the type and location without repeating the value. Use placeholders such as <local-path>, <token>, <internal-host> or <local-port>.

Use docs/AGENT_CONTRACTS.md as the rubric.

Respond in Markdown with:
- Result: Approved | Approved with notes | Changes requested
- Evidence
- Findings
- Recommendations
- Final decision
```
