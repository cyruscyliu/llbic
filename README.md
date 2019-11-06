# LLVM Linux Build Issues Collection

I guess most of you have troubles compiling Linux kernel with LLVM, while the solutions to build issues are all over
the internet, in a blog, in commit comments, etc. The project is then aiming to put these solutions together as a 
`build issues collection` and a learning material of LLVM compiler. BTW, `llbic` is short of LLVM Linux Build Issues
 Collection.

## Features

+ arch specific and linux-version specific, meaning that the project will tell you the least patches to your requirements
+ *compile `.S` and `.c` to bytecode and link them together (still bytecdoe), ported from 
[dr_checker](https://github.com/ucsb-seclab/dr_checker) which is a soundy vulnerablity detection tool for Linux Kernel drivers
+ *run basic passes on the bytecode generated in last step

>Two *features actually serve as a simple static analyzer of linux kernel source code.


## Support List
|build issues collection|arch|linux version|clang version|compile to bc|link all bc|
|:---:|:---:|:---:|:---:|:---:|:---:|
|[mips-linux-3.18.20](./arch/mips/linux-3.18.20.md)|mips|3.18.20|9|Y|Y|
|[arm-linux-3.18.20](./arch/arm/linux-3.18.20.md)|arm|3.18.20|9|Y|N|
|[arm-linux-2.6.32](./arch/arm/linux-2.6.32.md)|arm|2.6.32|9|Y|N|

## Quick Start

Prepare a buildable kernel.

```shell script
make ARCH=arm CROSS_COMPILE=path/to/cross_compiler_prefix V=1 >makeout.txt 2>&1
```

Run llvm compile.

```python
import os
from helper.compile import LLVMCompile

def test(self):
    kwargs = {
        'makeout': 'path/to/makeout.txt',
        'clangbin': '/usr/bin/clang-9',
        'llvm_bc_out': 'path/to/kernel_src_dir' + '-llvm-bitcode',
        'compiler_name': 'path/to/cross_compiler_gcc',
        'arch': 'mips',
        'kernel_src_dir': 'path/tokernel_src_dir',
    }
    llvm_compile = LLVMCompile(**kwargs)
    status = llvm_compile.setup()
    if status is not None:
        print(status)
        return
    llvm_compile.perform()
```

```text
# output would be
[+] Running LLVM Commands in multiprocessing mode.
[+] Finished Building LLVM Bitcode files
[+] Script containing all LLVM Build Commands:path/to/llvm_bc_out/llvm_build.sh
```

Run llvm link.

```python
from helper.link import LLVMLink

def test(self):
    kwargs = {
        'llvm_bc_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode',
    }
    llvm_link = LLVMLink(**kwargs)
    status = llvm_link.setup()
    if status is not None:
        print(status)
        return
    llvm_link.perform()
```

```text
# output would be
[+] To check BC file: path/to/llvm_bc_out/vmlinux.llvm.bc
```

## Others

### port dr_checker to clang-9

I don't bring all the code in `dr_checker` to this repo, but I still tested all the code in `dr_checker` with `clang-9`.
Besides changes you can see in this repo, I will list some others you might be interested in.

##### dr_linker

The return value of `parseBitcodeFile` has changed.

```cplusplus
// #include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/Bitcode/BitcodeReader.h"

// ErrorOr<std::unique_ptr<llvm::Module>> moduleOrErr = parseBitcodeFile(fileOrErr.get()->getMemBufferRef(), context);
// std::cout << "[*] " << " Processed " << "(" << (i+1) << " of " << all_interesting_files.size() << "): "
//           << curr_bc_file << "\n";
// if (std::error_code ec = moduleOrErr.getError()) {
//     std::cerr << "[-] Error reading Module: " + ec.message() << std::endl;
//     return 3;
// }
Expected<std::unique_ptr<llvm::Module>> moduleOrErr = parseBitcodeFile(fileOrErr.get()->getMemBufferRef(), context);
std::cout << "[*] " << " Processed " << "(" << (i+1) << " of " << all_interesting_files.size() << "): "
          << curr_bc_file << "\n";
if (llvm::Error ec = moduleOrErr.takeError()) {
    std::string message;
    handleAllErrors(std::move(ec), [&](ErrorInfoBase &EIB) {
        message = EIB.message();
    });
    std::cerr << "[-] Error reading Module: " + message << std::endl;
    return 3;
}
```

##### entry_point_identifier

The return value of `parseBitcodeFile` has changed (similar patches as above).

`BUG` Find a shorter invalid struct name.

```cplusplus
for(auto curre:allentries) {
    // if(curre.find(curr_st_name) != std::string::npos) {
    if(curr_st_name.length() >= curre.length() && curre.find(curr_st_name) != std::string::npos) {
        strcpy(hello_str, curre.c_str());
```
