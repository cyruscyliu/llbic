# LLVM Linux Build Issues Collection

In general, this project will compile and link old Linux kernels in llvm bitcode.

>I guess most of you have troubles compiling old Linux kernels with clang,
while the solutions are all over the internet, in blogs,
in commit comments, etc. The project is then aiming to put these solutions
together as a `build issues collection` and a learning material of clang usage.
BTW, `llbic` is short of LLVM Linux Build Issues Collection.

Note that assembly files(.S) cannot be compiled to bitcode files; 
we use `llvm-link` that cannot generate executables but a bigger llvm bitcode file.

## Background

    NAIVE: .c--->object.bc--->vmlinux.bc
        
Our NAIVE algorithm is based on [dr_checker](https://github.com/ucsb-seclab/dr_checker).
We first save all makefile commands by `V=1 >makeout.txt 2>&1`. 
To generate bitcode, we replace gcc with `emit-llvm` mode clang and remove unsupported flags.
When linked, we analyze all gcc-commands and ld-commands to find the scope and order to avoid multi-defined symbols.
Then, we get a single whole-program bitcode file directly.

    WLLVM: .c--->object.o+object.bc--->vmlinux.elf+vmlinux.bc

The [WLLVM](https://github.com/travitch/whole-program-llvm) provides python-based compiler wrappers that work in two steps.
The wrappers first invoke the compiler as normal. 
Then, for each object file, they call a bitcode compiler to produce LLVM bitcode.
The wrappers also store the location of the generated bitcode file in a dedicated section of the object file(e.g. objcopy).
When object files are linked together, the contents of the dedicated sections are concatenated (so we don't lose the locations of any of the constituent bitcode files).
After the build completes, one can use a WLLVM utility to read the contents of the dedicated section
and link all of the bitcode into a single whole-program bitcode file (llvm-link).
This utility works for both executable and native libraries. 

    LTO: .c--->object.bc---->vmlinux.elf(vmlinux.bc in memory)

The [LTO](https://llvm.org/docs/LinkTimeOptimization.html) is intermodular optimization when performed during the link stage.
In this model, the linker treats LLVM bitcode files like native object files and allows mixing and matching among them.
The linker uses libLTO, a shared object, to handle LLVM bitcode files. Then you can retieve the whole-program bitcode file from memeory.
FYI: [ThinLTO](http://clang.llvm.org/docs/ThinLTO.html): Scalable and Incremental LTO.


## Support List
|build issues collection|arch|linux version|clang version|object.bc|vmlinux.bc|
|:---:|:---:|:---:|:---:|:---:|:---:|
|[mips-linux-4.14.167](./arch/mips/linux-4.14.167.md)|mips|4.14.167|9|Y|Y|
|[mips-linux-4.4.42](./arch/mips/linux-4.4.42.md)|mips|4.4.42|9|Y|Y|
|[mips-linux-3.18.20](./arch/mips/linux-3.18.20.md)|mips|3.18.20|6/9|Y|Y|
|[arm-linux-3.18.20](./arch/arm/linux-3.18.20.md)|arm|3.18.20|9|Y|Y|
|[arm-linux-2.6.32](./arch/arm/linux-2.6.32.md)|arm|2.6.32|9|Y|Y|

Note:
+ object.bc: Compile each c file to llvm bitcode file.
+ vmlinux.bc: Link necessary object.bc files together to a vmlinux.bc.

## Quick Start

*Before using llbic, you should have already built the kernel source code successfully using gcc.*
*If you target openwrt firmware, you had better follow the [openwrt-build-docker](https://github.com/cyruscyliu/openwrt-build-docker) to build the target kernel source code.*

I recommend you using Docker such that all commands in this project can be ran directly.

```shell script
git clone git@github.com:cyruscyliu/llbic.git && cd llbic
docker build -f Dockerfile_llvm6 -t llbic:llvm6 .
docker build -f Dockerfile_llvm9 -t llbic:llvm9 .
docker run -it \
        -v ${PATH_OF_LLBIC_REPO}:/mnt/llbic \
        -v ${PATH_OF_BUILT_KERNEL_SOURCE}:/mnt/build \
        # see the following comment for this volume config if you use openwrt-build-docker
        -v ${PATH_OPENWRT_BUILDER_USED_OUTSIDE}:${PATH_OPENWRT_BUILDER_USED_INSIDE} \
        llbic:XXX /bin/bash
```

Comment:
- `-v path/to/openwrt-build-docker/share:/root/firmware`
- see the volume section of the [yaml](https://github.com/cyruscyliu/openwrt-build-docker/blob/master/10.03/docker-compose.yml) as the example
- llbic:XXX could be llbic:llvm6 or llbic:llvm9

Take [mips-linux-3.18.20](./arch/mips/linux-3.18.20.md) as an example.

```shell script
export BUILD=/home/root/build

# get a buildable kernel
# 1. build the kerne
# 2. get the name of the compiler from the generated 'makeout.txt' in the step 1, e.g. 'arm-openwrt-linux-uclibcgnueabi-gcc'

# patch this kernel source code
cp /home/root/llbic/arch/mips/linux-3.18.20.sh . && ./linux-3.18.20.sh

cd /home/root/llbic
# dependency graph (if needed)
python helper/dependency.py $BUILD/linux-3.18.20/makeout.txt

# object.bc
cd /home/root/llbic
# half compile (generate command only)
python wrapper.py dr_checker compile command-only \
    $BUILD/linux-3.18.20/makeout.txt mips /usr/bin/clang \
    $STAGING_DIR/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-gcc \
    $BUILD/linux-3.18.20/ $BUILD/linux-3.18.20-llvm-bitcode
# full compile
python wrapper.py dr_checker compile \
    $BUILD/linux-3.18.20/makeout.txt mips /usr/bin/clang \
    $STAGING_DIR/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-gcc \
    $BUILD/linux-3.18.20/ $BUILD/linux-3.18.20-llvm-bitcode
# vmlinux.bc
python wrapper.py dr_checker link \
    $BUILD/linux-3.18.20/makeout.txt \
    /usr/bin/llvm-link $BUILD/linux-3.18.20-llvm-bitcode
```

Note:
+ For arm-linux.2.6.32, please run `sed -i -r "s/defined\(@val\)/@val/" kernel/timeconst.pl` first.

## Others
+ The initial idea was inspired by [dr_checker](https://github.com/ucsb-seclab/dr_checker).
+ [port dr_checker to clang9](./doc/port-dr_checker-2-clang-9.md)
