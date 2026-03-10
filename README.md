# llbic

Compile Linux kernels to source code, LLVM bitcode, and kernel images with one stable command.

[![Docker Publish](https://github.com/cyruscyliu/llbic/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/cyruscyliu/llbic/actions/workflows/docker-publish.yml)
[![Container Registry](https://img.shields.io/badge/ghcr.io-llbic-blue)](https://github.com/cyruscyliu/llbic/pkgs/container/llbic)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

`llbic` is a one-shot interface for turning a Linux kernel version into a reproducible build workspace.
It is designed for researchers, tool builders, and agent workflows that need stable kernel artifacts instead of ad hoc scripts.

## Quick start

Docker is the default workflow:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12
```

This downloads the kernel source, builds it, and writes output to:

```text
out/linux-6.12/
  llbic.log
  vmlinux.bc
  *.bc
```

Use `--clang` to pick a toolchain:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12 --clang 18
```

For agents, use JSON output:

```bash
docker run --rm -v "$(pwd)/out:/out" ghcr.io/cyruscyliu/llbic:latest 6.12 --json
```

What you get from one run:

- Resolved kernel source tarball from `kernel.org`
- Extracted source tree
- Per-file `.bc` artifacts and linked `vmlinux.bc`
- Compiled kernel image when produced by the target kernel
- End-to-end `llbic.log`
- Optional JSON output for agents

Example response:

```json
{
  "status": "success",
  "kernel_version": "6.12",
  "kernel_name": "linux-6.12",
  "source_url": "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.12.tar.xz",
  "source_dir": "/home/llbic/sources/linux-6.12",
  "output_dir": "/out/linux-6.12",
  "log_file": "/out/linux-6.12/llbic.log",
  "clang": "clang",
  "llvm_major": "18",
  "bitcode_files": [
    "/out/linux-6.12/vmlinux.bc"
  ],
  "bitcode_count": 1,
  "vmlinux_bc": "/out/linux-6.12/vmlinux.bc",
  "kernel_images": [
    "/home/llbic/sources/linux-6.12/vmlinux"
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

## Why llbic

- One command instead of download, extract, patch, compile, and collect steps
- Stable Docker-based environment for reproducible experiments
- Human-friendly CLI and machine-friendly JSON mode
- Per-version output layout that works well for batch runs and automation

## Local usage

```bash
./llbic 6.12
./llbic 6.12 --clang 18
./llbic 6.12 --output ./out
./llbic --json 6.12
```

Each one-shot run writes a timestamped end-to-end log to
`out/linux-<version>/llbic.log`.

## CLI

```text
llbic <version> [--clang VER] [--output DIR] [--json]
llbic <command> [options]
```

Commands:

- `build <VERSION>`: download, extract, compile
- `compile [KERNEL]`: compile extracted sources
- `download [VERSION|URL]`: fetch sources directly
- `extract`: unpack archives
- `list`: show sources and outputs
- `clean [TARGET]`: remove `build`, `sources`, or both
- `version`: print version

## Community

- Contributions are welcome through issues and pull requests.
- For repo conventions and contribution flow, see [CONTRIBUTING.md](./CONTRIBUTING.md).
- Legacy patch-oriented workflows remain available in `llbic.py` for older kernel work.

## Build images

```bash
docker compose build llbic
docker compose build llbic-mid
docker compose build llbic-legacy
```

## License

See [LICENSE](LICENSE).
