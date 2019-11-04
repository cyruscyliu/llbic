from unittest import TestCase

from build.llvm_link import LLVMLink


class TestLLVMLink(TestCase):
    def test_mips_31820(self):
        kwargs = {
            'llvm_bc_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode',
        }
        llvm_link = LLVMLink(**kwargs)
        status = llvm_link.setup()
        if status is not None:
            print(status)
            return
        llvm_link.perform()
