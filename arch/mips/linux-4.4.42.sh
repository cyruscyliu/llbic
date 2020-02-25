patch -b drivers/md/raid10.c /home/root/llbic/arch/mips/md-raid10-remove-VLAIS.diff
grep fault@function -rl arch/mips | xargs -l sed -i -r "s/fault@function/fault,@function/"
