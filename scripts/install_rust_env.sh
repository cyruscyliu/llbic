#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/install_rust_env.sh [--system] [--toolchain TOOLCHAIN] [--set-default]

Installs a Rust toolchain suitable for Linux kernel Rust builds and bindgen use.

Defaults:
  --toolchain stable
  Does not change the rustup default toolchain unless --set-default is passed

Modes:
  default   Install into the current user's ~/.cargo and ~/.rustup
  --system  Install into /usr/local/{cargo,rustup} and symlink tools into /usr/local/bin

Installed components:
  - rustup
  - rustc
  - cargo
  - rust-src
  - rustfmt
  - bindgen-cli
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '[+] %s\n' "$*" >&2
}

SYSTEM_INSTALL=0
TOOLCHAIN="stable"
SET_DEFAULT=0

toolchain_bin() {
  local tool="$1"
  rustup which --toolchain "${TOOLCHAIN}" "${tool}" 2>/dev/null || true
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system)
      SYSTEM_INSTALL=1
      shift
      ;;
    --toolchain)
      [[ $# -ge 2 ]] || die "--toolchain requires a value"
      TOOLCHAIN="$2"
      shift 2
      ;;
    --set-default)
      SET_DEFAULT=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

command -v curl >/dev/null 2>&1 || die "curl is required"

if [[ "${SYSTEM_INSTALL}" -eq 1 ]]; then
  export CARGO_HOME="/usr/local/cargo"
  export RUSTUP_HOME="/usr/local/rustup"
  mkdir -p "${CARGO_HOME}" "${RUSTUP_HOME}"
else
  export CARGO_HOME="${CARGO_HOME:-${HOME}/.cargo}"
  export RUSTUP_HOME="${RUSTUP_HOME:-${HOME}/.rustup}"
  mkdir -p "${CARGO_HOME}" "${RUSTUP_HOME}"
fi

export PATH="${CARGO_HOME}/bin:${PATH}"

if [[ ! -x "${CARGO_HOME}/bin/rustup" ]]; then
  log "Installing rustup into ${CARGO_HOME}"
  curl https://sh.rustup.rs -sSf | sh -s -- -y --profile minimal --default-toolchain none
fi

log "Installing Rust toolchain: ${TOOLCHAIN}"
rustup toolchain install "${TOOLCHAIN}" --profile minimal
if [[ "${SET_DEFAULT}" -eq 1 ]]; then
  rustup default "${TOOLCHAIN}"
fi
rustup component add --toolchain "${TOOLCHAIN}" rust-src
rustup component add --toolchain "${TOOLCHAIN}" rustfmt

log "Installing bindgen-cli"
cargo +"${TOOLCHAIN}" install --locked bindgen-cli --force

if [[ "${SYSTEM_INSTALL}" -eq 1 ]]; then
  ln -sf "${CARGO_HOME}/bin/rustup" "/usr/local/bin/rustup"
  if [[ -x "${CARGO_HOME}/bin/bindgen" ]]; then
    ln -sf "${CARGO_HOME}/bin/bindgen" "/usr/local/bin/bindgen"
  fi

  for tool in cargo rustc rustdoc rustfmt cargo-fmt cargo-clippy clippy-driver; do
    tool_path="$(toolchain_bin "${tool}")"
    if [[ -n "${tool_path}" && -x "${tool_path}" ]]; then
      ln -sf "${tool_path}" "/usr/local/bin/${tool}"
    fi
  done
fi

log "Rust environment ready"
rustup run "${TOOLCHAIN}" rustc --version
rustup run "${TOOLCHAIN}" cargo --version
bindgen --version
