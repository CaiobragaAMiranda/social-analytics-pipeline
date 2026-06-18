# Review Policy

This project uses local validation, GitHub Actions and on-demand AI review before implementation PRs are merged.

## Required Checks

Every implementation PR must pass:

- `Python quality and security`
- `Secret scan`
- Local documentation verification when documentation changes

The GitHub Actions workflow is the required remote quality gate. It runs unit tests, Ruff, Bandit, pip-audit and Gitleaks.

## CodeRabbit

CodeRabbit automatic review is disabled in repository configuration.

Use CodeRabbit on demand when a PR changes code, tests, workflows, public documentation, security-sensitive behavior or review/governance rules.

To request a review, comment on the PR:

```text
@coderabbitai review
```

If CodeRabbit is unavailable or returns no actionable review, continue only when GitHub Actions pass and the user accepts the remaining risk.

## Merge Rule

Merge only when:

- GitHub Actions are green.
- Secret scan is green.
- CodeRabbit has reviewed the PR or the lack of review is documented in the PR notes.
- There are no unresolved blocking findings.

Small tasks may be batched in groups of up to five before commit and PR. Open a PR earlier when the change is large, risky, security-sensitive, blocks further work or needs external review before continuing.
