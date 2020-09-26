import os

def get_version(source):
    makefile = os.path.join(source, 'Makefile')
    with open(makefile) as f:
        for line in f:
            if line.startswith('VERSION'):
                version = line.strip().split('=')[1].strip()
                continue
            if line.startswith('PATCHLEVEL'):
                patchlevel = line.strip().split('=')[1].strip()
                continue
            if line.startswith('SUBLEVEL'):
                sublevel = line.strip().split('=')[1].strip()
                break
    return '{}.{}.{}'.format(version, patchlevel, sublevel)


def get_compiler_name(source):
    fork_o_cmd = os.path.join(source, 'kernel/.fork.o.cmd')
    with open(fork_o_cmd) as f:
        cmd = f.readline()
    compiler_name = cmd.split(':=')[1].split()[0]
    return compiler_name


def patch(source, patches=None, backup=True):
    kernel_ver = get_version(source)
    patch_dir = os.path.join('patches/{}'.format(kernel_ver))
    patch_sh = 'linux-{}.sh'.format(kernel_ver)

    for patch in os.listdir(patch_dir):
        if patch.endswith('diff'):
            os.system('cp patches/{}/{} {}'.format(kernel_ver, patch, source))
    os.system('cp patches/{}/{} {}'.format(kernel_ver, patch_sh, source))

    if backup:
        backup_source = source + '.ori'
        if not os.path.exists(backup_source):
            print("[+] Backing up the Linux kernel source code.")
            os.system('cp -rL {} {}'.format(source, backup_source))
        else:
            print("[+] Backed up the Linux kernel source code.")

    cwd = os.getcwd()
    os.chdir(source)
    print("[+] Patching the Linux kernel source code.")
    os.system('./{}'.format(patch_sh))
    os.chdir(cwd)
