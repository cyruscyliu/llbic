# LLVM Linux Build Issues Collection

I guess most of you have troubles compiling Linux kernel with LLVM, while the solutions to build issues are all over
the internet, in a blog, in commit comments, etc. The project is then aiming to put these solutions together as a 
`build issues collection` and a learning material of LLVM compiler. BTW, `llbic` is short of LLVM Linux Build Issues
 Collection.
 
 Generally, compiling Linux kernel with LLVM consists several tasks listed below.
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
|[mips-linux-3.18.20](./arch/mips/linux-3.18.20.md)|mips|3.18.20|9|Y|N|
|[arm-linux-3.18.20](./arch/arm/linux-3.18.20.md)|arm|3.18.20|9|Y|N|
|[arm-linux-2.6.32](./arch/arm/linux-2.6.32.md)|arm|2.6.32|9|Y|N|

## Quick Start

Prepare a buildable kernel.

```shell script
make ARCH=mips CROSS_COMPILE=path/to/cross_compiler_prefix V=1 >makeout.txt 2>&1
python wrapper.py dr_checker compile \
  path/to/linux-source-code/makeout.txt \
  mips \
  /usr/bin/clang cross_compiler_prefix-gcc \
  path/to/linux-source-code path/to/linux-source-code-llvm-bitcode
```
## Others

+ [port dr_checker to clang-9](./doc/port-dr_checker-2-clang-9.md)
