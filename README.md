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

## Local usage

`./llbic` runs inside Docker and will build the local image if it is missing.
Use `LLBIC_REBUILD=1` to force rebuilding the image.

```bash
./llbic 6.12
./llbic 6.12 --out-of-tree
./llbic 6.12 --clang 18
./llbic 6.12 --output ./out
./llbic --json 6.12
```

`--out-of-tree` builds with `make O=<dir>` so the build output lives outside the
extracted source tree. This avoids conflicts when rebuilding the same kernel
with a different `--clang` version.

Artifacts are written under `out/linux-<version>/` by default (override
with `--output`):

- `llbic.log`: end-to-end build log
- `llbic.json`: machine-readable build summary
- `bitcode_files.txt`: list of generated `.bc` files (relative paths)

`--json` also prints the JSON summary to stdout.

## Community

- Contributions are welcome through issues and pull requests.
- For repo conventions and contribution flow, see [CONTRIBUTING.md](./CONTRIBUTING.md).
- For security reporting guidance, see [SECURITY.md](./SECURITY.md).
- Community participation is covered by [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).
- Legacy patch-oriented workflows remain available in `llbic.py` for older kernel work.

## License

See [LICENSE](LICENSE).
