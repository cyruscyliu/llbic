# Status Board

This folder contains the test matrix and generated status board for `llbic`.

## Matrix

Edit [`matrix.json`](matrix.json) to define which kernel versions to test and
with what knobs.

## Run

From the repo root:

```bash
scripts/run_status_board.py --matrix status/matrix.json
```

This writes:

- `status/status.json` (machine-readable)
- `status/STATUS.md` (human-readable table)

Use `--rebuild` to force rebuilding Docker images (`LLBIC_REBUILD=1`).

