#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_checked(args: list[str], cwd: Path | None = None) -> str:
    p = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {args}\n{p.stderr.strip()}")
    return p.stdout.strip()


def safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def row_key(row: dict[str, Any]) -> str:
    return (
        f"{row.get('arch', 'unknown')}::"
        f"{row.get('clang', 'unknown')}::"
        f"{row.get('kernel', 'unknown')}"
    )


def result_is_success(result: Any) -> bool:
    return str(result) in {"pass", "success"}


def row_is_passing(row: dict[str, Any]) -> bool:
    return (
        result_is_success(row.get("result"))
        and bool(row.get("bitcode_emitted"))
        and bool(row.get("vmlinux_present"))
    )


def collect_rows(repo_root: Path, build_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for manifest in sorted(build_root.rglob("llbic.json")):
        payload = safe_read_json(manifest)
        if not payload:
            continue

        kernel_images = payload.get("kernel_images") or []
        if not isinstance(kernel_images, list):
            kernel_images = []

        bitcode_count = int(payload.get("bitcode_count") or 0)
        bitcode_emitted = bitcode_count > 0
        vmlinux_present = "vmlinux" in kernel_images
        clang = str(
            payload.get("requested_clang")
            or payload.get("llvm_major")
            or payload.get("clang")
            or "unknown"
        )

        rows.append(
            {
                "kernel": str(
                    payload.get("kernel_version")
                    or manifest.parent.name.removeprefix("linux-")
                ),
                "arch": str(payload.get("arch") or "unknown"),
                "clang": clang,
                "result": str(payload.get("status") or "unknown"),
                "bitcode_emitted": bitcode_emitted,
                "vmlinux_present": vmlinux_present,
                "paths": {
                    "manifest": str(manifest.relative_to(repo_root)),
                },
            }
        )

    rows.sort(key=lambda row: (row.get("arch", ""), row.get("clang", ""), row.get("kernel", "")))
    return rows


def compare_with_existing(
    current_rows: list[dict[str, Any]], existing_rows: list[dict[str, Any]]
) -> list[str]:
    warnings: list[str] = []
    existing_by_key = {row_key(row): row for row in existing_rows}

    for row in current_rows:
        key = row_key(row)
        existing = existing_by_key.get(key)

        if not row_is_passing(row):
            warnings.append(
                f"{key} is currently broken: result={row.get('result')}, "
                f"bitcode_emitted={row.get('bitcode_emitted')}, "
                f"vmlinux_present={row.get('vmlinux_present')}"
            )

        if not existing:
            continue

        if row_is_passing(existing) and not row_is_passing(row):
            warnings.append(
                f"{key} regressed: passing support changed from true to false"
            )

        if bool(existing.get("bitcode_emitted")) and not bool(row.get("bitcode_emitted")):
            warnings.append(f"{key} regressed: bitcode_emitted changed from true to false")

        if bool(existing.get("vmlinux_present")) and not bool(row.get("vmlinux_present")):
            warnings.append(f"{key} regressed: vmlinux_present changed from true to false")

    return warnings


def render_status_md(status: dict[str, Any]) -> str:
    lines: list[str] = []
    meta = status["meta"]

    lines.append("# llbic Support Status")
    lines.append("")
    lines.append(f"- Generated: `{meta['generated_at']}`")
    lines.append(f"- Git SHA: `{meta['git_sha']}`")
    lines.append(f"- Build root: `{meta['build_root']}`")
    warning_count = len(status.get("warnings", []))
    lines.append(f"- Warnings: `{warning_count}`")
    lines.append("")
    lines.append("| Arch | Clang | Kernel | Result | Bitcode | vmlinux |")
    lines.append("|---|---|---|---|---|---|")

    for row in status["rows"]:
        arch = row["arch"]
        clang = row.get("clang", "unknown")
        kernel = row["kernel"]
        result = row["result"]
        bitcode = "yes" if row["bitcode_emitted"] else "no"
        vmlinux = "yes" if row["vmlinux_present"] else "no"
        lines.append(
            f"| `{arch}` | `{clang}` | `{kernel}` | **{result}** | {bitcode} | {vmlinux} |"
        )

    lines.append("")
    lines.append("Field meanings:")
    lines.append("- `result`: copied from `llbic.json.status`")
    lines.append("- `bitcode`: true when `bitcode_count > 0`")
    lines.append("- `vmlinux`: true when `kernel_images` contains `vmlinux`")
    if status.get("warnings"):
        lines.append("")
        lines.append("Warnings:")
        for warning in status["warnings"]:
            lines.append(f"- {warning}")
    lines.append("")
    return "\n".join(lines)


def badge_color(passed: int, total: int) -> str:
    if total == 0:
        return "lightgrey"
    if passed == total:
        return "brightgreen"
    if passed == 0:
        return "red"
    return "yellow"


def write_badges(status: dict[str, Any], badges_dir: Path) -> list[Path]:
    rows = status["rows"]
    total = len(rows)
    pass_count = sum(1 for row in rows if row_is_passing(row))
    bitcode_count = sum(1 for row in rows if row.get("bitcode_emitted"))
    vmlinux_count = sum(1 for row in rows if row.get("vmlinux_present"))

    badges = {
        "overall.json": {
            "schemaVersion": 1,
            "label": "status board",
            "message": f"{pass_count}/{total} passing",
            "color": badge_color(pass_count, total),
        },
        "bitcode.json": {
            "schemaVersion": 1,
            "label": "bitcode",
            "message": f"{bitcode_count}/{total} emitted",
            "color": badge_color(bitcode_count, total),
        },
        "vmlinux.json": {
            "schemaVersion": 1,
            "label": "vmlinux",
            "message": f"{vmlinux_count}/{total} built",
            "color": badge_color(vmlinux_count, total),
        },
    }

    badges_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in badges.items():
        path = badges_dir / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        written.append(path)
    return written


def print_badge_summary(status: dict[str, Any]) -> None:
    rows = status["rows"]
    total = len(rows)
    pass_count = sum(1 for row in rows if row_is_passing(row))
    bitcode_count = sum(1 for row in rows if row.get("bitcode_emitted"))
    vmlinux_count = sum(1 for row in rows if row.get("vmlinux_present"))

    print("badges:")
    print(f"  status board: {pass_count}/{total} passing")
    print(f"  bitcode:      {bitcode_count}/{total} emitted")
    print(f"  vmlinux:      {vmlinux_count}/{total} built")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Collect simplified support results by reading completed llbic.json manifests."
    )
    ap.add_argument(
        "--build-root",
        default="out",
        help="Directory containing llbic build outputs such as out/linux-6.18.16-x86_64-clang18/ (default: out).",
    )
    ap.add_argument(
        "--json-out",
        default="status/status.json",
        help="Where to write the collected machine-readable results.",
    )
    ap.add_argument(
        "--md-out",
        default="status/STATUS.md",
        help="Where to write the rendered Markdown status table.",
    )
    ap.add_argument(
        "--badges-dir",
        default="status/badges",
        help="Where to write badge endpoint JSON files when there are no warnings.",
    )
    ap.add_argument(
        "--force-badges",
        action="store_true",
        help="Write badge endpoint JSON files even when warnings are present.",
    )
    ap.add_argument(
        "--print-badges",
        action="store_true",
        help="Print the current badge summary in plain text.",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    build_root = (repo_root / args.build_root).resolve()
    json_out = (repo_root / args.json_out).resolve()
    md_out = (repo_root / args.md_out).resolve()
    badges_dir = (repo_root / args.badges_dir).resolve()

    if not build_root.exists():
        raise SystemExit(f"build root not found: {build_root}")

    try:
        git_sha = run_checked(["git", "rev-parse", "HEAD"], cwd=repo_root)
    except Exception:
        git_sha = "unknown"

    rows = collect_rows(repo_root, build_root)
    existing_status = safe_read_json(json_out) or {}
    existing_rows = existing_status.get("rows") or []
    if not isinstance(existing_rows, list):
        existing_rows = []
    warnings = compare_with_existing(rows, existing_rows)

    status = {
        "meta": {
            "generated_at": utc_now_iso(),
            "git_sha": git_sha,
            "build_root": str(build_root.relative_to(repo_root)),
        },
        "rows": rows,
        "warnings": warnings,
    }

    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    md_out.write_text(render_status_md(status) + "\n")

    print(f"wrote {json_out.relative_to(repo_root)}")
    print(f"wrote {md_out.relative_to(repo_root)}")
    for warning in warnings:
        print(f"warning: {warning}")

    if warnings and not args.force_badges:
        print("warning: badges not updated because warnings are present")
    else:
        if warnings and args.force_badges:
            print("warning: forcing badge update despite warnings")
        for path in write_badges(status, badges_dir):
            print(f"wrote {path.relative_to(repo_root)}")

    if args.print_badges:
        print_badge_summary(status)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
