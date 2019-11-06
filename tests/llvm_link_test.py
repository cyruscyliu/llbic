import os
from unittest import TestCase

from helper.link import LLVMLink

home = '/home/liuqiang/Desktop'


def link(**kwargs):
    llvm_link = LLVMLink(**kwargs)
    status = llvm_link.setup()
    if status is not None:
        print(status)
        return
    llvm_link.perform()


class TestLLVMLink(TestCase):
    def test_31820(self):
        kwargs = {
            'llvm_bc_out': os.path.join(home, 'linux-3.18.20-llvm-bitcode'),
        }
        link(**kwargs)

    def test_2632(self):
        kwargs = {
            'llvm_bc_out': os.path.join(home, 'linux-2.6.32-llvm-bitcode'),
        }
        link(**kwargs)
