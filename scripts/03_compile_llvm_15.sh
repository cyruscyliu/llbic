#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC_DIR="${ROOT_DIR}/sources"

LLVM_SRC_DIR="${SRC_DIR}/llvm-project-15.0.7.src"
LLVM_BUILD_DIR="${ROOT_DIR}/build/llvm-15.0.7"
LLVM_INSTALL_DIR="${ROOT_DIR}/build/llvm"

CMAKE_GENERATOR="${CMAKE_GENERATOR:-Ninja}"
NPROC="${NPROC:-$(nproc)}"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "Error: source directory not found: ${SRC_DIR}" >&2
  exit 1
fi

if [[ ! -d "${LLVM_SRC_DIR}" ]]; then
  echo "Error: LLVM source directory not found: ${LLVM_SRC_DIR}" >&2
  echo "Hint: your extracted tree may be ${SRC_DIR}/llvm-project-22.1.0.src" >&2
  exit 1
fi

if ! command -v cmake >/dev/null 2>&1; then
  echo "Error: cmake is not installed or not in PATH." >&2
  exit 1
fi

if ! command -v ninja >/dev/null 2>&1 && [[ "${CMAKE_GENERATOR}" == "Ninja" ]]; then
  echo "Error: ninja is not installed or not in PATH." >&2
  exit 1
fi

mkdir -p "${LLVM_BUILD_DIR}" "${LLVM_INSTALL_DIR}"

cmake -S "${LLVM_SRC_DIR}/llvm" -B "${LLVM_BUILD_DIR}" -G "${CMAKE_GENERATOR}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="${LLVM_INSTALL_DIR}" \
  -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra;lld" \
  -DLLVM_ENABLE_RUNTIMES="compiler-rt" \
  -DLLVM_TARGETS_TO_BUILD="AArch64;X86"

cmake --build "${LLVM_BUILD_DIR}" -- -j"${NPROC}"
cmake --install "${LLVM_BUILD_DIR}"

echo "Done. LLVM is installed at: ${LLVM_INSTALL_DIR}"
