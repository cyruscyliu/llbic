#!/usr/bin/python
import sys
import argparse

from bin.compile import LLVMCompile
from bin.link import LLVMLink


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LLVM Linux Build Issues Collection')
    parser.add_argument('-a', '--arch', help='Architecture.', choices=['x86_64', 'arm', 'mips'])
    parser.add_argument('-ac', '--action', help='Action of compiling or linking.', choices=['compile', 'link'])
    parser.add_argument('-c', '--clangbin', help='Clang.')
    parser.add_argument('-co', '--command_only', help='Only commands.', action='store_true')
    parser.add_argument('-cop', '--compiler_name', help='Only commands.', action='store_true')
    parser.add_argument('-mo', '--makeout', help='Makeout.txt.', action='store_true')
    parser.add_argument('-o', '--output', help='Linux kernel bitcode.', action='store_true')
    parser.add_argument('-s', '--source', help='Linux kernel source.', action='store_true')

    args = parser.parse_args()

    context = {
        'makeout': args.makeout,
        'arch': args.arch,
        'clangbin': args.clangbin,
        'kernel_src_dir': args.source,
        'llvm_bc_out': args.output,
        'command_only': args.command_only,
        'compiler_name': args.compiler_name,
    }

    if args.action == 'compile':
        compile_(**context)
    elif args.action == 'link':
        link(**context)
    else:
        parser.print_help()
