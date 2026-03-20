#!/usr/bin/env bash
set -euo pipefail

real_rustc() {
  if [[ -n "${LLBIC_RUSTC_REAL:-}" && -x "${LLBIC_RUSTC_REAL}" ]]; then
    printf '%s\n' "${LLBIC_RUSTC_REAL}"
    return 0
  fi

  rustup which rustc
}

should_emit_bc() {
  [[ "${LLBIC_RUSTC_EMIT_LLVM_BC:-1}" == "1" ]]
}

main() {
  local rustc_bin
  rustc_bin="$(real_rustc)"

  if ! should_emit_bc; then
    exec "${rustc_bin}" "$@"
  fi

  local arg=""
  local obj_out=""
  local has_bc_emit=0
  local has_ll_emit=0
  local -a forwarded=()

  for arg in "$@"; do
    case "${arg}" in
      --emit=obj=*)
        obj_out="${arg#--emit=obj=}"
        ;;
      --emit=llvm-bc=*|--emit=llvm-bc)
        has_bc_emit=1
        ;;
      --emit=llvm-ir=*|--emit=llvm-ir)
        has_ll_emit=1
        ;;
    esac
    forwarded+=("${arg}")
  done

  if [[ -n "${obj_out}" && "${has_bc_emit}" -eq 0 && "${has_ll_emit}" -eq 0 ]]; then
    forwarded+=("--emit=llvm-bc=${obj_out%.o}.bc")
  fi

  exec "${rustc_bin}" "${forwarded[@]}"
}

main "$@"
