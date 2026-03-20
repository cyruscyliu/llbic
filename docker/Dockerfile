FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LLBIC_RUST_BIN=/usr/local/llbic-rust/bin
ENV CARGO_HOME=/usr/local/cargo
ENV RUSTUP_HOME=/usr/local/rustup
ENV PATH=${LLBIC_RUST_BIN}:/usr/local/cargo/bin:${PATH}

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
      gcc-riscv64-linux-gnu \
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
        --slave /usr/bin/llvm-nm llvm-nm /usr/bin/llvm-nm-${v} \
        --slave /usr/bin/llvm-objcopy llvm-objcopy /usr/bin/llvm-objcopy-${v} \
        --slave /usr/bin/llvm-objdump llvm-objdump /usr/bin/llvm-objdump-${v} \
        --slave /usr/bin/llvm-ranlib llvm-ranlib /usr/bin/llvm-ranlib-${v} \
        --slave /usr/bin/llvm-readelf llvm-readelf /usr/bin/llvm-readelf-${v} \
        --slave /usr/bin/llvm-size llvm-size /usr/bin/llvm-size-${v} \
        --slave /usr/bin/llvm-strings llvm-strings /usr/bin/llvm-strings-${v} \
        --slave /usr/bin/llvm-strip llvm-strip /usr/bin/llvm-strip-${v} \
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

COPY scripts/install_rust_env.sh /tmp/install_rust_env.sh
RUN chmod +x /tmp/install_rust_env.sh \
      && /tmp/install_rust_env.sh --system \
      && rm -f /tmp/install_rust_env.sh

COPY scripts/rustc-llbic-wrapper.sh /usr/local/bin/rustc-llbic-wrapper
COPY scripts/bindgen-llbic-wrapper.sh /usr/local/bin/bindgen-llbic-wrapper
RUN chmod +x /usr/local/bin/rustc-llbic-wrapper \
      /usr/local/bin/bindgen-llbic-wrapper \
      && mkdir -p "${LLBIC_RUST_BIN}" \
      && printf '%s\n' '#!/usr/bin/env bash' \
                     'exec /usr/local/bin/rustc-llbic-wrapper "$@"' \
         > "${LLBIC_RUST_BIN}/rustc" \
      && printf '%s\n' '#!/usr/bin/env bash' \
                     'exec /usr/local/bin/bindgen-llbic-wrapper "$@"' \
         > "${LLBIC_RUST_BIN}/bindgen" \
      && chmod +x "${LLBIC_RUST_BIN}/rustc" "${LLBIC_RUST_BIN}/bindgen" \
      && LLBIC_RUSTC_REAL="$(rustup which rustc)" /usr/local/bin/rustc-llbic-wrapper --version \
      && LLBIC_BINDGEN_REAL="/usr/local/cargo/bin/bindgen" CC=clang /usr/local/bin/bindgen-llbic-wrapper --version

# Install llbic CLI
COPY llbic /usr/local/bin/llbic
RUN chmod +x /usr/local/bin/llbic

RUN apt-get update && apt-get install -y --no-install-recommends sudo file \
      && rm -rf /var/lib/apt/lists/* \
      && useradd -m -s /bin/bash llbic \
      && echo "llbic ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/llbic

LABEL org.opencontainers.image.source="https://github.com/cyruscyliu/llbic"
LABEL org.opencontainers.image.description="Compile Linux kernels to LLVM bitcode (recent: 6.x/7.x)"

USER llbic
WORKDIR /home/llbic
ENTRYPOINT ["llbic"]
