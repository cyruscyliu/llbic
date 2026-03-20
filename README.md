# llbic

Compile Linux kernels to source code, LLVM bitcode, and kernel images with one
stable command.

[![Container Registry](https://img.shields.io/badge/ghcr.io-llbic-blue)](https://github.com/cyruscyliu/llbic/pkgs/container/llbic)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

`llbic` is a Linux kernel build CLI with an explicit staged command model and a
stable machine-facing manifest. It is designed for researchers, tool builders,
and agent workflows that need reusable kernel artifacts instead of ad hoc
scripts.

## Quick start

Run the canonical build command:

```bash
./llbic build 6.12
```

This downloads the kernel source, builds it, and writes output to:

```text
out/linux-6.12/
  llbic.log
  kernel-build.log
  llbic.json
  bitcode_files.txt
```

`./llbic` delegates backend execution to the shared
[`research-runtime`](/home/debian/Projects/research-os/runtime/research-runtime/README.md)
layer when it is available. Docker remains the default backend, and the local
image is built automatically if it is missing. Use `LLBIC_REBUILD=1` to force
rebuilding the image, or `LLBIC_BACKEND=host` to bypass Docker on a prepared
host toolchain.

Use `--clang` to pick a toolchain:

```bash
./llbic build 6.12 --clang 18
```

Use `--arch` (and optionally `--cross`) to build for another architecture:

```bash
./llbic build 6.12 --arch arm64
./llbic build 6.12 --arch arm --cross arm-linux-gnueabi-
```

For agents, use structured output:

```bash
./llbic build 6.12 --json
```

What you get from one build:

- Resolved kernel source tarball from `kernel.org`
- Extracted source tree
- A kernel build (in-tree by default; or out-of-tree with `--out-of-tree`)
- LLVM bitcode manifest (`bitcode_files.txt`) plus `bitcode_root` in `llbic.json`
- Compiled kernel images when produced by the target kernel (`vmlinux`, `bzImage`, etc.)
- End-to-end `llbic.log`
- Optional JSON output for agents

Example response:

Stable path fields are workspace-relative, even when `./llbic` runs inside
Docker. Use the `runtime` and `paths` blocks when you need the local container
or host resolution.

```json
{
  "status": "success",
  "kernel_version": "6.12",
  "kernel_name": "linux-6.12",
  "source_url": "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.12.tar.xz",
  "source_dir": "sources/linux-6.12",
  "output_dir": "out/linux-6.12",
  "log_file": "out/linux-6.12/llbic.log",
  "kernel_build_log": "out/linux-6.12/kernel-build.log",
  "arch": "x86_64",
  "cross_compile": null,
  "defconfig": "defconfig",
  "build_layout": "intree",
  "scope": "full",
  "requested_files": [],
  "make_targets": [],
  "kconfig_fragments": [],
  "bitcode_root": "sources/linux-6.12",
  "bitcode_list_file": "out/linux-6.12/bitcode_files.txt",
  "clang": "clang",
  "llvm_major": "18",
  "runtime": {
    "execution": "docker",
    "workspace_root": "/work",
    "sources_root": "/work/sources",
    "output_root": "/out"
  },
  "bitcode_files_rel": [
    "kernel/sched/core.bc"
  ],
  "bitcode_count": 1,
  "vmlinux_bc": null,
  "kernel_images": [
    "vmlinux",
    "arch/x86/boot/bzImage"
  ]
}
```

## Command Model

The public command tree is:

```text
llbic build <version>
llbic download [version|url ...]
llbic extract
llbic compile [kernel-name]
llbic inspect <output-dir|llbic.json>
llbic clean [build|sources|all]
```

Use the staged commands when you want explicit Unix-style boundaries. Use
`build` when you want the full one-shot workflow.

## Usage

Canonical one-shot build:

```bash
./llbic build 6.18.16 --arch arm64 --out-of-tree
```

Fetch and extract sources explicitly:

```bash
./llbic download 6.18.16 --json
./llbic extract --json
```

Inspect an existing build without rerunning:

```bash
./llbic inspect ./out/linux-6.18.16
./llbic inspect ./out/linux-6.18.16/llbic.json --json
```

Compile only one file for debugging or verification:

```bash
./llbic build 6.18.16 --out-of-tree --file kernel/sched/core.c --json
./llbic compile linux-6.18.16 --clang 18 --file kernel/sched/core.c --json
```

`--out-of-tree` builds with `make O=<dir>` so the build output lives outside the
extracted source tree. This avoids conflicts when rebuilding the same kernel
with a different `--clang` version.

Artifacts are written under `out/linux-<version>/` by default (override
with `--output`):

- `llbic.log`: end-to-end build log
- `llbic.json`: machine-readable build summary
- `bitcode_files.txt`: list of detected LLVM bitcode files (relative paths under `bitcode_root`)

`build --json` prints the build summary to stdout and also writes `llbic.json`.
Staged commands such as `download`, `extract`, `compile`, and `inspect` also
support `--json` and return structured status on stdout.

Stable build fields include:

- `status`
- `exit_code`
- `kernel_version`
- `kernel_name`
- `source_dir`
- `output_dir`
- `arch`
- `cross_compile`
- `defconfig`
- `build_layout`
- `scope`
- `requested_files`
- `make_targets`
- `bitcode_root`
- `bitcode_list_file`
- `bitcode_files`
- `bitcode_count`
- `config_path`
- `config_sha256`
- `kernel_images`

`runtime` and `paths` are convenience metadata for resolving those portable
paths in the current environment. Agents should treat the relative scalar fields
as the stable artifact identities.

Note: `kernel/time/timeconst.bc` in the Linux source tree is an input for the `bc`
calculator (used to generate `include/generated/timeconst.h`), not LLVM bitcode.

Different images serve different kernel era:

| Image | Kernels | Clang |
|---|---|---|
| `ghcr.io/cyruscyliu/llbic:latest` | 6.x, 7.x | 14, 15, 16, 18 |
| `ghcr.io/cyruscyliu/llbic:mid` | 4.x, 5.x | 8, 9, 10, 11, 12 |
| `ghcr.io/cyruscyliu/llbic:legacy` | 2.6, 3.x | 6.0, 7, 8 |

Flags:

- `--arch, -a`: `x86_64` (default), `arm`, `arm64`, `mips`, `riscv`
- `--cross`: `CROSS_COMPILE` prefix (defaults are applied for some arches; override as needed)
- `--defconfig`: kbuild config target (default: `defconfig`)
- `--kconfig, -K`: merge one or more Kconfig fragments into the generated `.config` (repeatable)

Example: build ARM64 `defconfig` plus your own config fragment:

```bash
./llbic build 6.18.16 --arch arm64 --out-of-tree -K ./my-kconfig.fragment
```

## Status board

`status/matrix.json` defines a set of kernel versions + knobs (arch/clang/layout)
to test before release. To run it:

```bash
scripts/run_status_board.py --matrix status/matrix.json
```

This generates:

- `status/status.json` (machine-readable)
- `status/STATUS.md` (human-readable)

## Community

- Contributions are welcome through issues and pull requests.
- For repo conventions and contribution flow, see [CONTRIBUTING.md](./CONTRIBUTING.md).
- For security reporting guidance, see [SECURITY.md](./SECURITY.md).
- Community participation is covered by [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## License

See [LICENSE](LICENSE).
