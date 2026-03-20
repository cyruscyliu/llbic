#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/install_rust_env.sh [--system] [--toolchain TOOLCHAIN]

Installs a Rust toolchain suitable for Linux kernel Rust builds and bindgen use.

Defaults:
  --toolchain stable

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
rustup default "${TOOLCHAIN}"
rustup component add rust-src
rustup component add rustfmt

log "Installing bindgen-cli"
cargo install --locked bindgen-cli --force

if [[ "${SYSTEM_INSTALL}" -eq 1 ]]; then
  for tool in cargo rustc rustup rustdoc cargo-clippy cargo-fmt rustfmt clippy-driver bindgen; do
    if [[ -x "${CARGO_HOME}/bin/${tool}" ]]; then
      ln -sf "${CARGO_HOME}/bin/${tool}" "/usr/local/bin/${tool}"
    fi
  done
fi

log "Rust environment ready"
rustc --version
cargo --version
bindgen --version
