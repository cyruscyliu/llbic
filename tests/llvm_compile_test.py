from unittest import TestCase
from helper.compile import LLVMCompile


class TestLLVMCompile(TestCase):
    def test_mips_31820(self):
        kwargs = {
            'makeout': '/home/liuqiang/Desktop/linux-3.18.20/makeout.txt',
            'clangbin': '/usr/bin/clang-9',
            'llvm_bc_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode',
            'compiler_name': '/home/liuqiang/Desktop/staging_dir/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-gcc',
            'arch': 'mips',
            'kernel_src_dir': '/home/liuqiang/Desktop/linux-3.18.20'
        }
        llvm_compile = LLVMCompile(**kwargs)
        status = llvm_compile.setup()
        if status is not None:
            print(status)
            return
        llvm_compile.perform()
