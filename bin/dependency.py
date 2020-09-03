from graphviz import Digraph

import os
import sys

# special state
final_init_built_in = False
final_init_version = False


def valid_command(command_split, indicator):
    return len(command_split) and command_split[0].endswith(indicator) or \
           len(command_split) > 1 and command_split[1].endswith(indicator)


def parse_gcc_target_and_source(command_split):
    """
     gcc CFLAGS -S -o kernel/bounds.s kernel/bounds.c
    """
    global final_init_version
    target = command_split[-2]
    source = command_split[-1]
    if target == 'init/version.o':
        if final_init_version:
            return target, source
        else:
            final_init_version = True
            return None, source
    else:
        return target, source


def parse_ld_target_and_sources(command_split):
    """
    ld -m elf32ltsmip -G 0 -static -n -nostdlib --build-id -X -o vmlinux -T ./arch/mips/kernel/vmlinux.lds \
        arch/mips/kernel/head.o init/built-in.o --start-group usr/built-in.o arch/mips/built-in.o kernel/built-in.o \
        mm/built-in.o fs/built-in.o ipc/built-in.o security/built-in.o crypto/built-in.o block/built-in.o lib/lib.a \
        arch/mips/fw/lib/lib.a arch/mips/lib/lib.a arch/mips/math-emu/lib.a lib/built-in.o \
        arch/mips/fw/lib/built-in.o arch/mips/lib/built-in.o arch/mips/math-emu/built-in.o drivers/built-in.o \
        sound/built-in.o firmware/built-in.o arch/mips/pci/built-in.o net/built-in.o --end-group
    """
    global final_init_built_in

    target_and_sources = []
    for item in reversed(command_split):
        if item.startswith('--'):
            continue
        if item == '-T':
            # remove vmlinux.lds
            target_and_sources.pop()
            continue
        if item == '-o':
            break
        target_and_sources.append(item)
    target = target_and_sources[-1]
    sources = target_and_sources[:-1]
    if target == 'init/built-in.o':
        if final_init_built_in:
            return target, sources
        else:
            final_init_built_in = True
            return None, sources
    elif target == 'vmlinux.o':
        return None, sources
    else:
        return target, sources


def parse_ar_target_and_sources(command_split):
    """
    ar rcsD drivers/amba/built-in.o
    ar rcsD arch/mips/math-emu/lib.a arch/mips/math-emu/dp_sqrt.o arch/mips/math-emu/ieee754d.o arch/mips/math-emu/sp_sqrt.o
    """
    target_and_sources = []
    for item in reversed(command_split):
        if item.endswith('-ar'):
            break
        target_and_sources.append(item)
    target = target_and_sources[-2]
    sources = target_and_sources[:-2]
    return target, sources


def find_dependency(path_to_makeout, graph):
    ordered_nodes = []
    commands = []
    with open(path_to_makeout) as f:
        for line in f:
            commands.extend(line.split(';'))

    nodes_to_remove = []
    for command in commands:
        items = command.split()
        if valid_command(items, '-gcc') or valid_command(items, 'ccache_cc'):
            target, source = parse_gcc_target_and_source(items)
            if target is not None:
                graph.edge(source, target)
                ordered_nodes.append(source)
        if valid_command(items, '-ld'):
            target, sources = parse_ld_target_and_sources(items)
            if target is not None:
                for source in sources:
                    graph.edge(source, target)
                    ordered_nodes.append(source)
        if valid_command(items, '-ar'):
            target, sources = parse_ar_target_and_sources(items)
            if len(sources):
                for source in sources:
                    graph.edge(source, target)
                    ordered_nodes.append(source)
            else:
                nodes_to_remove.append(target)
                if target in ordered_nodes:
                    ordered_nodes.remove(target)

    graph.remove(nodes_to_remove)
    return ordered_nodes


def dot_remove(self, nodes_to_remove):
    # remove useless node
    for node_to_remove in nodes_to_remove:
        target_node_is_useless = None
        for node in self.body:
            if node.strip().startswith('"' + node_to_remove):
                target_node_is_useless = node
                break
        if target_node_is_useless is None:
            continue
        self.body.remove(target_node_is_useless)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage python {} path/to/makeout.txt'.format(sys.argv[0]))
        exit(-1)
    path_to_makeout = sys.argv[1]

    # prepare the dot
    setattr(Digraph, 'remove', dot_remove)
    graph = Digraph(comment='build dependency')
    graph.attr(rankdir='LR')
    graph.attr(ratio='compress')
    ordered_nodes = find_dependency(path_to_makeout, graph)
    print(ordered_nodes)
    graph.render('makeout.gv', view=False)
    with open('order.csv', 'w') as f:
        f.write('\n'.join(ordered_nodes))
    print('makeout.gv makeout.gv.pdf order.csv at {}'.format(os.path.dirname(os.path.realpath('./'))))
