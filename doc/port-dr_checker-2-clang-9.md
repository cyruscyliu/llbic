# port dr_checker to clang-9

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
