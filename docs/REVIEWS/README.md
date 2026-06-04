# Reviews Directory

This directory has two different purposes and they should not be mixed.

## Official Files

These files are safe to keep in Git and should be the default reference during handoff:

- `REVIEW_SUMMARY.md`: the consolidated review outcome
- `README.md`: this governance note

## Local Evidence Files

Files such as `review-YYYYMMDD-HHMMSS.md` and `chatgpt-review-*.md` are raw review artifacts.

- They are local evidence files.
- They may contain noisy tool output.
- They should not be committed by default.
- They can be regenerated when needed.

## Rules

- Use `REVIEW_SUMMARY.md` as the primary resume document for review history.
- Keep raw review files in this directory only as temporary local evidence.
- Before committing any review-related file, confirm it does not expose secrets, local paths, payloads, hosts, ports, IPs, or credentials.
- If a raw review contains a finding that matters long term, copy the conclusion into `REVIEW_SUMMARY.md` instead of committing the raw file.
