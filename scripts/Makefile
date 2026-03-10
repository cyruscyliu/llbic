SHELL := /usr/bin/env bash

ROOT_DIR := $(abspath $(CURDIR)/..)

# Override these from CLI if needed, for example:
#   make -C scripts linux-defconfig LINUX_PATH=/path/to/linux KCONFIG_FRAGMENTS="a.conf b.conf"
ARCH ?= arm64
LINUX_PATH ?= $(ROOT_DIR)/sources/linux
CROSS_COMPILE_NS_KERNEL ?=
KCONFIG_FRAGMENTS ?= \
	$(CURDIR)/kconfigs/qemu.conf \
	$(CURDIR)/kconfigs/cca.conf

LINUX_DEFCONFIG_COMMON_ARCH := $(ARCH)
LINUX_DEFCONFIG_COMMON_FILES := \
	$(LINUX_PATH)/arch/$(LINUX_DEFCONFIG_COMMON_ARCH)/configs/defconfig \
	$(KCONFIG_FRAGMENTS)

.PHONY: prepare-config linux-defconfig linux-defconfig-clean

prepare-config: linux-defconfig

linux-defconfig: $(LINUX_PATH)/.config

$(LINUX_PATH)/.config: $(LINUX_DEFCONFIG_COMMON_FILES)
	@if [[ ! -x "$(LINUX_PATH)/scripts/kconfig/merge_config.sh" ]]; then \
		echo "Error: missing merge script: $(LINUX_PATH)/scripts/kconfig/merge_config.sh" >&2; \
		exit 1; \
	fi
	cd "$(LINUX_PATH)" && \
		ARCH="$(LINUX_DEFCONFIG_COMMON_ARCH)" \
		CROSS_COMPILE="$(CROSS_COMPILE_NS_KERNEL)" \
		scripts/kconfig/merge_config.sh $(LINUX_DEFCONFIG_COMMON_FILES)

linux-defconfig-clean:
	rm -f "$(LINUX_PATH)/.config"
