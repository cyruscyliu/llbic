#include <assert.h>
#include <stdio.h>

#include <iostream>
#include <map>
#include <vector>
#include <set>

#include "llvm/IR/Constants.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/GlobalVariable.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/InlineAsm.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Type.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Pass.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Bitcode/BitcodeWriter.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"

// PassManagerBuilder was removed in LLVM 17
#if LLVM_VERSION_MAJOR < 17
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#endif

using namespace llvm;

// Legacy pass manager (Clang <= 16, requires -flegacy-pass-manager)
#if LLVM_VERSION_MAJOR < 17
class LegacyIRDumper : public ModulePass {

public:
	static char ID;

	LegacyIRDumper() : ModulePass(ID) {}

	virtual bool runOnModule(Module &M);
};
#endif

// New pass manager (Clang >= 14)
class IRDumper : public PassInfoMixin<IRDumper> {

public:
	PreservedAnalyses run(Module &M, ModuleAnalysisManager &);
};
