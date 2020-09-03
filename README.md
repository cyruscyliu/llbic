# LLVM Linux Build Issues Collection

I guess most of you have troubles compiling old Linux kernels with clang,
while the solutions to issues are all over the internet, in a blog,
in commit comments, etc. The project is then aiming to put these solutions
together as a `build issues collection` and a learning material of clang usage.
BTW, `llbic` is short of LLVM Linux Build Issues Collection.

In general, this project will compile and link old Linux kernels in llvm bitcode.


```
+--+   gcc    +-----------+   llbic   +---+  
+.c+  ----->  +makeout.txt+  -------> +.bc+  
+--+          +-----------+           +---+  
```

# Usage

```
sudo apt-get install -y clang-3.8 clang-6.0 clang-9.0
sudo ln -s /usr/bin/llvm-config-6.0 /usr/bin/llvm-config

sudo apt-get install -y python3 python3-pip && python3 -m pip install --upgrade pip
sudo -H pip3 install networkx matplotlib graphviz
sudo ln -s /usr/bin/python3 /usr/bin/python

git clone https://github.com/cyruscyliu/llbic.git
```

## Support List
|build issues collection|arch|linux version|clang version|object.bc|vmlinux.bc|
|:---:|:---:|:---:|:---:|:---:|:---:|
|[mips-linux-4.14.167](./arch/mips/linux-4.14.167.md)|mips|4.14.167|9|Y|Y|
|[mips-linux-4.4.42](./arch/mips/linux-4.4.42.md)|mips|4.4.42|9|Y|Y|
|[mips-linux-3.18.20](./arch/mips/linux-3.18.20.md)|mips|3.18.20|6/9|Y|Y|
|[arm-linux-3.18.20](./arch/arm/linux-3.18.20.md)|arm|3.18.20|9|Y|Y|
|[arm-linux-2.6.32](./arch/arm/linux-2.6.32.md)|arm|2.6.32|9|Y|Y|


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
+ Check the [backgroud](./doc/backgroud.md) for WLLVM and LTO.
