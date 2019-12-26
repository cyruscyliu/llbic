from unittest import TestCase

from passes.graphs import dot_callgraph, dot_cfg


class TestLLVMPass(TestCase):
    def test_mips_31820(self):
        kwargs = {
            'opt_bin_path': '/usr/bin/opt',
            'llvm_bc_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode',
            'analysis_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode/out',
            'analysis_so': '/home/liuqiang/Desktop/llbic/pass',
        }
        dot_callgraph(kwargs['llvm_bc_out'], ['init', 'arch/mips/bcm47xx'])
        dot_cfg(kwargs['llvm_bc_out'], ['init', 'arch/mips/bcm47xx'])
