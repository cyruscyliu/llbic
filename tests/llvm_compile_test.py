from unittest import TestCase
import os

from wrapper import compile_

home = '/home/liuqiang/Desktop'


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

    def test_arm_2632(self):
        kwargs = {
            'makeout': os.path.join(home, 'linux-2.6.32/makeout.txt'),
            'clangbin': '/usr/bin/clang-9',
            'llvm_bc_out': os.path.join(home, 'linux-2.6.32-llvm-bitcode'),
            'compiler_name': os.path.join(
                home, 'staging_dir/toolchain-arm_v5t_gcc-4.3.3+cs_uClibc-0.9.30.1_eabi/usr/bin/arm-openwrt-linux-gcc'),
            'arch': 'arm',
            'kernel_src_dir': os.path.join(home, 'linux-2.6.32')
        }
        compile_(**kwargs)
