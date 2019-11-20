import sys

from helper.compile import LLVMCompile


def compile_(**kwargs):
    llvm_compile = LLVMCompile(**kwargs)
    status = llvm_compile.setup()
    if status is not None:
        print(status)
        return
    llvm_compile.perform()


def main(argv):
    algorithm = argv[1]
    action = argv[2]

    if algorithm == 'dr_checker' and action == 'compile':
        kwargs = {
            'makeout': argv[3],
            'arch': argv[4],
            'clangbin': argv[5],
            'compiler_name': argv[6],
            'kernel_src_dir': argv[7],
            'llvm_bc_out': argv[8],
        }
        compile_(**kwargs)


if __name__ == '__main__':
    main(sys.argv)
