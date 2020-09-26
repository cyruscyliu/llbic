import os

def get_version(source):
    makefile = os.path.join(source, 'Makefile')
    with open(makefile) as f:
        for line in f:
            if line.startswith('VERSION'):
                version = line.strip().split('=')[1].strip()
                patchlevel = line.strip().split('=')[1].strip()
                sublevel = line.strip().split('=')[1].strip()
    return '{}.{}.{}'.format(version, patchlevel, sublevel)


def get_compiler_name(source):
    fork_o_cmd = os.path.join(source, 'kernel/.fork.o.cmd')
    with open(fork_o_cmd) as f:
        cmd = f.realine()
    compiler_name = cmd.split(':=')[1].split()[0]
    return compiler_name
