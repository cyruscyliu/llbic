# LLVM Linux Build Issues Collection

I guess most of you have troubles comipling Linux kernel with LLVM, while the solutions to build issues are all over the internet, in a blog, in commit comments. The project is then aiming to put these solutions together as a `build issues collection` and a learning materail of compiler. BTW, `llbic` is short of LLVM Linux Build Issues Collection.

## features

+ compiler `.S` and `.c` to bytes code and link them toghether, ported from [dr_checker](https://github.com/ucsb-seclab/dr_checker) which is a soundy vulnerablity detection tool for Linux Kernel drivers
+ arch specific and linux-version specific, meaning that the project will tell you the least patches to your requirements
