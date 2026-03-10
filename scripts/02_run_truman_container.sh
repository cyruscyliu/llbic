#!/usr/bin/env bash
set -euo pipefail

IMAGE="truman:latest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOST_LLVM_BUILD_DIR="${ROOT_DIR}/build"
CONTAINER_LLVM_BUILD_DIR="/home/debian/build"
HOST_SOURCES_DIR="${ROOT_DIR}/sources"
CONTAINER_SOURCES_DIR="/home/debian/sources"
HOST_MLTA_DIR="${ROOT_DIR}/mlta"
CONTAINER_MLTA_DIR="/home/debian/mlta"
HOST_SCRIPTS_DIR="${ROOT_DIR}/scripts"
CONTAINER_SCRIPTS_DIR="/home/debian/scripts"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed or not in PATH." >&2
  exit 1
fi

if [[ ! -d "${HOST_LLVM_BUILD_DIR}" ]]; then
  echo "Error: host directory does not exist: ${HOST_LLVM_BUILD_DIR}" >&2
  exit 1
fi

if [[ ! -d "${HOST_SOURCES_DIR}" ]]; then
  echo "Error: sources directory does not exist: ${HOST_SOURCES_DIR}" >&2
  exit 1
fi

if [[ ! -d "${HOST_MLTA_DIR}" ]]; then
  echo "Error: mlta directory does not exist: ${HOST_MLTA_DIR}" >&2
  exit 1
fi

if [[ ! -d "${HOST_SCRIPTS_DIR}" ]]; then
  echo "Error: scripts directory does not exist: ${HOST_SCRIPTS_DIR}" >&2
  exit 1
fi

docker run --rm -it \
  -v "${HOST_LLVM_BUILD_DIR}:${CONTAINER_LLVM_BUILD_DIR}" \
  -v "${HOST_SOURCES_DIR}:${CONTAINER_SOURCES_DIR}" \
  -v "${HOST_MLTA_DIR}:${CONTAINER_MLTA_DIR}" \
  -v "${HOST_SCRIPTS_DIR}:${CONTAINER_SCRIPTS_DIR}" \
  "${IMAGE}"
