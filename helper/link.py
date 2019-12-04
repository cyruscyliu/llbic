"""
Copyright (c) 2015, The Regents of the University of California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS'
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
"""
import os
import networkx as nx
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

from helper.base import Component
from helper.dependency import find_dependency


class GraphWrapper(object):
    def __init__(self):
        self.graph = nx.DiGraph()

    def edge(self, from_node, to_node):
        self.graph.add_edge(to_node, from_node)

    def remove(self, nodes):
        assert isinstance(nodes, list)
        for node in nodes:
            try:
                self.graph.remove_node(node)
            except nx.exception.NetworkXError as e:
                pass

    def leafs(self):
        vmlinux = nx.descendants(self.graph, 'vmlinux')
        return [x for x in vmlinux if self.graph.out_degree(x) == 0 and self.graph.in_degree(x) == 1]


class LLVMLink(Component):
    '''
        Component that links the driver bitcode file with all the dependent bitcode files.
    '''

    def __init__(self, **kwargs):
        self.curr_makeout = kwargs.pop('makeout', None)
        self.clang_bin = kwargs.pop('clangbin', None)
        self.llvm_bc_out = kwargs.pop('llvm_bc_out', None)

    def setup(self):
        if (not os.path.exists(self.curr_makeout)) or \
                (not os.path.exists(self.clang_bin)):
            return "Required files(" + str(self.curr_makeout) + ", " + str(self.clang_bin) + ") do not exist"
        if not os.path.exists(self.llvm_bc_out) or not os.path.isdir(self.llvm_bc_out):
            return 'Provided LLVM Bitcode directory:' + str(self.llvm_bc_out) + ' does not exist.'
        return None

    def perform(self):
        return _process_dependency_and_link(self.curr_makeout, self.clang_bin, self.llvm_bc_out)

    def get_name(self):
        return 'LLVMLink'

    def is_critical(self):
        # Yes, this component is critical
        return True


def _is_bit_code_file(curr_file):
    fp = open(curr_file, 'rb')
    conts = fp.read(2)
    fp.close()
    return conts == b'BC'


def get_ordered_link_files(all_link_files, ordered_nodes):
    ordered_link_files = []
    for node in ordered_nodes:
        if node in all_link_files:
            ordered_link_files.append(node)
    return ordered_link_files


def _process_dependency_and_link(makeout, llvm_link, llvm_bc_out):
    # find denpendency
    graph = GraphWrapper()
    ordered_nodes = find_dependency(makeout, graph)
    all_link_files = graph.leafs()
    ordered_link_files = get_ordered_link_files(all_link_files, ordered_nodes)

    # link all required files together in order, but only c code
    link_files = []
    for all_link_file in ordered_link_files:
        name, _, extent = str(all_link_file).partition('.')
        if extent == 'c':
            link_files.append('-override')
            link_files.append(name + '.llvm.bc')
    # to avoid not enough positional comand line arguments
    link_files.pop(0)
    built_in_bc = os.path.join(llvm_bc_out, 'vmlinux.llvm.bc')
    cmd = llvm_link + ' ' + ' '.join(link_files) + ' -o ' + built_in_bc

    # let's do it
    cwd = os.getcwd()
    os.chdir(llvm_bc_out)
    os.system(cmd)
    os.chdir(cwd)
    print('[+] To check BC file:' + built_in_bc)

    return True
