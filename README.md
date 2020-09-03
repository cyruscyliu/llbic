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

git clone https://github.com/cyruscyliu/llbic.git ~/llbic

# compile your own kernel first to generate `makeout.txt`
export SOURCE=~/linux-3.18.20
cd $SOURCE && make defconfig && make V=1 >makeout.txt 2>&1

# patch your kernel 
cp patches/3.18.20/linux-3.18.20.sh $SOURCE 
cd $SOURCE && ./linux-3.18.20.sh

# run llbic
cd ~/llbic && make compile && make link && make dependency
```

## Trouble shooting

+ We now support x86_64, arm and mips. Please export ARCH if necessary.
+ We highly reply on the `makeout.txt`. Please check the compiler name in it.
It can be `gcc`, `ccache`, `arm-openwrt-linux-uclibcgnueabi-gcc`. Please export CC if necesary.
+ And sometimes, files are not found in the host, please manipulate the path below carefully.
```
docker run -it \
        -v ${PATH_OF_LLBIC_REPO}:/mnt/llbic \
        -v ${PATH_OF_BUILT_KERNEL_SOURCE}:/mnt/build \
        # see the following comment for this volume config if you use openwrt-build-docker
        -v ${PATH_OPENWRT_BUILDER_USED_OUTSIDE}:${PATH_OPENWRT_BUILDER_USED_INSIDE} \
        -v path/to/openwrt-build-docker/share:/root/firmware \
        llbic:XXX /bin/bash
```
+ For linux-2.6.32, please run `sed -i -r "s/defined\(@val\)/@val/" kernel/timeconst.pl` first.
+ 

## Support List
+ linux-2.6.32 [patch](./patches/2.6.32/linux-2.6.32.sh) [documention](./patches/2.6.32/linux-2.6.32.md)
+ linux-3.18.20][patch](./patches/3.18.20/linux-3.18.20.sh) [documention](./patches/3.18.20/linux-3.18.20.md)
+ linux-4.4.42][patch](./patches/4.4.42/linux-4.4.42.sh) [documention](./patches/4.4.42/linux-4.4.42.md)
+ linux-4.14.167][patch](./patches/4.14.167/linux-4.14.167.sh) [documention](./patches/4.14.167/linux-4.14.167.md)

## Others
+ The initial idea was inspired by [dr_checker](https://github.com/ucsb-seclab/dr_checker).
+ [port dr_checker to clang9](./doc/port-dr_checker-2-clang-9.md)
+ Check the [backgroud](./doc/backgroud.md) for WLLVM and LTO.
