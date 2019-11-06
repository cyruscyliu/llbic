# overview 

### specific
`arm`
`2.6.32`

### buildable kernel
`linux-2.6.32 patched by OpenWrt`

```text
Can't use 'defined(@array)' (Maybe you should just omit the defined()?) at kernel/timeconst.pl line 373.
/home/liuqiang/Desktop/linux-2.6.32/kernel/Makefile:129: recipe for target 'kernel/timeconst.h' failed

change "if (!defined(@array)) {" to "if (!@array) {"
```

### toolchains
`arm-openwrt-linux-`
# invalid instruction

```text
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/kernel/entry-armv.S:946:2: error: instruction 'rsbcs' can not set flags, but 's' suffix specified
 rsbcss r8, r8, #(2b - 1b)
 ^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/kernel/entry-common.S:307:2: error: invalid instruction
 ldmccia r1, {r0 - r3} @ have to reload r0 - r3
 

^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/kernel/entry-common.S:353:3: error: invalid instruction
  stmloia sp, {r5, r6} @ shuffle args
  ^
<instantiation>:5:2: error: invalid instruction, did you mean: str, strb, strd, strh, strt, trap?
 stralt r3, [r0], #4
 ^
<instantiation>:1:1: note: while in macro instantiation
.rept 1
^
<instantiation>:1:1: note: while in macro instantiation
usracc str, r3, r0, 4, al, 1, 20f
^
<instantiation>:1:1: note: while in macro instantiation
strusr r3, r0, 4, abort=20f
^
<instantiation>:1:1: note: while in macro instantiation
str1w r0, r3, 20f
^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/lib/copy_template.S:102:3: note: while in macro instantiation
  str8w r0, r3, r4, r5, r6, r7, r8, ip, lr, abort=20f
  ^
```

##### solutions
```shell script
find ./arch/arm -name "*.[hSc]" -exec sed -i -r "s/^((\s*[._a-zA-Z0-9]*[\:\(])?\s*)([a-z]{3})(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)([a-z]{1,2})(\s)/\1\3\5\4\6/" {} \;
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/copy_from_user.S
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/copy_to_user.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)bt/\\\\instr\\\\\(\)bt\\\\cond/" arch/arm/include/asm/assembler.h 
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)t/\\\\instr\\\\\(\)t\\\\cond/" arch/arm/include/asm/assembler.h 
# fix fp
sed -i -r "s/lenhgt/length/" arch/arm/mm/mmu.c
sed -i -r "s/sigdne/signed/" arch/arm/mm/alignment.c
sed -i -r "s/sigdne/signed/" arch/arm/kernel/ptrace.c
```

###  too many positional arguments

```text
<instantiation>:40:47: error: too many positional arguments
  str8w r0, r3, r4, r5, r6, r7, r8, r9, ip, , abort=19f
                                              ^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/lib/copy_template.S:247:5: note: while in macro instantiation
18: forward_copy_shift lsr=24 lsl=8
    ^
```

##### solutions

>Remove `,`.
>[Click and see detials.](https://lkml.org/lkml/2019/1/3/545)


### expected string in directive

```text
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/mm/proc-feroceon.S:546:30: error: expected string in directive
 .section ".proc.info.init", #alloc, #execinstr
                             ^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/boot/compressed/head.S:98:22: error: expected string in directive
  .section ".start", #alloc, #execinstr
                     ^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/boot/compressed/piggy.S:1:22: error: expected string in directive
 .section .piggydata,#alloc
                     ^
```

###### solutions

>Replace Sun/Solaris style flag on section directive.
>[Click and see details.](https://lkml.org/lkml/2019/10/30/807)

### variable length array 

```text
/home/liuqiang/Desktop/linux-2.6.32/crypto/testmgr.c:1433:9: error: fields must have a constant size: 'variable length array in structure' extension will never be supported
                        char ctx[crypto_shash_descsize(tfm)];
                             ^
1 error generated.
/home/liuqiang/Desktop/linux-2.6.32/crypto/hmac.c:58:8: error: fields must have a constant size: 'variable length array in structure' extension will never be supported
                char ctx[crypto_shash_descsize(hash)];
                     ^
1 error generated.
/home/liuqiang/Desktop/linux-2.6.32/lib/libcrc32c.c:46:8: error: fields must have a constant size: 'variable length array in structure' extension will never be supported
                char ctx[crypto_shash_descsize(tfm)];
                     ^
1 error generated.
```

##### solutions

>[Click and see details](https://lkml.org/lkml/2012/10/30/521) for testmgr.c.
>[Click and see details](https://lkml.org/lkml/2012/10/30/376) for hmac.c.
>[Click and see details](https://www.redhat.com/archives/dm-devel/2014-September/msg00119.html) for libcrc32c.c

### invalid instruction

```text
<instantiation>:8:2: error: invalid instruction, did you mean: strb, strexb?
 strneb r2, [r1]
 ^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/lib/testclearbit.S:18:2: note: while in macro instantiation
 testop bicne, strneb
 ^
<instantiation>:8:2: error: invalid instruction, did you mean: strb, strexb?
 streqb r2, [r1]
 ^
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/lib/testsetbit.S:18:2: note: while in macro instantiation
 testop orreq, streqb
 ^
```

###### solutions
>strneb -> strbne, streqb -> strbeq

### operand must be a register in range [r0, r14] or apsr_nzcv

```text 
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/boot/compressed/head.S:946:16: error: operand must be a register in range [r0, r14] or apsr_nzcv
1: mrc p15, 0, r15, c7, c14, 3 @ test,clean,invalidate D cache
               ^
```

##### solutions

>LLVM's integrated assembler does not accept r15 as mrc operand.
>[Click and see details.](https://lkml.org/lkml/2019/11/1/717)

