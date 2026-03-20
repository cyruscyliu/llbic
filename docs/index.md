---
title: llbic
---

# llbic

`llbic` is a Linux kernel build tool for researchers, tool builders, and agent
workflows that need reproducible LLVM bitcode and kernel build artifacts.

This page explains where `llbic` comes from, what gap it is trying to close,
and why its design is deliberately more pragmatic than "build one giant kernel
bitcode blob somehow."

## Quick Start

Build a kernel and emit a machine-readable manifest:

```bash
./llbic build 6.18.16 --out-of-tree --json
```

For the full quick start, command model, and usage reference, see the
[repository README](../README.md).

## Introduction

Modern systems research is often a human-in-the-loop agent task. The human sets
goals, checks results, changes direction, and decides what matters; the agent
handles repetitive exploration, build orchestration, artifact collection, and
structured inspection.

That style of work needs infrastructure that is reproducible enough for humans
to trust and structured enough for agents to keep making progress. `llbic` sits
in that gap for Linux kernel builds: one stable entry point, one stable output
contract, and artifacts that can be inspected by both people and tools.

## Background

The background problem here is narrower than "build kernels." It is "emit
LLVM IR from kernel builds in a way that is reproducible and reusable."

That is harder than it sounds.

Linux kernels are versioned, configuration-heavy, architecture-sensitive, and
toolchain-sensitive. If you want LLVM IR, the hard part is not merely invoking
Clang. The hard part is deciding what artifact should count as "the LLVM IR for
the kernel" and then producing it consistently across different build contexts.

Historically, people solve this with a mix of:

- shell scripts that only work for one kernel era
- one-off build wrappers
- handwritten command rewriting
- locally meaningful output layouts

That is enough for one experiment. It is not enough for a reusable workflow.

## Design

`llbic` exists to close that gap.

Its role is not to be a new kernel build system. Its role is to provide a
stable command surface and a stable artifact contract around the kernel build
you are already trying to run.

In concrete terms, `llbic` gives you:

- one stable entry point for building a kernel
- explicit output artifacts under `out/`
- a machine-readable manifest in `llbic.json`
- a clean inspection step for already completed builds
- a path for status collection and regression tracking

That is what makes it useful in a human-in-the-loop agent setting. The human
can review the build record; the agent can keep operating on structured output.

## Design Summary

The high-level design is simple:

1. run a real kernel build, not a synthetic imitation of one
2. preserve a stable artifact layout
3. collect LLVM artifacts that the chosen strategy naturally produces
4. record everything in a manifest that is easy for agents and scripts to read

The key design choice is what `llbic` does **not** do. It does not try to force
every kernel build into one monolithic `vmlinux.bc` pipeline if the underlying
build does not naturally support that.

That restraint is the whole point.

## Implementation

One caveat first: in the Linux kernel tree, not every file ending in `.bc` is
LLVM bitcode. A canonical counterexample is `kernel/time/timeconst.bc`, which
is an input for the `bc` calculator used to generate
`include/generated/timeconst.h`, not LLVM IR bitcode.

There are a few common ways to think about LLVM bitcode generation in native
build systems:

```text
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

The rest of the implementation story is really about why `llbic` moved away
from model (2) and settled on models (3) and (4).

### The Original Bet: Rebuild the Link Tree in LLVM

Early `llbic` used a workflow inspired by
[dr_checker](https://github.com/ucsb-seclab/dr_checker):

- capture kernel build commands from `make V=1`
- rewrite `gcc` compile commands into `clang --emit-llvm` commands
- parse `ld` commands to reconstruct the dependency tree up to `vmlinux`
- run `llvm-link` over the leaves to produce a monolithic `vmlinux.bc`

As a proof of concept, this was useful. It demonstrated that you could extract
enough structure from the kernel build to assemble a large LLVM artifact. It
also produced a dependency graph that was interesting in its own right.

But the approach was fragile.

Three problems kept recurring:

- Assembly was always a gap. Files such as `.S` do not have a clean LLVM-IR
  representation in this workflow, so the result was incomplete from the start.
- Native linker behavior does not map cleanly to `llvm-link`. The ELF linker
  often tolerates conflicts or resolves them with rules that are not mirrored by
  LLVM's link step.
- The pipeline quietly turned into a second kernel build system. Once you start
  rewriting compile commands, reconstructing link structure, and compensating
  for version-specific behavior, you are no longer "using the kernel build";
  you are reimplementing it.

That was the turning point. The most ambitious artifact was also the least
trustworthy one.

### Two Models That Helped Clarify the Design

The redesign was not done in a vacuum. Two existing models are especially
useful reference points.

### WLLVM

[WLLVM](https://github.com/travitch/whole-program-llvm) uses compiler wrappers.
The wrapped compiler still produces normal object files, but it also emits LLVM
bitcode and stores the location of that bitcode in a special section of the
object. After the build completes, a separate utility walks those records and
reconstructs a whole-program bitcode view.

That model is appealing because it stays closer to the native build. The normal
artifacts still exist, and the bitcode trail is preserved alongside them rather
than reconstructed after the fact.

### LTO

[LTO](https://llvm.org/docs/LinkTimeOptimization.html) treats LLVM bitcode as a
first-class input to the link step. In this model, the linker and `libLTO`
coordinate optimization across modules as part of the normal native build.

The key flag is `-flto`. Conceptually, it tells Clang to preserve LLVM IR for
link-time optimization instead of lowering each translation unit directly into a
final native object file.

There are two main flavors:

- Full LTO merges the whole program into a single optimization unit. It can
  produce strong whole-program results, but it is expensive in time and memory.
- ThinLTO keeps per-module summaries and performs cross-module optimization in a
  more scalable way. It is usually a better fit for very large codebases.

LLVM's
[ThinLTO documentation](http://clang.llvm.org/docs/ThinLTO.html) is useful
background here.

### What llbic Does Today

Modern `llbic` does not try to force one canonical `vmlinux.bc` artifact.
Instead, it asks a more pragmatic question:

What LLVM bitcode does the kernel build already know how to produce, and how can
we collect it reproducibly?

That leads to two execution paths.

#### 1. Kernel-Native Clang LTO

This is the preferred path when the target kernel supports it.

`llbic` enables a kernel configuration that uses Clang LTO, such as
`CONFIG_LTO_CLANG_FULL`, and builds with `LLVM=1`. In this mode, the kernel's
own Clang/LTO flow is responsible for producing LLVM bitcode as part of the
normal compile and link process. `llbic` does not inject an extra pass just to
"dump IR."

After the build, `llbic` searches the relevant build root for real LLVM bitcode
modules, verifies them by file type rather than filename alone, and records the
results in a manifest.

That is the core design choice: `llbic` discovers and records the build's
natural LLVM artifacts instead of trying to synthesize a second build model on
top of the kernel.

#### 2. IRDumper as a Fallback

Some kernels, configurations, or toolchain combinations do not make native LTO
the right answer.

In those cases, `llbic` falls back to the `IRDumper` Clang pass plugin. The
build still produces the normal object files expected by the kernel, but the
plugin also writes one `.bc` file per compiled translation unit.

This has a very different tradeoff profile from the old link-tree approach:

- it preserves the native kernel build
- it avoids reconstructing a synthetic LLVM link graph
- it produces per-file bitcode that is easy to index and analyze

For research and tooling workflows, that is often the more useful artifact
anyway: reproducible, indexable, and tied directly to the real compile path.

### What You Get Back From llbic

Regardless of strategy, `llbic` writes the build record under
`out/linux-<ver>-<arch>-clang<ver>/`.

The important files are:

- `llbic.json`: the machine-readable build summary
- `bitcode_files.txt`: the discovered LLVM bitcode file list
- `llbic.log`: the end-to-end `llbic` log
- `kernel-build.log`: the underlying kernel build log

The key point is that `llbic` is designed around reusable build artifacts, not
around one giant derived bitcode file that may or may not correspond cleanly to
the real kernel build.

## Discussion

The old approach optimized for a seductive output: one monolithic LLVM file.
The current approach optimizes for correctness, portability, and repeatability.

That tradeoff is deliberate.

Linux kernel builds are already complicated. The more faithfully `llbic` can
reuse the kernel's real compile and link behavior, the more likely it is to stay
useful across versions and architectures. Recording the emitted LLVM artifacts
is much more robust than trying to reverse-engineer and replay the entire build
graph in a parallel system.

The project no longer asks the kernel build to become something it is not. It
asks a simpler question instead: what LLVM artifacts does this build already
produce, and how can we make them reproducible, inspectable, and reusable?

That question turns out to be much easier to answer well.

That is why modern `llbic` is less ambitious in one narrow sense, but more
useful in the ways that matter for real research and tooling workflows:

- it gives humans a build they can inspect
- it gives agents an output contract they can continue from
- it avoids reimplementing the kernel build system in a parallel universe
