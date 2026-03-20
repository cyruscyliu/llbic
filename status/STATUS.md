# llbic Support Status

- Generated: `2026-03-20T16:01:41+00:00`
- Git SHA: `5aa788a273c0747c03e83dba70838f6d2a2dc913`
- Build root: `out`
- Warnings: `1`

| Arch | Clang | Kernel | Result | Bitcode | vmlinux |
|---|---|---|---|---|---|
| `arm64` | `15` | `6.18.16` | **success** | yes | yes |
| `x86_64` | `18` | `6.18.16` | **success** | yes | no |

Field meanings:
- `result`: copied from `llbic.json.status`
- `bitcode`: true when `bitcode_count > 0`
- `vmlinux`: true when `kernel_images` contains `vmlinux`

Warnings:
- x86_64::18::6.18.16 is currently broken: result=success, bitcode_emitted=True, vmlinux_present=False

