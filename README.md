# llbic

Compile Linux kernels to LLVM bitcode and kernel images with one stable
command.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Kernel Support](https://img.shields.io/badge/kernels-2.6%20to%207.x-blue.svg)](#usage)
[![Status Board](https://img.shields.io/badge/status%20board-matrix-informational.svg)](./status/README.md)

`llbic` is a Linux kernel build CLI for researchers, tool builders, and agent
workflows that need reproducible kernel artifacts instead of ad hoc scripts. It
pairs an explicit staged command model with a stable machine-readable manifest
so builds are easy to automate, inspect, and reuse.

## For Agents

For agent workflows, start by asking `llbic` for its command surface and prefer
machine-readable output whenever the result will be consumed programmatically.

```text
Use ./llbic --help first to discover the available commands and flags.
When running a build or inspection step for automation, prefer --json so the
result can be parsed reliably. Typical flow:

./llbic --help
./llbic build 6.18.16 --out-of-tree --json
./llbic inspect out/linux-6.18.16/llbic.json --json
```

## Quick start

```bash
./llbic build 6.18.16 --out-of-tree --json
```

That single command:

- Downloads the requested kernel tarball from `kernel.org`
- Extracts the source into `sources/linux-6.18.16`
- Compiles the kernel with the selected backend and toolchain
- Writes logs, a machine-readable manifest, and the bitcode list under `out/linux-6.18.16/`
- Prints the same build summary to stdout because `--json` was requested

You run `./llbic` from the repository root. The CLI creates and manages
`sources/` and `out/` automatically, so you do not need to prepare build
directories by hand.

Expected output layout:

```text
out/linux-6.18.16/
  llbic.log
  kernel-build.log
  llbic.json
  bitcode_files.txt
```

```bash
./llbic inspect out/linux-6.18.16/llbic.json --json
```

Use `inspect` to read back the manifest from a completed build without
rerunning any build steps. This is useful in scripts and agent workflows when
you want to verify the recorded kernel version, architecture, artifact paths,
and bitcode summary from `out/linux-6.18.16/llbic.json`. Stable path fields are
workspace-relative, even when `./llbic` runs inside Docker. Use the `runtime`
and `paths` blocks when you need the local container or host resolution.

Example response shape (abridged):

```json
{
  "status": "success",
  "exit_code": 0,
  "error_step": null,
  "error": null,
  "kernel_version": "6.18.16",
  "kernel_name": "linux-6.18.16",
  "source_url": "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.18.16.tar.xz",
  "source_dir": "sources/linux-6.18.16",
  "output_dir": "out/linux-6.18.16",
  "log_file": "out/linux-6.18.16/llbic.log",
  "strategy": "lto",
  "kernel_build_log": "out/linux-6.18.16/kernel-build.log",
  "arch": "x86_64",
  "arch_is_default": 1,
  "cross_compile": null,
  "cross_compile_is_default": 1,
  "defconfig": "defconfig",
  "defconfig_is_default": 1,
  "build_layout": "outtree",
  "build_layout_is_default": 0,
  "scope": "full",
  "requested_files": [],
  "make_targets": [],
  "kconfig_fragments": [],
  "kconfig_fragments_count": 0,
  "kbuild_dir": "out/linux-6.18.16/kbuild-x86_64-clang18",
  "config_path": "out/linux-6.18.16/kbuild-x86_64-clang18/.config",
  "config_sha256": "<sha256>",
  "bitcode_root": "out/linux-6.18.16/kbuild-x86_64-clang18",
  "bitcode_list_file": "out/linux-6.18.16/bitcode_files.txt",
  "clang": "clang-18",
  "llvm_major": "18",
  "runtime": {
    "execution": "host",
    "workspace_root": "<workspace-root>",
    "sources_root": "<sources-root>",
    "output_root": "<output-root>"
  },
  "paths": {
    "source_dir": {
      "portable": "sources/linux-6.18.16",
      "runtime_path": "<runtime-specific>",
      "resolved_path": "<host-specific>"
    }
  },
  "bitcode_files": [
    "out/linux-6.18.16/kbuild-x86_64-clang18/kernel/sched/core.bc"
  ],
  "bitcode_files_rel": [
    "kernel/sched/core.bc"
  ],
  "bitcode_count": 1,
  "vmlinux_bc": null,
  "kernel_images": [
    "vmlinux",
    "arch/x86/boot/bzImage"
  ],
  "kernel_images_abs": [
    "out/linux-6.18.16/kbuild-x86_64-clang18/vmlinux",
    "out/linux-6.18.16/kbuild-x86_64-clang18/arch/x86/boot/bzImage"
  ]
}
```

## Usage

The public command tree is:

```text
llbic build <version>
llbic download [version|url ...]
llbic extract
llbic compile [kernel-name]
llbic inspect <output-dir|llbic.json>
llbic clean [build|sources|all]
```

Use `build` when you want the full workflow in one command:

```bash
./llbic build 6.18.16 --arch arm64 --out-of-tree
```

Use scoped compilation to build only selected translation units for debugging,
verification, or targeted bitcode generation:

```bash
./llbic build 6.18.16 --out-of-tree --file kernel/sched/core.c --json
```

Use `download` when you only want to fetch kernel archives:

```bash
./llbic download 6.18.16 --json
./llbic download https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.18.16.tar.xz --json
```

Use `extract` when archives already exist locally and you want unpacked source trees:

```bash
./llbic extract --json
```

Use `compile` when the extracted `linux-*` tree already exists and you do not
want to re-download or re-extract:

```bash
./llbic compile linux-6.18.16 --json
```

Use `inspect` to summarize an existing build without rerunning it:

```bash
./llbic inspect ./out/linux-6.18.16/llbic.json --json
```

Use `clean` to remove generated artifacts:

```bash
./llbic clean build --json
./llbic clean sources --json
./llbic clean all --json
```

Flags let you shape the build itself: target architecture, toolchain version,
config source, build layout, output location, and whether the result should be
human-readable or machine-readable.

Flags:

- `--arch, -a`: `x86_64` (default), `arm`, `arm64`, `mips`, `riscv`
- `--clang`: select the LLVM/Clang major version for the build environment
- `--cross`: `CROSS_COMPILE` prefix (defaults are applied for some arches; override as needed)
- `--defconfig`: kbuild config target (default: `defconfig`)
- `--kconfig, -K`: merge one or more Kconfig fragments into the generated `.config` (repeatable)
- `--file, -f`: compile only selected source-relative translation units
- `--output, -o`: override the default `out/linux-<version>/` directory
- `--json`: print a structured status or manifest to stdout
- `--verbose, -V`: pass `V=1` to the kernel build
- `--outtree`, `--out-of-tree`: use `make O=<dir>` for an out-of-tree build
- `--intree`: build in the source tree and run `make clean` first

Example: build ARM64 `defconfig` plus your own config fragment:

```bash
./llbic build 6.18.16 --arch arm64 --out-of-tree -K ./my-kconfig.fragment
```

Environment variables control how `llbic` runs the build backend. They are
runtime overrides, not build-definition flags. `llbic` now uses the prepared
host toolchain by default. Set `LLBIC_BACKEND=docker` when you want the
containerized toolchain path, and use `LLBIC_REBUILD=1` to force rebuilding the
selected Docker image.

`build` always writes `llbic.json`, even on failure. `--json` additionally
emits structured output to stdout. Staged commands such as `download`,
`extract`, `compile`, `inspect`, and `clean` use `--json` for their stdout
response.

Artifacts are written under `out/linux-<version>/` by default (override with
`--output`):

- `llbic.log`: end-to-end build log
- `kernel-build.log`: raw kernel build output from the underlying `make` steps
- `bitcode_files.txt`: list of detected LLVM bitcode files (relative paths under `bitcode_root`)
- `llbic.json`: machine-readable build summary

The `build` manifest includes these top-level fields:

- `status`
- `exit_code`
- `error_step`
- `error`
- `kernel_version`
- `kernel_name`
- `source_url`
- `source_dir`
- `output_dir`
- `log_file`
- `strategy`
- `arch`
- `arch_is_default`
- `cross_compile`
- `cross_compile_is_default`
- `defconfig`
- `defconfig_is_default`
- `build_layout`
- `build_layout_is_default`
- `scope`
- `requested_files`
- `make_targets`
- `kconfig_fragments`
- `kconfig_fragments_count`
- `kbuild_dir`
- `bitcode_root`
- `kernel_build_log`
- `bitcode_list_file`
- `bitcode_files`
- `bitcode_files_rel`
- `bitcode_count`
- `config_path`
- `config_sha256`
- `clang`
- `llvm_major`
- `kernel_images`
- `kernel_images_abs`
- `vmlinux_bc`

Treat the portable scalar path fields such as `source_dir`, `output_dir`,
`bitcode_root`, `kernel_build_log`, and `bitcode_list_file` as the stable
artifact identities.

Note: `kernel/time/timeconst.bc` in the Linux source tree is an input for the `bc`
calculator (used to generate `include/generated/timeconst.h`), not LLVM bitcode.

## Community

Contributions are welcome through issues and pull requests.

`llbic` does not currently ship a standalone unit test suite. For contributors,
the practical regression contract is to run the relevant build path, collect
the resulting artifacts, and update the status board when support coverage
changes.

A plan is to add `out/linux-<version>/llbic.status.jsonl` as an append-only
per-build progress stream. If implemented, it would complement `llbic.json`
rather than replace it: `llbic.status.jsonl` for progressive phase updates,
`llbic.json` for the final manifest, and `status/status.json` for the
aggregated status board.

Quick local verification for a typical change:

```bash
./llbic --help
./llbic build 6.18.16 --out-of-tree --json
./llbic inspect out/linux-6.18.16/llbic.json --json
scripts/run_status_board.py --matrix status/matrix.json
```

This generates:

- `status/status.json` (machine-readable)
- `status/STATUS.md` (human-readable)

The status board is monotonic by default: a change should not rewrite an
existing passing entry into a failing one unless the pull request is explicitly
documenting a regression or changing the support contract. In practice, that
means a CI check can compare the generated `status/status.json` against the
version in the branch and reject the change if previously recorded entries
regress unexpectedly.

The status matrix defaults to `clang: auto`. In the current implementation,
that resolves to `llbic`'s default Clang for the target kernel era: `18` for
6.x and newer, `12` for 4.x and 5.x, and `7` for 2.6.x and 3.x. In practice,
when you run through the Docker images below, that means the status board uses
the highest supported Clang version in the selected image unless the matrix
entry pins `clang` explicitly.

The status board follows `llbic`'s active backend selection. Use the prepared
host toolchain when available, or set `LLBIC_BACKEND=docker` when you want the
containerized path and the image-defined toolchain selection.

| Image | Kernels | Clang |
|---|---|---|
| `ghcr.io/cyruscyliu/llbic:latest` | 6.x, 7.x | 14, 15, 16, 18 |
| `ghcr.io/cyruscyliu/llbic:mid` | 4.x, 5.x | 8, 9, 10, 11, 12 |
| `ghcr.io/cyruscyliu/llbic:legacy` | 2.6, 3.x | 6.0, 7, 8 |

## License

See [LICENSE](LICENSE).
