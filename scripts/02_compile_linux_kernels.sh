#!/usr/bin/env bash
set -euo pipefail

# Compile Linux kernels to LLVM bitcode for static analysis.
#
# Strategy:
#   - Kernel >= 5.12: use native CONFIG_LTO_CLANG_FULL (best for analysis)
#   - Kernel < 5.12:  use IRDumper pass plugin (fallback)
#
# Usage:
#   bash scripts/02_compile_linux_kernels.sh [CLANG_VERSION]
#
# Examples:
#   bash scripts/02_compile_linux_kernels.sh        # use default clang
#   bash scripts/02_compile_linux_kernels.sh 18     # use clang-18

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCES_DIR="${ROOT_DIR}/sources"
NPROC="${NPROC:-$(nproc)}"

CLANG_VERSION="${1:-}"

# --- Resolve Clang binary ---
if [[ -n "${CLANG_VERSION}" ]]; then
  CLANG="clang-${CLANG_VERSION}"
else
  CLANG="clang"
  CLANG_VERSION="$(${CLANG} --version | grep -oP 'clang version \K[0-9]+')"
fi

if ! command -v "${CLANG}" >/dev/null 2>&1; then
  echo "Error: ${CLANG} not found" >&2
  exit 1
fi

LLVM_MAJOR="$(${CLANG} --version | grep -oP 'clang version \K[0-9]+')"

echo "Using: ${CLANG} ($(${CLANG} --version | head -1))"

if [[ ! -d "${SOURCES_DIR}" ]]; then
  echo "Error: sources directory not found: ${SOURCES_DIR}" >&2
  echo "Hint: run scripts/00 and scripts/01 first" >&2
  exit 1
fi

# --- Find kernel source trees ---
KERNEL_TREES=()
for d in "${SOURCES_DIR}"/linux-*/; do
  [[ -d "${d}" ]] || continue
  KERNEL_TREES+=("${d%/}")
done

if [[ ${#KERNEL_TREES[@]} -eq 0 ]]; then
  echo "Error: no kernel source trees found in ${SOURCES_DIR}" >&2
  exit 1
fi

echo "Found ${#KERNEL_TREES[@]} kernel(s): ${KERNEL_TREES[*]##*/}"
echo ""

# --- Helper: extract kernel version from Makefile ---
kernel_version() {
  local src="$1"
  local ver sub
  ver="$(make -C "${src}" -s kernelversion 2>/dev/null)" || true
  echo "${ver}"
}

# --- Helper: compare version >= threshold ---
version_ge() {
  # Returns 0 (true) if $1 >= $2
  printf '%s\n%s' "$2" "$1" | sort -V -C
}

# --- LTO approach: for kernels >= 5.12 ---
compile_with_lto() {
  local kernel_src="$1"
  local kernel_name="$2"
  local output_dir="$3"

  echo "  Strategy: CONFIG_LTO_CLANG_FULL (native LTO)"

  # Generate defconfig then enable full LTO
  echo "  Generating defconfig + LTO config..."
  make -C "${kernel_src}" CC="${CLANG}" LLVM=1 defconfig -j"${NPROC}" > /dev/null 2>&1

  # Enable LTO and disable incompatible options
  "${kernel_src}/scripts/config" --file "${kernel_src}/.config" \
    --enable LTO_CLANG \
    --enable LTO_CLANG_FULL \
    --disable LTO_CLANG_THIN \
    --disable LTO_NONE \
    --disable MODVERSIONS

  # Regenerate config with new options resolved
  make -C "${kernel_src}" CC="${CLANG}" LLVM=1 olddefconfig -j"${NPROC}" > /dev/null 2>&1

  # Compile — with full LTO, .o files in vmlinux.a are LLVM bitcode
  echo "  Compiling with ${CLANG} + full LTO..."
  make -C "${kernel_src}" \
    CC="${CLANG}" \
    LLVM=1 \
    -j"${NPROC}" \
    2>&1 | tee "${SOURCES_DIR}/${kernel_name}-build.log"

  # Collect bitcode: with full LTO, object files ARE bitcode
  echo "  Collecting bitcode files..."
  mkdir -p "${output_dir}"

  # .o files under LTO are actually LLVM bitcode; verify and copy
  local bc_count=0
  while IFS= read -r -d '' obj; do
    if file "${obj}" | grep -q "LLVM IR bitcode"; then
      cp "${obj}" "${output_dir}/$(basename "${obj}" .o).bc"
      ((bc_count++))
    fi
  done < <(find "${kernel_src}" -name '*.o' -print0)

  # Also link all bitcode into a single vmlinux.bc
  if [[ ${bc_count} -gt 0 ]]; then
    echo "  Linking ${bc_count} .bc files into vmlinux.bc..."
    find "${output_dir}" -name '*.bc' | \
      xargs llvm-link -o "${output_dir}/vmlinux.bc" 2>/dev/null || \
      echo "  Warning: llvm-link failed (may need more memory for large kernels)"
  fi

  echo "  Collected ${bc_count} bitcode files in ${output_dir}"
}

# --- IRDumper approach: for kernels < 5.12 ---
compile_with_irdumper() {
  local kernel_src="$1"
  local kernel_name="$2"
  local output_dir="$3"

  echo "  Strategy: IRDumper pass plugin (fallback)"

  # Resolve IRDumper
  local irdumper_so="/opt/IRDumper/${CLANG_VERSION}/libDumper.so"
  if [[ ! -f "${irdumper_so}" ]]; then
    echo "Error: IRDumper not found: ${irdumper_so}" >&2
    echo "Available versions:" >&2
    ls /opt/IRDumper/ 2>/dev/null >&2 || echo "  (none)" >&2
    exit 1
  fi

  # Build flags based on LLVM version
  local dumper_flags
  if [[ "${LLVM_MAJOR}" -ge 17 ]]; then
    dumper_flags="-Wno-error -g -fpass-plugin=${irdumper_so}"
  elif [[ "${LLVM_MAJOR}" -ge 15 ]]; then
    dumper_flags="-Wno-error -g -Xclang -no-opaque-pointers -fpass-plugin=${irdumper_so}"
  elif [[ "${LLVM_MAJOR}" -ge 14 ]]; then
    dumper_flags="-Wno-error -g -fpass-plugin=${irdumper_so}"
  else
    dumper_flags="-Wno-error -g -Xclang -flegacy-pass-manager -Xclang -load -Xclang ${irdumper_so}"
  fi

  echo "  IRDumper: ${irdumper_so}"
  echo "  Flags: ${dumper_flags}"

  local kernel_makefile="${kernel_src}/Makefile"
  local marker="# --- IRDumper flags (auto-injected) ---"

  # Generate defconfig
  echo "  Generating defconfig..."
  make -C "${kernel_src}" CC="${CLANG}" LLVM=1 defconfig -j"${NPROC}" > /dev/null 2>&1

  # Patch Makefile
  if ! grep -qF "${marker}" "${kernel_makefile}"; then
    cat >> "${kernel_makefile}" <<EOF

${marker}
KBUILD_USERCFLAGS += ${dumper_flags}
KBUILD_CFLAGS += ${dumper_flags}
EOF
    echo "  Patched ${kernel_makefile}"
  fi

  # Compile
  echo "  Compiling with ${CLANG} + IRDumper..."
  make -C "${kernel_src}" \
    CC="${CLANG}" \
    LLVM=1 \
    -j"${NPROC}" \
    2>&1 | tee "${SOURCES_DIR}/${kernel_name}-build.log"

  # Restore Makefile
  if grep -qF "${marker}" "${kernel_makefile}"; then
    local marker_line
    marker_line="$(grep -nF "${marker}" "${kernel_makefile}" | head -1 | cut -d: -f1)"
    head -n "$((marker_line - 2))" "${kernel_makefile}" > "${kernel_makefile}.tmp"
    mv "${kernel_makefile}.tmp" "${kernel_makefile}"
  fi

  # Collect .bc files
  echo "  Collecting .bc files..."
  mkdir -p "${output_dir}"
  find "${kernel_src}" -name '*.bc' -exec cp {} "${output_dir}/" \;

  local bc_count
  bc_count="$(find "${output_dir}" -name '*.bc' | wc -l)"

  # Link into vmlinux.bc
  if [[ ${bc_count} -gt 0 ]]; then
    echo "  Linking ${bc_count} .bc files into vmlinux.bc..."
    find "${output_dir}" -name '*.bc' ! -name 'vmlinux.bc' | \
      xargs llvm-link -o "${output_dir}/vmlinux.bc" 2>/dev/null || \
      echo "  Warning: llvm-link failed"
  fi

  echo "  Collected ${bc_count} bitcode files in ${output_dir}"
}

# --- Main loop ---
for kernel_src in "${KERNEL_TREES[@]}"; do
  kernel_name="$(basename "${kernel_src}")"
  output_dir="${ROOT_DIR}/build/${kernel_name}"
  kver="$(kernel_version "${kernel_src}")"

  echo "=== ${kernel_name} (${kver}) ==="

  if version_ge "${kver}" "5.12"; then
    compile_with_lto "${kernel_src}" "${kernel_name}" "${output_dir}"
  else
    compile_with_irdumper "${kernel_src}" "${kernel_name}" "${output_dir}"
  fi

  echo ""
done

echo "Done. Bitcode output is in: ${ROOT_DIR}/build/"
