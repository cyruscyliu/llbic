#include "IRDumper.h"

using namespace llvm;


void saveModule(Module &M, Twine filename)
{
	int bc_fd;
	StringRef FN = filename.getSingleStringRef();
	sys::fs::openFileForWrite(
			FN.take_front(FN.size() - 2) + ".bc", bc_fd);
	raw_fd_ostream bc_file(bc_fd, true, true);
	WriteBitcodeToFile(M, bc_file);
}

/* ===== Legacy Pass Manager (LLVM < 17) ===== */
#if LLVM_VERSION_MAJOR < 17

bool LegacyIRDumper::runOnModule(Module &M) {
	saveModule(M, M.getName());
	return false;
}

char LegacyIRDumper::ID = 0;
static RegisterPass<LegacyIRDumper> X("IRDumper", "IRDumper pass", false, false);

static void register_pass(const PassManagerBuilder &PMB,
		legacy::PassManagerBase &PM) {
	PM.add(new LegacyIRDumper());
}

static RegisterStandardPasses RegisterIRDumperPass(
		PassManagerBuilder::EP_OptimizerLast, register_pass);
static RegisterStandardPasses RegisterRDumperPassL0(
		PassManagerBuilder::EP_EnabledOnOptLevel0, register_pass);

#endif /* LLVM_VERSION_MAJOR < 17 */

/* ===== New Pass Manager (all versions) ===== */

PreservedAnalyses IRDumper::run(Module &M, ModuleAnalysisManager &) {
	saveModule(M, M.getName());
	return PreservedAnalyses::all();
}

llvm::PassPluginLibraryInfo getIRDumperPluginInfo() {
	return {LLVM_PLUGIN_API_VERSION, "IRDumper", LLVM_VERSION_STRING,
		[](PassBuilder &PB) {
			PB.registerPipelineParsingCallback(
					[](StringRef Name, llvm::ModulePassManager &PM,
						ArrayRef<llvm::PassBuilder::PipelineElement>) {
					if (Name == "IRDumper") {
					PM.addPass(IRDumper());
					return true;
					}
					return false;
					});
		}};
}

#ifndef LLVM_BYE_LINK_INTO_TOOLS
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
	return getIRDumperPluginInfo();
}
#endif
