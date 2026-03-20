# llbic Agent Skill

Use this repository when you need to build Linux kernels reproducibly and
collect LLVM bitcode artifacts, logs, and a stable machine-readable manifest.

## Purpose

`llbic` is a Linux kernel build CLI with a stable command surface and a
machine-readable output contract. The main workflow is:

```bash
./llbic build <version> --out-of-tree --json
```

That command downloads the kernel source if needed, extracts it, builds it, and
writes the resulting artifacts under `out/linux-<version>-<arch>-clang<version>/`.

## First Steps

When operating as an agent in this repo:

1. Run `./llbic --help` to discover the current command surface.
2. Prefer `--json` when a command result will be consumed programmatically.
3. Use `inspect` to re-read a finished build instead of rebuilding it.

Typical flow:

```bash
./llbic --help
./llbic build 6.18.16 --out-of-tree --json
./llbic inspect out/linux-6.18.16-x86_64-clang18/llbic.json --json
```

## Backend Selection

`llbic` uses the prepared host toolchain by default.

Use the host path when:

- the required host Clang version exists
- you want the fastest local iteration
- the local environment is already prepared for the target kernel/toolchain

Use Docker when:

- the required host Clang version does not exist
- the host Clang major does not match the kernel-era default and that mismatch
  is not intentional
- you want the image-defined toolchain path for reproducibility

Force Docker with:

```bash
LLBIC_BACKEND=docker ./llbic build <version> --json
```

Force an image rebuild with:

```bash
LLBIC_REBUILD=1 LLBIC_BACKEND=docker ./llbic build <version> --json
```

## Clang Defaults

If `--clang` is not provided, `llbic` selects a default Clang version based on
the kernel era:

- `18` for `6.x` and newer
- `12` for `4.x` and `5.x`
- `7` for `2.6.x` and `3.x`

On the host backend, `llbic` checks whether the expected `clang-<ver>` exists.
If it does not, the command fails early and recommends using Docker. If the
host LLVM major differs from the kernel-era default, `llbic` warns and suggests
`LLBIC_BACKEND=docker` unless the mismatch is intentional.

## Important Commands

One-shot build:

```bash
./llbic build 6.18.16 --out-of-tree --json
```

Scoped build for a single translation unit:

```bash
./llbic build 6.18.16 --out-of-tree --file kernel/sched/core.c --json
```

Compile an already extracted tree:

```bash
./llbic compile linux-6.18.16 --json
```

Inspect a prior result:

```bash
./llbic inspect out/linux-6.18.16-x86_64-clang18/llbic.json --json
```

Collect the support status board from completed build manifests:

```bash
python3 scripts/collect_status.py
```

## Artifact Contract

The main output directory is:

```text
out/linux-<version>-<arch>-clang<version>/
```

The key files are:

- `llbic.json`: final machine-readable build manifest
- `bitcode_files.txt`: discovered LLVM bitcode files
- `llbic.log`: end-to-end llbic log
- `kernel-build.log`: underlying kernel build log

Treat portable scalar paths in `llbic.json` such as `source_dir`, `output_dir`,
`bitcode_root`, and `bitcode_list_file` as the stable artifact identities.
`runtime` and `paths` are environment-dependent resolution helpers. The build
manifest also records `requested_clang`, which is important for distinguishing
support rows when the same kernel and arch are tested under different requested
toolchains, including failed host runs where the requested Clang is missing.

## Status Workflow

This repo does not currently use a standalone unit test suite as the primary
regression contract. The contributor workflow is:

1. run the build path you changed
2. collect the resulting artifacts
3. update the status board when support coverage or regression expectations change

The status board files are:

- `status/status.json`
- `status/STATUS.md`
- `status/badges/overall.json`
- `status/badges/bitcode.json`
- `status/badges/vmlinux.json`

The board should be monotonic by default: existing passing entries should not
silently regress to failing entries unless the pull request explicitly changes
the support contract or documents a regression. The collector compares against
the existing `status/status.json`, warns when previously good rows regress, and
only refreshes the badge JSON files when there are no warnings. Use
`--force-badges` only when you intentionally want to regenerate badge files
despite those warnings. For row identity, treat support targets as distinct by
`arch + requested_clang + kernel`.

## Documentation Priorities

When explaining or updating behavior, prefer these sources in order:

1. `./llbic --help`
2. `README.md`
3. `status/status.json`, `status/STATUS.md`, `status/badges/`, and `scripts/collect_status.py`
4. the implementation in `llbic`

If command behavior changes, update the documentation in the same change.
