# llbic

Compile Linux kernels to source code, LLVM bitcode, and kernel images with one
stable command.

[![Docker Publish](https://github.com/cyruscyliu/llbic/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/cyruscyliu/llbic/actions/workflows/docker-publish.yml)
[![Container Registry](https://img.shields.io/badge/ghcr.io-llbic-blue)](https://github.com/cyruscyliu/llbic/pkgs/container/llbic)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

`llbic` is a one-shot interface for turning a Linux kernel version into a build
workspace.  It is designed for researchers, tool builders, and agent workflows
that need stable kernel artifacts instead of ad hoc scripts.

## Quick start

Docker is the default workflow:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12
```

This downloads the kernel source, builds it, and writes output to:

```text
out/linux-6.12/
  llbic.log
  kernel-build.log
  llbic.json
  bitcode_files.txt
```

Use `--clang` to pick a toolchain:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12 --clang 18
```

Use `--arch` (and optionally `--cross`) to build for another architecture:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12 --arch arm64
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12 --arch arm --cross arm-linux-gnueabi-
```

For agents, use JSON output:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12 --json
```

What you get from one run:

- Resolved kernel source tarball from `kernel.org`
- Extracted source tree
- A kernel build (in-tree by default; or out-of-tree with `--out-of-tree`)
- LLVM bitcode manifest (`bitcode_files.txt`) plus `bitcode_root` in `llbic.json`
- Compiled kernel images when produced by the target kernel (`vmlinux`, `bzImage`, etc.)
- End-to-end `llbic.log`
- Optional JSON output for agents

Example response:

```json
{
  "status": "success",
  "kernel_version": "6.12",
  "kernel_name": "linux-6.12",
  "source_url": "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.12.tar.xz",
  "source_dir": "/work/sources/linux-6.12",
  "output_dir": "/out/linux-6.12",
  "log_file": "/out/linux-6.12/llbic.log",
  "kernel_build_log": "/out/linux-6.12/kernel-build.log",
  "arch": "x86_64",
  "cross_compile": null,
  "defconfig": "defconfig",
  "build_layout": "intree",
  "kconfig_fragments": [],
  "bitcode_root": "/work/sources/linux-6.12",
  "bitcode_list_file": "/out/linux-6.12/bitcode_files.txt",
  "clang": "clang",
  "llvm_major": "18",
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

## Images

Use the image that matches the kernel era:

| Image | Kernels | Clang |
|---|---|---|
| `ghcr.io/cyruscyliu/llbic:latest` | 6.x, 7.x | 14, 15, 16, 18 |
| `ghcr.io/cyruscyliu/llbic:mid` | 4.x, 5.x | 8, 9, 10, 11, 12 |
| `ghcr.io/cyruscyliu/llbic:legacy` | 2.6, 3.x | 6.0, 7, 8 |

Examples:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:mid 5.15 --clang 12
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:legacy 3.18 --clang 8
```

## Local usage

`./llbic` runs inside Docker and will build the local image if it is missing.
Use `LLBIC_REBUILD=1` to force rebuilding the image.

```bash
./llbic 6.12
./llbic 6.12 --out-of-tree
./llbic 6.12 --clang 18
./llbic 6.12 --output ./out
./llbic --json 6.12
./llbic 6.12 --arch arm64
./llbic 6.12 --arch riscv
```

`--out-of-tree` builds with `make O=<dir>` so the build output lives outside the
extracted source tree. This avoids conflicts when rebuilding the same kernel
with a different `--clang` version.

Artifacts are written under `out/linux-<version>/` by default (override
with `--output`):

- `llbic.log`: end-to-end build log
- `llbic.json`: machine-readable build summary
- `bitcode_files.txt`: list of detected LLVM bitcode files (relative paths under `bitcode_root`)

`--json` also prints the JSON summary to stdout.

Note: `kernel/time/timeconst.bc` in the Linux source tree is an input for the `bc`
calculator (used to generate `include/generated/timeconst.h`), not LLVM bitcode.

## Architecture & Config

Flags:

- `--arch, -a`: `x86_64` (default), `arm`, `arm64`, `mips`, `riscv`
- `--cross`: `CROSS_COMPILE` prefix (defaults are applied for some arches; override as needed)
- `--defconfig`: kbuild config target (default: `defconfig`)
- `--kconfig, -K`: merge one or more Kconfig fragments into the generated `.config` (repeatable)

Example: build ARM64 `defconfig` plus your own config fragment:

```bash
./llbic 6.18.16 --arch arm64 --out-of-tree -K ./my-kconfig.fragment
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
