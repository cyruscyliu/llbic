#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${ROOT_DIR}/sources"

mkdir -p "${OUT_DIR}"

URLS=(
  "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.18.16.tar.xz"
  "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.19.6.tar.xz"
  "https://git.kernel.org/torvalds/t/linux-7.0-rc2.tar.gz"
  "https://github.com/llvm/llvm-project/releases/download/llvmorg-15.0.7/llvm-project-15.0.7.src.tar.xz"
)

download_with_curl() {
  local url="$1"
  local out="$2"
  curl -fL --retry 3 --retry-delay 2 -o "${out}" "${url}"
}

download_with_wget() {
  local url="$1"
  local out="$2"
  wget -O "${out}" "${url}"
}

if command -v curl >/dev/null 2>&1; then
  DOWNLOADER="curl"
elif command -v wget >/dev/null 2>&1; then
  DOWNLOADER="wget"
else
  echo "Error: neither curl nor wget is installed." >&2
  exit 1
fi

for url in "${URLS[@]}"; do
  file_name="$(basename "${url}")"
  output_path="${OUT_DIR}/${file_name}"

  if [[ -s "${output_path}" ]]; then
    echo "Skipping ${file_name} (already exists)"
    continue
  fi

  echo "Downloading ${file_name}..."
  if [[ "${DOWNLOADER}" == "curl" ]]; then
    download_with_curl "${url}" "${output_path}"
  else
    download_with_wget "${url}" "${output_path}"
  fi
done

echo "Done. Files are in: ${OUT_DIR}"
