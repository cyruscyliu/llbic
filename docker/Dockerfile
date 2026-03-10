FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      # Basic build tools
      build-essential \
      bc \
      bison \
      flex \
      libssl-dev \
      libelf-dev \
      libncurses-dev \
      # Download tools
      curl \
      wget \
      ca-certificates \
      # LLVM build dependencies
      cmake \
      ninja-build \
      zlib1g-dev \
      libxml2-dev \
      # Python
      python3 \
      python3-pip \
      python3-venv \
      # Kernel build tools
      cpio \
      kmod \
      rsync \
      dwarves \
      debhelper \
      # Cross-compilation toolchains
      crossbuild-essential-armel \
      crossbuild-essential-arm64 \
      gcc-arm-linux-gnueabi \
      gcc-aarch64-linux-gnu \
      gcc-mipsel-linux-gnu \
      # Version control & misc
      git \
      xz-utils \
      lz4 \
      gawk \
      && rm -rf /var/lib/apt/lists/*

# Install Clang/LLVM versions (all from Ubuntu 24.04 default repos)
RUN apt-get update && apt-get install -y --no-install-recommends \
      clang-14 llvm-14 lld-14 llvm-14-dev \
      clang-15 llvm-15 lld-15 llvm-15-dev \
      clang-16 llvm-16 lld-16 llvm-16-dev \
      clang-18 llvm-18 lld-18 llvm-18-dev \
      && rm -rf /var/lib/apt/lists/*

# Register Clang/LLVM alternatives
RUN for v in 14 15 16 18; do \
      update-alternatives --install /usr/bin/clang clang /usr/bin/clang-${v} ${v}0 \
        --slave /usr/bin/clang++ clang++ /usr/bin/clang++-${v} \
        --slave /usr/bin/llvm-config llvm-config /usr/bin/llvm-config-${v} \
        --slave /usr/bin/llvm-link llvm-link /usr/bin/llvm-link-${v} \
        --slave /usr/bin/llvm-ar llvm-ar /usr/bin/llvm-ar-${v} \
        --slave /usr/bin/llvm-dis llvm-dis /usr/bin/llvm-dis-${v} \
        --slave /usr/bin/lld lld /usr/bin/lld-${v} \
        --slave /usr/bin/ld.lld ld.lld /usr/bin/ld.lld-${v}; \
    done

# Build IRDumper for each LLVM version
COPY IRDumper /tmp/IRDumper
RUN for v in 14 15 16 18; do \
      update-alternatives --set clang /usr/bin/clang-${v} \
      && make -C /tmp/IRDumper clean dumper \
      && mkdir -p /opt/IRDumper/${v} \
      && cp /tmp/IRDumper/build/lib/libDumper.so /opt/IRDumper/${v}/ ; \
    done \
    && rm -rf /tmp/IRDumper

RUN python3 -m pip install --break-system-packages \
      networkx \
      graphviz

RUN apt-get update && apt-get install -y --no-install-recommends sudo \
      && rm -rf /var/lib/apt/lists/* \
      && useradd -m -s /bin/bash llbic \
      && echo "llbic ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/llbic

USER llbic
WORKDIR /home/llbic
