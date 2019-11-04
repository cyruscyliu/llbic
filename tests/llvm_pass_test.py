from unittest import TestCase


class TestLLVMLink(TestCase):
    def test_mips_31820(self):
        kwargs = {
            'opt_bin_path': '/usr/bin/opt-9',
            'llvm_bc_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode',
            'analysis_out': '/home/liuqiang/Desktop/linux-3.18.20-llvm-bitcode/out',
            'analysis_so': '/home/liuqiang/Desktop/llbic/pass',
        }
        analysis_runner = AnalysisRunner(**kwargs)
        status = analysis_runner.setup()
        if status is not None:
            print(status)
            return
        analysis_runner.perform()
