# Background

This document summarizes common LLVM bitcode generation models and how
**llbic** has evolved.

Important caveat: in the Linux kernel tree, not every file ending in `.bc` is
LLVM bitcode. For example, `kernel/time/timeconst.bc` is an input to the `bc`
calculator (used to generate `include/generated/timeconst.h`), not `LLVM IR
bitcode`.

```
     --emit-llvm   +---+  llc   +--+  ld   +---+
(1) -------------> +.bc+ -----> +.o+ ----> +ELF+ (generic)
                   +---+        +--+       +---+

     --emit-llvm   +---+  llvm-link   +---+
(2) -------------> +.bc+ -----------> +.bc+  (legacy llbic)
                   +---+              +---+

     -flto -c  +---+  -flto   +---+
(3) ---------> +.bc+ -------> +ELF+ (lto) (llbic today)
               +---+          +---+

     clang + IRDumper   +--+      +---+
(4) ------------------> +.o+  +-> +.bc+  (llbic today as a fallback)
                        +--+  |   +---+
                              |
                              +--- normal kernel build artifacts
```

## Legacy: NAIVE llvm-link

Early versions of this repository used a dr_checker-inspired workflow:

- Capture the kernel build commands from `make V=1` into `makeout.txt`.
- Rewrite `gcc` compilation commands into `clang --emit-llvm` commands (dropping
  flags Clang did not understand).
- Parse `ld` commands to reconstruct a link dependency tree up to `vmlinux`, then
  `llvm-link` the leaf modules into a monolithic `vmlinux.bc`.

This was useful as a proof-of-concept, but it was brittle in practice:

- `.S` files are not represented at the LLVM-IR level, so the output was always
  incomplete.
- Symbol resolution differs: `ld` often picks the first definition and keeps
  going, while `llvm-link` requires explicit conflict handling (for example via
  [`-override`](http://lists.llvm.org/pipermail/llvm-commits/Week-of-Mon-20150420/272071.html)).
- The approach effectively reimplements a lot of the kernel build system (and
  breaks across versions/architectures/toolchains).

Reference: dr_checker (https://github.com/ucsb-seclab/dr_checker).

## Relative Models

(1) [WLLVM](https://github.com/travitch/whole-program-llvm) provides
python-based compiler wrappers that work in two steps. The wrappers first
invoke the compiler as normal. Then, for each object file, they call a bitcode
compiler to produce LLVM bitcode. The wrappers also store the location of the
generated bitcode file in a dedicated section of the object file (e.g. via
objcopy). When object files are linked together, the contents of the dedicated
sections are concatenated (so we don't lose the locations of any of the
constituent bitcode files). After the build completes, one can use a WLLVM
utility to read the contents of the dedicated section and link all of the
bitcode into a single whole-program bitcode file (`llvm-link`). This utility
works for both executables and native libraries.

(2) [LTO](https://llvm.org/docs/LinkTimeOptimization.html) is intermodular
optimization performed during the link stage. In this model, the linker treats
LLVM bitcode files like native object files and allows mixing and matching
among them. The linker uses `libLTO` to handle LLVM bitcode files.

The `-flto` flag tells Clang to emit LLVM bitcode for later link-time
optimization instead of lowering each translation unit directly to a final
native object file. In practice there are two main LTO modes:

- Full LTO: the linker merges the whole program into one optimization unit.
  This can produce strong whole-program optimization results, but it is more
  memory-intensive and slower on large builds such as the Linux kernel.
- ThinLTO: the linker keeps per-module summaries and performs scalable
  cross-module optimization without fully merging the entire program into one
  unit. This is usually a better fit for large codebases because it preserves
  more incremental and parallel build behavior.

FYI: [ThinLTO](http://clang.llvm.org/docs/ThinLTO.html) is LLVM's scalable and
incremental LTO model.

## llbic Today

The current `./llbic` script does **not** try to reconstruct a full link tree
or force a monolithic `vmlinux.bc`. Instead, it focuses on producing a
reproducible kernel build and collecting whatever LLVM bitcode the chosen
strategy naturally emits.

1. Kernel-native Clang LTO (preferred when supported)
   - llbic enables a kernel configuration that uses Clang LTO (for example
     `CONFIG_LTO_CLANG_FULL`) and builds with `LLVM=1`.
   - In this mode, the kernel's own Clang/LTO build flow is responsible for
     producing LLVM bitcode as part of the normal compilation and link stages;
     llbic does not inject a separate bitcode-dumping pass.
   - llbic then searches the relevant build root for real LLVM bitcode modules
     (verified by file type, not by filename) and writes a manifest.

2. IRDumper pass plugin (fallback)
   - If native LTO is not viable, llbic loads the `IRDumper` Clang pass plugin.
   - This keeps the normal compilation output (`.o`) but also dumps a `.bc` file
     per compiled translation unit (roughly per `.c` file).
   - This is more stable than the legacy link-tree approach because it does not
     require re-linking the entire kernel in LLVM space.

In both modes, llbic writes logs/metadata under `out/linux-<ver>/`, including:

- `llbic.json`: summary (includes `bitcode_root` plus relative paths)
- `bitcode_files.txt`: list of LLVM bitcode files (relative paths)
