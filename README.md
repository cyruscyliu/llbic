# LLVM Linux Build Issues Collection

I guess most of you have troubles compiling Linux kernel with LLVM, while the solutions to build issues are all over the internet, in a blog, in commit comments, etc. The project is then aiming to put these solutions together as a `build issues collection` and a learning material of LLVM compiler. BTW, `llbic` is short of LLVM Linux Build Issues Collection.

## features

+ compiler `.S` and `.c` to bytecode and link them toghether, ported from [dr_checker](https://github.com/ucsb-seclab/dr_checker) which is a soundy vulnerablity detection tool for Linux Kernel drivers
+ arch specific and linux-version specific, meaning that the project will tell you the least patches to your requirements
