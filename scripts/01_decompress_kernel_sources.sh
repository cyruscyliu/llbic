#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC_DIR="${ROOT_DIR}/sources"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "Error: source directory not found: ${SRC_DIR}" >&2
  echo "Hint: run scripts/00_download_kernel_sources.sh first" >&2
  exit 1
fi

for archive in "${SRC_DIR}"/*.tar.{xz,gz,bz2}; do
  [[ -f "${archive}" ]] || continue

  file_name="$(basename "${archive}")"
  out_name="${file_name%.tar.*}"
  out_dir="${SRC_DIR}/${out_name}"

  if [[ -d "${out_dir}" ]]; then
    echo "Skipping ${file_name} (already extracted)"
    continue
  fi

  echo "Extracting ${file_name}..."
  tar -xf "${archive}" -C "${SRC_DIR}"
done

echo "Done. Extracted sources are in: ${SRC_DIR}"
