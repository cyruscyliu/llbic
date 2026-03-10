#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${ROOT_DIR}/sources"
CONF_FILE="${ROOT_DIR}/sources.conf"

if [[ ! -f "${CONF_FILE}" ]]; then
  echo "Error: config file not found: ${CONF_FILE}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

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

while IFS= read -r line; do
  # Skip blank lines and comments
  [[ -z "${line}" || "${line}" =~ ^[[:space:]]*# ]] && continue

  url="${line}"
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
done < "${CONF_FILE}"

echo "Done. Files are in: ${OUT_DIR}"
