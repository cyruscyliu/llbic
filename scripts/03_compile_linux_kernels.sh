#!/usr/bin/env bash
set -euo pipefail

MLTA_DIR="${MLTA_DIR:-$PWD/mlta}"
SOURCES_DIR="${SOURCES_DIR:-$PWD/sources}"
SCRIPTS_DIR="${SCRIPTS_DIR:-$PWD/scripts}"
NPROC="${NPROC:-$(nproc)}"

IRGEN_SH="${MLTA_DIR}/irgen.sh"
IRDUMPER_DIR="${MLTA_DIR}/IRDumper"

KERNEL_TREES=(
  "linux-6.18.16"
  "linux-6.19.6"
  "linux-7.0-rc2"
)

if [[ ! -x "${IRGEN_SH}" ]]; then
  echo "Error: irgen.sh not found or not executable: ${IRGEN_SH}" >&2
  exit 1
fi

if [[ ! -d "${IRDUMPER_DIR}" ]]; then
  echo "Error: IRDumper directory not found: ${IRDUMPER_DIR}" >&2
  exit 1
fi

if [[ ! -d "${SOURCES_DIR}" ]]; then
  echo "Error: sources directory not found: ${SOURCES_DIR}" >&2
  exit 1
fi

if [[ ! -f "${SCRIPTS_DIR}/Makefile" ]]; then
  echo "Error: Makefile not found: ${SCRIPTS_DIR}/Makefile" >&2
  exit 1
fi

echo "Building IRDumper..."
make -C "${IRDUMPER_DIR}" NPROC="${NPROC}" dumper

for kernel in "${KERNEL_TREES[@]}"; do
  kernel_src="${SOURCES_DIR}/${kernel}"

  if [[ ! -d "${kernel_src}" ]]; then
    echo "Error: kernel source directory not found: ${kernel_src}" >&2
    exit 1
  fi

  echo "Preparing .config for ${kernel}..."
  make -C "${SCRIPTS_DIR}" linux-defconfig LINUX_PATH="${kernel_src}"

  echo "Running irgen for ${kernel}..."
  (
    cd "${MLTA_DIR}"
    ./irgen.sh "${kernel_src}"
  )
done

echo "Done."
