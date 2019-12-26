# LLVM Linux Build Issues Collection

I guess most of you have troubles compiling Linux kernel with LLVM, while the solutions to build issues are all over
the internet, in a blog, in commit comments, etc. The project is then aiming to put these solutions together as a 
`build issues collection` and a learning material of LLVM compiler. BTW, `llbic` is short of LLVM Linux Build Issues
 Collection.
 
 Generally, compiling Linux kernel with LLVM consists of several tasks listed below.
 + For mainline Linux kernel, compile and assembly all source code targeting to a specific architecture to LLVM byte 
 code, and then, link them together. I denote this task as `ML-vmlinux.bc`. This task does consist of `C-ML-vmliux.bc`
 and `L-ML-vmlinux.bc`, which is easily to be concluded, according to the state of the art techniques.
 + For mainline Linux kernel, build the whole source code targeting to a specific architecture to an executable with 
 Clang. I denote this task as `ML-vmlinux.elf`. And subtasks `C-ML-vmlinux.elf` and `L-ML-vmlinux.elf` as well.
 + For other Linux-based platform, say Android, we can easily define 2 tasks, `Android-vmlinux.bc` and
 `Android-vmlinux.elf`. We will not list their subtasks for sake of simplicity.


## Support List
|build issues collection|arch|linux version|clang version|c-ml-vmlinux.bc|l-vm-vmlinux.bc|
|:---:|:---:|:---:|:---:|:---:|:---:|
|[mips-linux-3.18.20](./arch/mips/linux-3.18.20.md)|mips|3.18.20|9|Y|Partial|
|[arm-linux-3.18.20](./arch/arm/linux-3.18.20.md)|arm|3.18.20|9|Y|Partial|
|[arm-linux-2.6.32](./arch/arm/linux-2.6.32.md)|arm|2.6.32|9|Y|Partial|

## Quick Start

*Before using llbic, you should have aleady built the kernel source code successfully using gcc.*
*If you target openwrt firmware, you had better follow the [openwrt-build-docker](https://github.com/cyruscyliu/openwrt-build-docker) to build the target kernel source code.*

I recommend you using Docker such that all commands in this project can be ran directly.

```shell script
git clone git@github.com:cyruscyliu/llbic.git && cd llbic
docker build -t llbic:latest .
docker run -it \
        -v ${PATH_OF_LLBIC_REPO}:/mnt/llbic \
        -v ${PATH_OF_BUILT_KERNEL_SOURCE}:/mnt/build \
        # see the following comment for this volume config if you use openwrt-build-docker
        -v ${PATH_OPENWRT_BUILDER_USED_OUTSIDE}:${PATH_OPENWRT_BUILDER_USED_INSIDE} \
        llbic:latest /bin/bash
```


Comment:
- `-v path/to/openwrt-build-docker/share:/root/firmware`
- see the volume section of the [yaml](https://github.com/cyruscyliu/openwrt-build-docker/blob/master/10.03/docker-compose.yml) as the example

Take [mips-linux-3.18.20](./arch/mips/linux-3.18.20.md) as an example.

```shell script
export BUILD=/home/root/build

# get a buildable kernel 
# 1. build the kernel using the repo
# 2. get the name of the compiler from the generated 'makeout.txt' in the step 1, e.g. 'arm-openwrt-linux-uclibcgnueabi-gcc'

# patch this kernel source code
cp /home/root/llbic/arch/mips/linux-3.18.20.sh . && ./linux-3.18.20.sh

cd /home/root/llbic
# dependency graph (if needed)
python helper/dependency.py $BUILD/linux-3.18.20/makeout.txt

# ml-vmlinux.bc
cd /home/root/llbic
# part compile (generate command only)
# c-ml-vmlinux.bc by NAIVE
python wrapper.py dr_checker compile command-only $BUILD/linux-3.18.20/makeout.txt mips /usr/bin/clang $STAGING_DIR/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-gcc $BUILD/linux-3.18.20/ $BUILD/linux-3.18.20-llvm-bitcode
# full compile
# c-ml-vmlinux.bc by NAIVE
python wrapper.py dr_checker compile $BUILD/linux-3.18.20/makeout.txt mips /usr/bin/clang $STAGING_DIR/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-gcc $BUILD/linux-3.18.20/ $BUILD/linux-3.18.20-llvm-bitcode
# full link
# l-ml-vmlinux.bc by NAIVE
python wrapper.py dr_checker link $BUILD/linux-3.18.20/makeout.txt /usr/bin/llvm-link $BUILD/linux-3.18.20-llvm-bitcode
```

>NOTE: For arm-linux.2.6.32, please run `sed -i -r "s/defined\(@val\)/@val/" kernel/timeconst.pl` first.

## Others
+ The initial idea was inspired by [dr_checker](https://github.com/ucsb-seclab/dr_checker).
+ [port dr_checker to clang](./doc/port-dr_checker-2-clang.md)

## Algorithm

|description|NAIVE|WLLVM|
|:---:|:---:|:---:|
|.S/.c ---clang---> .o(elf)|N|Y|
|.c ---clang---> .bc|Y|Y|
|.o ---ld---> vmlinux|N|Y|
|.bc ---llvm-link---> vmlinux.bc|Y|Y

The NAIVE algorithm is based on [dr_checker](https://github.com/ucsb-seclab/dr_checker), which is easy to understand, 
taking place of gcc with clang and linking generated bitcode files with llvm-link. We first save all makefile commands 
by `V=1 >makeout.txt 2>&1`. To generate bitcode, we replace gcc with `emit-llvm` mode clang and remove unsupported flags.
As a matter of fact, only .c file can emit LLVM-IR such that we can not analysis .S file in LLVM-IR level.
In the phase of linking all bitcode files, it is essential to known which files to link to avoid of multi-defined symbols. We
analyze all gcc-commands and ld-commands to find the dependency between source files and the final target: vmlinux.
The dependency is of course a [tree](./arch/mips/linux-3.18.20.gv.pdf), and all leafs should be linked together. As we 
mentioned before, only .c file can be linked, so we can only get a partial bitcode vmlinux. In practice, we still found multiple
defined symbols when we link all leafs together because host `ld` just use the first occurrence of the symbol definition
by ignoring others while `llvm-link` must use [`-override`](http://lists.llvm.org/pipermail/llvm-commits/Week-of-Mon-20150420/272071.html) 
explicitly . We then link the bitcode files one by one according to their orders in the makefile commands.
**If you only need vmlinux.bc ,then NAIVE is simple and helpful.**

The [WLLVM](https://github.com/travitch/whole-program-llvm) provides python-based compiler wrappers that work in two 
steps. The wrappers first invoke the compiler as normal. Then, for each object file, they call a bitcode compiler to 
produce LLVM bitcode. The wrappers also store the location of the generated bitcode file in a dedicated section of the 
object file(e.g. objcopy). When object files are linked together, the contents of the dedicated sections are 
concatenated (so we don't lose the locations of any of the constituent bitcode files). After the build completes, 
one can use a WLLVM utility to read the contents of the dedicated section and link all of the bitcode into a single 
whole-program bitcode file(llvm-link). This utility works for both executable and native libraries. The `NAIVE` 
algorithm is definitely a subset of the WLLVM w/ the ability to generate an executable vmlinux. **If you need vmlinux 
compiled by clang, use wllvm and I guess you have to solve the problem of unsupported flags.**

## Future Work
+ Port WLLVM to old Linux kernel.
+ Introduce gcc LTO framework and GoldLinker.
