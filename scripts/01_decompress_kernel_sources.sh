#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC_DIR="${ROOT_DIR}/sources"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "Error: source directory not found: ${SRC_DIR}" >&2
  exit 1
fi

ARCHIVES=(
  "${SRC_DIR}/linux-6.18.16.tar.xz"
  "${SRC_DIR}/linux-6.19.6.tar.xz"
  "${SRC_DIR}/linux-7.0-rc2.tar.gz"
  "${SRC_DIR}/llvm-project-15.0.7.src.tar.xz"
)

for archive in "${ARCHIVES[@]}"; do
  if [[ ! -f "${archive}" ]]; then
    echo "Skipping missing archive: ${archive}"
    continue
  fi

  file_name="$(basename "${archive}")"
  out_name="${file_name%.tar.xz}"
  out_name="${out_name%.tar.gz}"
  out_dir="${SRC_DIR}/${out_name}"

  if [[ -d "${out_dir}" ]]; then
    echo "Skipping ${file_name} (already extracted at ${out_dir})"
    continue
  fi

  echo "Extracting ${file_name}..."
  tar -xf "${archive}" -C "${SRC_DIR}"
done

echo "Done. Extracted sources are in: ${SRC_DIR}"
