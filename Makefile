ARCH			?=x86_64
CC 				?=ccache

LLVM_CONFIG		?=llvm-config
LLVM_CLANG		?=$(shell llvm-config --bindir)/clang
LLVM_LINK		?=$(shell llvm-config --bindir)/llvm_link

SOURCE			?=empty-kernel-source
BUILD			?=$(SOURCE)-llvm-bc-out
MAKEOUT			?=$(SOURCE)/makeout.txt

NPROC			?=$(shell nproc)
COMMAND_ONLY    ?=

all:
	@echo "  Please run make compile or make link."

compile:
ifeq ($(COMMAND_ONLY),)
	./llbic.py -ac compile -a $(ARCH) -cop $(CC) -c $(LLVM_CLANG) -s $(SOURCE) -o $(BUILD) -mo $(MAKEOUT)
else
	./llbic.py -ac compile -a $(ARCH) -cop $(CC) -c $(LLVM_CLANG) -s $(SOURCE) -o $(BUILD) -mo $(MAKEOUT)  -co
endif

link:
	./llbic.py -ac link -a $(ARCH) -cop $(CC) -c $(LLVM_CLANG) -s $(SOURCE) -o $(BUILD) -mo $(MAKEOUT)
