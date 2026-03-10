CUR_DIR = $(shell pwd)
SRC_DIR := ${CUR_DIR}/src
SRC_BUILD := ${CUR_DIR}/build

# Use system LLVM (managed by update-alternatives) by default.
# Override with: make LLVM_BUILD=/path/to/llvm/prefix dumper
LLVM_BUILD ?= $(shell llvm-config --prefix)

# Auto-detect C++ standard: LLVM >= 15 requires C++17, older uses C++14
LLVM_MAJOR := $(shell llvm-config --version | cut -d. -f1)
CXX_STD := $(shell [ "$(LLVM_MAJOR)" -ge 15 ] 2>/dev/null && echo c++17 || echo c++14)

NPROC ?= $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

CMAKE_GENERATOR ?= $(shell command -v ninja >/dev/null 2>&1 && echo Ninja || echo "Unix Makefiles")

build_src_func = \
	(mkdir -p ${2} \
		&& cd ${2} \
		&& PATH=${LLVM_BUILD}/bin:${PATH} \
			CC=clang CXX=clang++ \
			cmake ${1} \
					-G "${CMAKE_GENERATOR}" \
					-DCMAKE_BUILD_TYPE=Release \
					-DCMAKE_CXX_FLAGS_RELEASE="-std=${CXX_STD} -fno-rtti -fPIC -O3" \
					-DLLVM_DIR=${LLVM_BUILD}/lib/cmake/llvm \
			&& cmake --build . -- -j${NPROC})

all: dumper

dumper:
	$(call build_src_func, ${SRC_DIR}, ${SRC_BUILD})

clean:
	rm -rf ${SRC_BUILD}

.PHONY: all dumper clean
