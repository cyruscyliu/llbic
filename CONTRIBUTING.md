# Contributing to llbic

Thanks for contributing.

## Scope

Good contributions include:

- kernel-version support improvements
- Docker image and toolchain updates
- build reproducibility fixes
- JSON output and agent integration improvements
- documentation and onboarding cleanup

## Before opening a PR

- Keep changes focused.
- Prefer updating the Bash CLI in `llbic` for the main workflow.
- Preserve the canonical one-shot contract: `llbic build <version>`.
- If you change output behavior, update `README.md`.

## Development

Build Docker images locally:

```bash
docker compose build llbic
docker compose build llbic-mid
docker compose build llbic-legacy
```

Run the CLI locally:

```bash
./llbic --help
./llbic build 6.12 --json
```

## Pull requests

Please include:

- what changed
- why it changed
- how you verified it
- any kernel/toolchain/version constraints

Small, reviewable PRs are preferred over large mixed changes.
