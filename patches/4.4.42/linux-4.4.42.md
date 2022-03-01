# issues

### error: unknown token in expression/error: expected stack offset value

```text
/root/linux-4.4.42/arch/mips/boot/compressed/head.S:19:12: error: unknown token in expression
 .cprestore
           ^
/root/linux-4.4.42/arch/mips/boot/compressed/head.S:19:12: error: expected stack offset value
 .cprestore
```

##### solutions: 

unknown!

```shell script
```

### error: fields must have a constant size: 'variable length array in structure' extension will never be supported

```text
/root/linux-4.4.42/drivers/md/raid10.c:4491:17: error: fields must have a constant size: 'variable length array in structure' extension will never be supported
                struct r10dev devs[conf->copies];
                              ^
1 error generated.
```

##### solutions

>[Click and see details.](https://lore.kernel.org/patchwork/patch/837496/)

```shell script
patch -b drivers/md/raid10.c md-raid10-remove-VLAIS.diff
```

### error: expected STT_<TYPE_IN_UPPER_CASE>, '#<type>', '@<type>', '%<type>' or "<type>"

```text
/root/linux-4.4.42/arch/mips/kernel/r4k_fpu.S:361:22: error: expected STT_<TYPE_IN_UPPER_CASE>, '#<type>', '@<type>', '%<type>' or "<type>"
 .type fault@function
                     ^
```

##### solutions
>should be .type fault,@function
>[Click and see details.](https://sourceware.org/binutils/docs/as/Type.html#Type)

```shell script
grep fault@function -rl arch/mips | xargs -l sed -i -r "s/fault@function/fault,@function/"
```
