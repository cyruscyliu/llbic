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


def patch(source):
    kernel_ver = get_version(source)
    patch_dir = os.path.join('patches/{}'.format(kernel_ver))
    patch_sh = os.path.join(patch_dir, 'linux-{}'.format(kernel_ver))

    for patch in os.listdir(patch_dir):
        if patch.endswith('diff'):
            os.system('cp {} {}'.format(patch, source))

    cwd = os.getcwd()
    os.chdir(source)
    os.system(patch_sh)
    os.chdir(cwd)
