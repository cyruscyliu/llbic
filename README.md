# LLBIC: LLVM Linux Build Issues Collection

Performing static analysis with clang on Linux kernel source code requires LLVM
bitcode. While the latest Linux kernel supports clang, we still have troubles
compiling old Linux kernels. Ad-hoc solutions are all over the internet, in a
blog, in commit comments, etc. This project is then aiming to put these
solutions together as a `build issues collection`.

Furthermore, this project can help compile old Linux kernels in LLVM bitcode.
It replaces GCC to clang and adjusts other flags in the make command lines to
generate bitcode files, and then links them all together to a `vmlinux.bc`. The
initial idea was inspired by
[dr_checker](https://github.com/ucsb-seclab/dr_checker) ([port dr_checker to
clang9](./doc/port-dr_checker-2-clang-9.md)). Other approaches that support the
latest Linux kernel are [WLLVM and LTO](./doc/backgroud.md), which is not
included in this project.

```
+--+   gcc    +-----------+   llbic   +---+
+.c+  ----->  +makeout.txt+  -------> +.bc+
+--+          +-----------+           +---+
```

# Usage

## Create docker and Run

```
sudo docker build . -t llbic:latest
sudo docker-compose up -d
sudo docker-compose run --rm llbic /bin/bash
sudo docker-compose down
```

## Compile, Patch, ReCompile, and Link

To apply LLBIC, you have to download the Linux kernel source code and
(cross-)compilers, and manage to build the Linux kernel to get a `makeout.txt`.

```
bash -x download-kernel.sh
apt-get install -y crossbuild-essential-armel
cd linux-x.x.x
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- orion5x_defconfig
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- V=1 > makeout.txt
```

Examples are in the following.

```
./llbic.py -a arm -s linux-4.4.42 -mo linux-4.4.42/makeout.txt -o linux-4.4.42-llvm-bitcode patch
./llbic.py -a arm -s linux-4.4.42 -mo linux-4.4.42/makeout.txt -o linux-4.4.42-llvm-bitcode compile
./llbic.py -a arm -s linux-4.4.42 -mo linux-4.4.42/makeout.txt -o linux-4.4.42-llvm-bitcode link

./llbic.py -a arm -s linux-4.14.167 -mo linux-4.14.167/makeout.txt -o linux-4.14.167-llvm-bitcode patch
./llbic.py -a arm -s linux-4.14.167 -mo linux-4.14.167/makeout.txt -o linux-4.14.167-llvm-bitcode compile
./llbic.py -a arm -s linux-4.14.167 -mo linux-4.14.167/makeout.txt -o linux-4.14.167-llvm-bitcode link
```

## Support List

Because LLBIC is part of [FirmGuide](https://github.com/cyruscyliu/firmguide),
we now support ARM and MIPS Linux 2.6.32
[patch](./patches/2.6.32/linux-2.6.32.sh), 3.18.20
[patch](./patches/3.18.20/linux-3.18.20.sh), 4.4.42
[patch](./patches/4.4.42/linux-4.4.42.sh), 4.14.167
[patch](./patches/4.14.167/linux-4.14.167.sh). A next plan is on demand if there
is any requirement from both academia and industry.

## Contact

If you have any problems, please fire issues!
