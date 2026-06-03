# Software Engineering Skills and Standards

This document defines the engineering habits expected in this repository. It is intentionally practical: use it as a checklist before changing code, opening PRs or asking an AI reviewer to evaluate work.

## 1. Engineering Mindset

### Think Before Coding

- Understand the problem, expected behavior and failure modes before editing files.
- Explain proposed changes, scope, exclusions and validation before implementation.
- Prefer a small design note or direct explanation over jumping into complex code.
- Identify dependencies, bottlenecks and sensitive-data risks early.

### Keep Solutions Simple

- Follow KISS: choose the simplest readable solution that solves the current task.
- Follow YAGNI: do not build abstractions for hypothetical future requirements.
- Prefer explicit, maintainable code over clever shortcuts.
- Keep documentation compact and useful; avoid long historical logs when a summary is enough.

## 2. Code Quality and Tests

### Tests Are Required

- Do not delete, skip or comment out tests just to make CI pass.
- If behavior changes, update tests to reflect the new rule.
- If a test fails unexpectedly, fix the code or explain the changed requirement.
- Use fake clients and fixtures for external APIs; real network calls must not be part of automated tests.

### Safe Refactoring

- Keep refactors scoped to the task.
- Avoid unrelated formatting churn.
- Preserve public behavior unless the task explicitly changes it.
- Prefer existing local patterns over new frameworks or abstractions.

## 3. Git and Pull Requests

### Branching

- Keep `master` deployable and protected.
- Work on short-lived branches.
- Never use destructive Git operations on shared branches.
- Use `git push --force-with-lease` only on personal feature branches when truly needed.

### Commits

- Make commits atomic: one clear purpose per commit.
- Use conventional prefixes:
  - `feat:` for new capabilities.
  - `fix:` for bug fixes.
  - `docs:` for documentation.
  - `refactor:` for behavior-preserving improvements.
  - `test:` for test changes.
  - `ci:` for pipeline changes.

### Pull Requests

- Explain what changed, why it changed and how it was validated.
- Keep PRs small enough for meaningful review.
- Treat review as quality work, not personal criticism.
- Address actionable CodeRabbit, CI and reviewer findings before merge.

## 4. CI, Security and Data Safety

### CI Expectations

Every meaningful change should pass, when applicable:

```powershell
.\scripts\verify_docs.ps1
$env:PYTHONPATH = "src"; python -m unittest discover -s tests
ruff check .
bandit -c pyproject.toml -r src
docker compose --env-file .env.example config --quiet
```

GitHub Actions must remain green. If the main branch breaks, fixing CI becomes the top priority.

### Public Repository Safety

Never commit:

- `.env` files.
- API keys, tokens or credentials.
- Real channel IDs when unnecessary.
- Raw API payloads or generated local data.
- Local absolute paths.
- Internal hosts, IPs, ports or expanded DSNs.
- Logs that include sensitive request URLs or query parameters.

Use placeholders such as `<local-api-key>`, `<local-dsn>`, `<project-root>` and `<configured>`.

## 5. Data Pipeline Standards

- Preserve raw payloads locally before transformation, but keep them out of Git.
- Normalize provider-specific payloads into the shared `SocialMetric` schema.
- Keep loads idempotent.
- Prefer explicit error messages that help operators without exposing secrets.
- Add validation before broadening provider scope or increasing volume.
- Use retries/backoff only where failure is transient and safe to retry.

## 6. AI-Agent Collaboration

- The repository, not chat memory, is the source of truth.
- Before coding, state the proposed task and expected validation.
- Keep task docs short enough for future agents to resume quickly.
- Use `docs/AGENT_CONTRACTS.md` for review expectations.
- Gemini, ChatGPT, CodeRabbit and GitHub Actions are reviewers; none replace local engineering judgment.

## 7. Daily Checklist

- [ ] Do I understand the problem and expected behavior?
- [ ] Did I explain the proposed change before coding?
- [ ] Is the solution simpler than the alternatives?
- [ ] Did I avoid unrelated changes?
- [ ] Did I add or update tests where useful?
- [ ] Did I protect secrets, local data and public-repo safety?
- [ ] Did local validation and CI pass?
- [ ] Is the PR small and clear enough to review?
