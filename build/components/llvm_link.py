import os
import subprocess

from build.components.base_component import Component


class LLVMLink(Component):
    """
        Component that links the driver bitcode file with all the dependent bitcode files.
    """

    def __init__(self, **kwargs):
        self.llvm_bc_out = kwargs.pop('llvm_bc_out', None)

    def setup(self):
        if not os.path.exists(self.llvm_bc_out) or not os.path.isdir(self.llvm_bc_out):
            return "Provided LLVM Bitcode directory:" + str(self.llvm_bc_out) + " does not exist."
        return None

    def perform(self):
        return _process_dir(self.llvm_bc_out)

    def get_name(self):
        return "LLVMLink"

    def is_critical(self):
        # Yes, this component is critical
        return True


def _is_bit_code_file(curr_file):
    fp = open(curr_file, 'rb')
    conts = fp.read(2)
    fp.close()
    return conts == b'BC'


def _process_dir(llvm_bc_out):
    to_test_bc = os.path.join(llvm_bc_out, "vmlinux.llvm.bc")
    all_link_files = []
    for root, dirs, files in os.walk(llvm_bc_out):
        if not len(dirs):
            for file_ in files:
                link_file = os.path.join(root, file_)
                if _is_bit_code_file(link_file):
                    all_link_files.append(link_file)
    os.system('llvm-link-9 ' + " ".join(all_link_files) + " -o " + to_test_bc)
    os.system('llvm-dis-9 vmlinux.llvm.bc -o vmlinux.llvm.ll')
    print("To check BC file:" + to_test_bc)
    return True
