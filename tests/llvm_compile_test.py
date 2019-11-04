from unittest import TestCase
from helper.compile import LLVMCompile
import os

home = '/home/liuqiang/Desktop'


def compile_(**kwargs):
    llvm_compile = LLVMCompile(**kwargs)
    status = llvm_compile.setup()
    if status is not None:
        print(status)
        return
    llvm_compile.perform()


class TestLLVMCompile(TestCase):

    def test_mips_31820(self):
        kwargs = {
            'makeout': os.path.join(home, 'linux-3.18.20/makeout.txt'),
            'clangbin': '/usr/bin/clang-9',
            'llvm_bc_out': os.path.join(home, 'linux-3.18.20-llvm-bitcode'),
            'compiler_name': os.path.join(
                home, 'staging_dir/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-gcc'),
            'arch': 'mips',
            'kernel_src_dir': os.path.join(home, 'linux-3.18.20')
        }
        compile_(**kwargs)

    def test_arm_31820(self):
        kwargs = {
            'makeout': os.path.join(home, 'linux-3.18.20/makeout.txt'),
            'clangbin': '/usr/bin/clang-9',
            'llvm_bc_out': os.path.join(home, 'linux-3.18.20-llvm-bitcode'),
            'compiler_name': os.path.join(
                home, 'staging_dir/toolchain-arm_mpcore_gcc-4.8-linaro_uClibc-0.9.33.2_eabi/bin/arm-openwrt-linux-gcc'),
            'arch': 'arm',
            'kernel_src_dir': os.path.join(home, 'linux-3.18.20')
        }
        compile_(**kwargs)
