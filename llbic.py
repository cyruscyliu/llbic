#!/usr/bin/python
import os
import sys
import argparse
import subprocess

from bin.utils import get_version, get_compiler_name, patch
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
    parser.add_argument('action', help='Patch, compile or link.', choices=['patch', 'compile', 'link'])
    parser.add_argument('-a', '--arch', help='Architecture.', choices=['arm', 'mips'], required=True)
    parser.add_argument('-s', '--source', help='Path to Linux kernel source code.', required=True)
    parser.add_argument('-mo', '--makeout', help='Path to makeout.txt.', required=True) 
    parser.add_argument('-lc', '--llvm_config', help='Path to llvm-config.', default='llvm-config')
    parser.add_argument('-o', '--output', help='Path to Linux kernel llvm bitcode.')
    parser.add_argument('-co', '--command_only', help='Command only mode.', action='store_true', default=False)

    args = parser.parse_args()

    if args.output is None:
        args.output = args.source + '-llvm-bitcode'

    llvm_bindir = subprocess.check_output(
        '{} --bindir'.format(args.llvm_config), shell=True).decode()

    context = {
        'makeout': args.makeout,
        'llvm_bc_out': args.output,
        'compiler_name': get_compiler_name(args.source),
        'arch': args.arch,
        'out': None,
        'kernel_src_dir': args.source,
        'command_only': args.command_only,
    }

    if args.action == 'compile':
        clang = os.path.join(llvm_bindir, 'clang')
        context['clangbin'] = clang
        compile_(**context)
    elif args.action == 'link':
        llvm_link = os.path.join(llvm_bindir, 'llvm_link')
        context['clangbin'] = llvm_link
        link(**context)
    elif args.action == 'patch':
        patch(arg.source)
    else:
        parser.print_help()
