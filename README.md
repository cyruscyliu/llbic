# LLVM Linux Build Issues Collection

I guess most of you have troubles compiling Linux kernel with LLVM, while the solutions to build issues are all over
the internet, in a blog, in commit comments, etc. The project is then aiming to put these solutions together as a 
`build issues collection` and a learning material of LLVM compiler. BTW, `llbic` is short of LLVM Linux Build Issues
 Collection.

## Features

+ compile `.S` and `.c` to bytecode and link them together (still bytecdoe), ported from [dr_checker](https://github.com/ucsb-seclab/dr_checker) which is a soundy vulnerablity detection tool for Linux Kernel drivers
+ arch specific and linux-version specific, meaning that the project will tell you the least patches to your requirements

## Support List
|arch|linux version|clang version|compile to bc|link all bc|
|:---:|:---:|:---:|:---:|:---:|
|mips|3.18.20|9|Y|Y|

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


