import os


def dot_callgraph(llvm_bc_out):
    """
    vmlinux.llvm.bc is too large, so we handle every built-in.bc instead
    """
    for root, dirs, files in os.walk(llvm_bc_out):
        if not len(dirs):
            build_in_bc = os.path.join(root, 'build-in.llvm.bc')
            os.system('dot-9 -dot-callgraph {} -o '.format())


