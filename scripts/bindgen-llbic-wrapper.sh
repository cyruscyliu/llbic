#!/usr/bin/env bash
set -euo pipefail

real_bindgen() {
  if [[ -n "${LLBIC_BINDGEN_REAL:-}" && -x "${LLBIC_BINDGEN_REAL}" ]]; then
    printf '%s\n' "${LLBIC_BINDGEN_REAL}"
    return 0
  fi

  if [[ -x "/usr/local/cargo/bin/bindgen" ]]; then
    printf '%s\n' "/usr/local/cargo/bin/bindgen"
    return 0
  fi

  command -v bindgen
}

active_clang_major() {
  local clang_bin="${CC:-clang}"
  local version_line=""

  version_line="$("${clang_bin}" --version 2>/dev/null | head -n 1 || true)"
  if [[ "${version_line}" =~ clang\ version[[:space:]]+([0-9]+)\. ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  if [[ "${clang_bin}" =~ clang-([0-9]+)$ ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

maybe_set_libclang_path() {
  [[ -n "${LIBCLANG_PATH:-}" ]] && return 0

  local major=""
  local candidate=""

  major="$(active_clang_major || true)"
  [[ -n "${major}" ]] || return 0

  candidate="/usr/lib/llvm-${major}/lib"
  if [[ -r "${candidate}/libclang.so.1" || -r "${candidate}/libclang.so" ]]; then
    export LIBCLANG_PATH="${candidate}"
  fi
}

main() {
  maybe_set_libclang_path
  exec "$(real_bindgen)" "$@"
}

main "$@"
