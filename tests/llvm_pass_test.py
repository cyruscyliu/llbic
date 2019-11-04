from unittest import TestCase

from passes.graphs import dot_callgraph, dot_cfg


class TestLLVMPass(TestCase):
    def test_mips_31820(self):
        kwargs = {
            'opt_bin_path': '/usr/bin/opt-9',
            'llvm_bc_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode',
            'analysis_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode/out',
            'analysis_so': '/home/liuqiang/Desktop/llbic/pass',
        }
        dot_callgraph(kwargs['llvm_bc_out'])
        dot_cfg(kwargs['llvm_bc_out'])
