#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_checked(args: list[str], cwd: Path | None = None) -> str:
    p = subprocess.run(args, cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {args}\n{p.stderr.strip()}")
    return p.stdout.strip()


def normalize_kernel_name(kernel: str) -> str:
    kernel = kernel.strip()
    if kernel.startswith("linux-"):
        kernel = kernel[len("linux-") :]
    return f"linux-{kernel}"


def guess_image_from_kernel(kernel: str) -> str:
    # Keep in sync with llbic wrapper logic: 2/3 -> legacy, 4/5 -> mid, else latest.
    m = re.match(r"^linux-([0-9]+)\.", kernel)
    if not m:
        m = re.match(r"^([0-9]+)\.", kernel)
    major = int(m.group(1)) if m else None
    if major in (2, 3):
        return "ghcr.io/cyruscyliu/llbic:legacy"
    if major in (4, 5):
        return "ghcr.io/cyruscyliu/llbic:mid"
    return "ghcr.io/cyruscyliu/llbic:latest"


def tail_text(path: Path, lines: int = 80) -> str:
    try:
        data = path.read_text(errors="replace").splitlines()
    except FileNotFoundError:
        return ""
    if len(data) <= lines:
        return "\n".join(data)
    return "\n".join(data[-lines:])


def safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


@dataclass
class Target:
    kernel: str
    layout: str
    image: str
    clang: str
    output: str | None
    timeout_sec: int
    notes: str


def load_matrix(path: Path) -> tuple[dict[str, Any], list[Target]]:
    raw = json.loads(path.read_text())
    if raw.get("version") != 1:
        raise RuntimeError(f"unsupported matrix format version: {raw.get('version')}")

    defaults = raw.get("defaults", {})

    def get_default(key: str, fallback: Any) -> Any:
        v = defaults.get(key, fallback)
        return v

    targets: list[Target] = []
    for t in raw.get("targets", []):
        kernel = str(t["kernel"])
        layout = str(t.get("layout", get_default("layout", "outtree")))
        image = str(t.get("image", get_default("image", "auto")))
        clang = str(t.get("clang", get_default("clang", "auto")))
        output = t.get("output", get_default("output", None))
        timeout_sec = int(t.get("timeout_sec", get_default("timeout_sec", 14400)))
        notes = str(t.get("notes", ""))
        targets.append(
            Target(
                kernel=kernel,
                layout=layout,
                image=image,
                clang=clang,
                output=output,
                timeout_sec=timeout_sec,
                notes=notes,
            )
        )

    return raw, targets


def build_llbic_cmd(t: Target) -> list[str]:
    cmd = ["./llbic", t.kernel]
    if t.layout == "outtree":
        cmd.append("--out-of-tree")
    elif t.layout == "intree":
        cmd.append("--intree")
    else:
        raise RuntimeError(f"unknown layout: {t.layout}")

    if t.clang != "auto":
        cmd += ["--clang", t.clang]

    if t.output:
        cmd += ["--output", t.output]

    return cmd


def env_for_target(t: Target) -> dict[str, str]:
    env = dict(os.environ)
    if t.image != "auto":
        env["LLBIC_IMAGE"] = t.image
    return env


def compute_out_dir(repo_root: Path, t: Target) -> Path:
    # Mirror llbic default: /out inside the container maps to ./out on host.
    # If user specifies --output, treat it as relative to repo root unless absolute.
    if t.output:
        p = Path(t.output)
        out_root = p if p.is_absolute() else (repo_root / p)
    else:
        out_root = repo_root / "out"

    return out_root / normalize_kernel_name(t.kernel)


def render_status_md(status: dict[str, Any]) -> str:
    lines: list[str] = []
    meta = status["meta"]
    lines.append("# llbic Support Status")
    lines.append("")
    lines.append(f"- Generated: `{meta['generated_at']}`")
    lines.append(f"- Git SHA: `{meta['git_sha']}`")
    lines.append("")
    lines.append("| Kernel | Result | Image | Clang | Layout | Bitcode | vmlinux.bc | Notes |")
    lines.append("|---|---|---|---|---|---:|---|---|")
    for row in status["rows"]:
        kernel = row["kernel"]
        result = row["result"]
        image = row.get("image_effective", "")
        clang = row.get("clang_effective", "")
        layout = row.get("layout", "")
        bitcode_count = row.get("bitcode_count", 0)
        vmlinux = "yes" if row.get("vmlinux_bc") else "no"
        notes = row.get("notes", "")
        lines.append(f"| `{kernel}` | **{result}** | `{image}` | `{clang}` | `{layout}` | {bitcode_count} | {vmlinux} | {notes} |")
    lines.append("")
    lines.append("Result definition:")
    lines.append("- pass: build completed and produced at least one `.bc` file")
    lines.append("- fail: build failed or no `.bc` files were produced")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run llbic test matrix and generate a support status board.")
    ap.add_argument("--matrix", default="status/matrix.json", help="Path to matrix json.")
    ap.add_argument("--out", default="status", help="Output directory for status board files.")
    ap.add_argument("--rebuild", action="store_true", help="Force Docker image rebuilds (sets LLBIC_REBUILD=1).")
    ap.add_argument("--dry-run", action="store_true", help="Print commands but do not execute.")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    matrix_path = (repo_root / args.matrix).resolve()
    out_dir = (repo_root / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        git_sha = run_checked(["git", "rev-parse", "HEAD"], cwd=repo_root)
    except Exception:
        git_sha = "unknown"

    raw_matrix, targets = load_matrix(matrix_path)

    if args.dry_run:
        for t in targets:
            cmd = build_llbic_cmd(t)
            env = env_for_target(t)
            if args.rebuild:
                env["LLBIC_REBUILD"] = "1"
            env_prefix = ""
            for k in ("LLBIC_IMAGE", "LLBIC_REBUILD"):
                if k in env and env[k]:
                    env_prefix += f"{k}={shlex.quote(env[k])} "
            print(env_prefix + " ".join(shlex.quote(c) for c in cmd))
        return 0

    status: dict[str, Any] = {
        "meta": {
            "generated_at": utc_now_iso(),
            "git_sha": git_sha,
            "matrix_file": str(matrix_path.relative_to(repo_root)),
            "matrix": raw_matrix,
        },
        "rows": [],
    }

    for t in targets:
        cmd = build_llbic_cmd(t)
        env = env_for_target(t)
        if args.rebuild:
            env["LLBIC_REBUILD"] = "1"

        out_kernel_dir = compute_out_dir(repo_root, t)
        llbic_json = out_kernel_dir / "llbic.json"
        bc_list = out_kernel_dir / "bitcode_files.txt"
        kernel_build_log = out_kernel_dir / "kernel-build.log"
        llbic_log = out_kernel_dir / "llbic.log"

        started = time.time()
        rc = None
        err: str = ""
        try:
            p = subprocess.run(
                cmd,
                cwd=str(repo_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=t.timeout_sec,
            )
            rc = p.returncode
            # Keep stderr tail for quick diagnosis in the status JSON.
            err = p.stderr.strip()
        except subprocess.TimeoutExpired:
            rc = 124
            err = f"timeout after {t.timeout_sec}s"

        duration_sec = int(time.time() - started)

        j = safe_read_json(llbic_json)
        bitcode_count = 0
        vmlinux_bc = None
        clang_effective = t.clang
        image_effective = t.image

        if j:
            bitcode_count = int(j.get("bitcode_count") or 0)
            vmlinux_bc = j.get("vmlinux_bc")
            clang_effective = str(j.get("llvm_major") or t.clang)
            image_effective = env.get("LLBIC_IMAGE") or guess_image_from_kernel(t.kernel)

        # Fall back to bitcode list file if JSON is missing/partial.
        if bitcode_count == 0 and bc_list.exists():
            try:
                bitcode_count = len([ln for ln in bc_list.read_text().splitlines() if ln.strip()])
            except Exception:
                pass

        result = "pass" if (rc == 0 and bitcode_count > 0) else "fail"

        row: dict[str, Any] = {
            "kernel": t.kernel,
            "layout": t.layout,
            "image": t.image,
            "image_effective": image_effective,
            "clang": t.clang,
            "clang_effective": clang_effective,
            "output_dir": str(out_kernel_dir.relative_to(repo_root)),
            "exit_code": rc,
            "duration_sec": duration_sec,
            "result": result,
            "bitcode_count": bitcode_count,
            "vmlinux_bc": vmlinux_bc,
            "notes": t.notes,
            "paths": {
                "llbic_json": str(llbic_json.relative_to(repo_root)) if llbic_json.exists() else None,
                "bitcode_list": str(bc_list.relative_to(repo_root)) if bc_list.exists() else None,
                "kernel_build_log": str(kernel_build_log.relative_to(repo_root)) if kernel_build_log.exists() else None,
                "llbic_log": str(llbic_log.relative_to(repo_root)) if llbic_log.exists() else None,
            },
        }

        if result != "pass":
            row["error_tail"] = {
                "stderr_tail": "\n".join(err.splitlines()[-40:]) if err else "",
                "kernel_build_log_tail": tail_text(kernel_build_log, lines=80),
                "llbic_log_tail": tail_text(llbic_log, lines=80),
            }

        status["rows"].append(row)

    status_json_path = out_dir / "status.json"
    status_md_path = out_dir / "STATUS.md"
    status_json_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    status_md_path.write_text(render_status_md(status))

    print(f"wrote {status_json_path.relative_to(repo_root)}")
    print(f"wrote {status_md_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
