# Backgroud

## LLVM pipeline

```
     --emit-llvm   +---+  llc   +--+  ld   +---+
(1) -------------> +.bc+ -----> +.o+ ----> +ELF+ (generic)
                   +---+        +--+       +---+

     -flto -c  +---+  -flto   +---+
(2) ---------> +.bc+ -------> +ELF+ (lto)
               +---+          +---+

     --emit-llvm   +---+  llvm-link   +---+
(3) -------------> +.bc+ -----------> +.bc+  (llbic)
                   +---+              +---+
```

## Similar projects

Our NAIVE algorithm is based on [dr_checker](https://github.com/ucsb-seclab/dr_checker),
which is easy to understand, taking place of gcc with clang and linking generated
bitcode files with llvm-link. We first save all makefile commands by `V=1 >makeout.txt 2>&1`.
To generate bitcode, we replace gcc with `emit-llvm` mode clang and remove unsupported flags.
As a matter of fact, only .c file can emit LLVM-IR such that we can not analysis .S file
in LLVM-IR level. In the phase of linking all bitcode files, it is essential to known which
files to link to avoid of multi-defined symbols. We analyze all gcc-commands and ld-commands
to find the dependency between source files and the final target: vmlinux. The dependency is
of course a [tree](./arch/mips/linux-3.18.20.gv.pdf), and all leafs should be linked together.
As we mentioned before, only .c file can be linked, so we can only get a partial bitcode vmlinux.
In practice, we still found multiple defined symbols when we link all leafs together because
host `ld` just use the first occurrence of the symbol definition by ignoring others while `llvm-link`
must use [`-override`](http://lists.llvm.org/pipermail/llvm-commits/Week-of-Mon-20150420/272071.html)
explicitly. We then link the bitcode files one by one according to their orders in the makefile commands.
**If you only need vmlinux.bc ,then NAIVE is simple and helpful.**

The [WLLVM](https://github.com/travitch/whole-program-llvm) provides python-based compiler
wrappers that work in two steps. The wrappers first invoke the compiler as normal. Then,
for each object file, they call a bitcode compiler to produce LLVM bitcode. The wrappers also
store the location of the generated bitcode file in a dedicated section of the object file(e.g. objcopy).
When object files are linked together, the contents of the dedicated sections are concatenated
(so we don't lose the locations of any of the constituent bitcode files). After the build completes,
one can use a WLLVM utility to read the contents of the dedicated section and link all of the bitcode
into a single whole-program bitcode file(llvm-link). This utility works for both executable and
native libraries. The `NAIVE` algorithm is definitely a subset of the WLLVM w/ the ability to generate
an executable vmlinux. **If you need vmlinux compiled by clang, use wllvm and I guess you have to
solve the problem of unsupported flags.**

The [LTO](https://llvm.org/docs/LinkTimeOptimization.html) is intermodular optimization
when performed during the link stage. In this model, the linker treats LLVM bitcode files
like native object files and allows mixing and matching among them. The linker uses libLTO,
a shared object, to handle LLVM bitcode files. **If you need global optimization and want a vmlinux
executable, try this.** FYI: [ThinLTO](http://clang.llvm.org/docs/ThinLTO.html): Scalable and
Incremental LTO.
