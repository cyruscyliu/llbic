from graphviz import Digraph

import os
import sys

# special state
final_init_built_in = False
final_init_version = False

dot = Digraph(comment='build dependency')
dot.attr(rankdir='LR')
dot.attr(ratio='compress')


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


def main(path_to_makeout):
    commands = []
    with open(path_to_makeout) as f:
        for line in f:
            commands.extend(line.split(';'))

    nodes_to_remove = []
    for command in commands:
        items = command.split()
        if valid_command(items, '-gcc'):
            target, source = parse_gcc_target_and_source(items)
            if target is not None:
                dot.edge(source, target)
        if valid_command(items, '-ld'):
            target, sources = parse_ld_target_and_sources(items)
            if target is not None:
                for source in sources:
                    dot.edge(source, target)
        if valid_command(items, '-ar'):
            target, sources = parse_ar_target_and_sources(items)
            if len(sources):
                for source in sources:
                    dot.edge(source, target)
            else:
                nodes_to_remove.append(target)

    # remove useless node
    for node_to_remove in nodes_to_remove:
        target_node_is_useless = None
        for node in dot.body:
            if node.strip().startswith('"' + node_to_remove):
                target_node_is_useless = node
                break
        if target_node_is_useless is None:
            continue
        dot.body.remove(target_node_is_useless)
    dot.render('makeout.gv', view=False)
    print('makeout.gv and makeout.gv.pdf at {}'.format(os.path.dirname(os.path.realpath(path_to_makeout))))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage python {} path/to/makeout.txt'.format(sys.argv[0]))
        exit(-1)
    path_to_makeout = sys.argv[1]
    main(path_to_makeout)
