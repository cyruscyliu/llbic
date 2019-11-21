import sys

from helper.compile import LLVMCompile
from helper.link import LLVMLink


def compile_(**kwargs):
    llvm_compile = LLVMCompile(**kwargs)
    status = llvm_compile.setup()
    if status is not None:
        print(status)
        return
    llvm_compile.perform()


def link(**kwargs):
    llvm_link = LLVMLink(**kwargs)
    status = llvm_link.setup()
    if status is not None:
        print(status)
        return
    llvm_link.perform()


def main(argv):
    algorithm = argv[1]
    action = argv[2]

    if len(argv) == 9 and algorithm == 'dr_checker' and action == 'compile':
        context = {'makeout': argv[3], 'arch': argv[4], 'clangbin': argv[5],
                   'compiler_name': argv[6], 'kernel_src_dir': argv[7], 'llvm_bc_out': argv[8]}
        compile_(**context)
    elif len(argv) == 6 and algorithm == 'dr_checker' and action == 'link':
        context = {'makeout': argv[3], 'clangbin': argv[4], 'llvm_bc_out': argv[5]}
        link(**context)
    else:
        print('usage:')
        print('\tpython wrapper.py dr_checker compile path/to/makeout.txt arch path/to/clang '
              'path/to/gcc  path/to/kernel_src_dir path/to/llvm_bc_out')
        print('\tpython wrapper.py dr_checker link path/to/makeout.txt path/to/llvm-link path/to/llvm_bc_out')


if __name__ == '__main__':
    main(sys.argv)
