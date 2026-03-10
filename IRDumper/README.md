# IRDumper

An LLVM pass plugin that dumps each compiled translation unit as LLVM bitcode
(`.bc`) during kernel compilation. The normal compilation and linking process is
not affected — the pass writes `.bc` files as a side effect.

## How It Works

IRDumper is loaded into Clang as a pass plugin. For each module (`.c` file)
compiled, it intercepts the compiled IR and writes it out as a `.bc` file
alongside the regular `.o` object file.

Both the legacy and new LLVM pass managers are supported:
- **Legacy PM** (Clang <= 14): requires `-flegacy-pass-manager`
- **New PM** (Clang >= 15): default, loaded via `-fpass-plugin`

## Build

IRDumper requires an LLVM installation with development headers. Inside the
Docker containers, LLVM is managed via `update-alternatives`, so the system
`llvm-config` is used automatically.

```bash
# Build using system LLVM (selected via update-alternatives)
make dumper

# Build against a specific LLVM installation
make LLVM_BUILD=/path/to/llvm/prefix dumper

# Switch LLVM version before building
sudo update-alternatives --set clang /usr/bin/clang-18
make clean dumper
```

The output is `build/lib/libDumper.so`.

## Usage

```bash
# New PM (Clang >= 15, default)
clang -fpass-plugin=build/lib/libDumper.so -c foo.c -o foo.o

# Legacy PM (Clang <= 14)
clang -flegacy-pass-manager -Xclang -load -Xclang build/lib/libDumper.so -c foo.c -o foo.o
```

This produces both `foo.o` (normal object) and `foo.bc` (LLVM bitcode).

## Origin

IRDumper is adapted from the [mlta](https://github.com/umnsec/mlta) project
(MIT License).
