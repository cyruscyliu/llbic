import os


def check_path(path, limit):
    for lm in limit:
        if path.find(lm) != -1:
            return True
    return False


def dot_callgraph(llvm_bc_out, limit):
    """
    vmlinux.llvm.bc is too large, so we handle every built-in.bc instead
    """
    for root, dirs, files in os.walk(llvm_bc_out):
        if not check_path(root, limit):
            continue
        build_in_bc = os.path.join(root, 'built-in.llvm.bc')
        if not os.path.exists(build_in_bc):
            continue
        cwd = os.getcwd()
        os.chdir(root)
        os.system('opt-9 -dot-callgraph {} >/dev/null 2>&1'.format(build_in_bc))
        os.system('dot -O -Tpdf callgraph.dot')
        os.chdir(cwd)


def dot_cfg(llvm_bc_out, limit):
    """
    vmlinux.llvm.bc is too large, so we handle every built-in.bc instead
    """
    for root, dirs, files in os.walk(llvm_bc_out):
        if not check_path(root, limit):
            continue
        build_in_bc = os.path.join(root, 'built-in.llvm.bc')
        if not os.path.exists(build_in_bc):
            continue
        cwd = os.getcwd()
        os.chdir(root)
        os.system('opt-9 -dot-cfg-only {} >/dev/null 2>&1'.format(build_in_bc))
        for dot_file in os.listdir(root):
            if dot_file.startswith('.') and dot_file.endswith('dot'):
                os.system('dot -O -Tpdf {}'.format(dot_file))
        os.chdir(cwd)
