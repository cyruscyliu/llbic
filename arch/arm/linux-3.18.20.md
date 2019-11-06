# overview 

### specific
`arm`
`3.18.20`

### buildable kernel
`linux-3.18.20 patched by OpenWrt`

### toolchains
`arm-openwrt-linux-`

# issues

### invalid instruction

```text
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/kernel/entry-common.S:475:2: error: invalid instruction
 ldmccia r1, {r0 - r6} @ have to reload r0 - r6
 ^
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/kernel/entry-common.S:476:2: error: invalid instruction
 stmccia sp, {r4, r5} @ and update the stack args
 ^
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/kernel/entry-common.S:523:3: error: invalid instruction
  stmloia sp, {r5, r6} @ shuffle args
  ^
```

##### solutions

```text
diff --git a/arch/arm/kernel/entry-common.S b/arch/arm/kernel/entry-common.S
index 10c3283d6c19..56be67ecf0fa 100644
--- a/arch/arm/kernel/entry-common.S
+++ b/arch/arm/kernel/entry-common.S
@@ -223,9 +223,7 @@ local_restart:
tst r10, #_TIF_SYSCALL_WORK @ are we tracing syscalls?
bne __sys_trace

- cmp scno, #NR_syscalls @ check upper syscall limit
- badr lr, ret_fast_syscall @ return address
- ldrcc pc, [tbl, scno, lsl #2] @ call sys_* routine
+ invoke_syscall tbl, scno, r10, ret_fast_syscall

add r1, sp, #S_OFF
2: cmp scno, #(__ARM_NR_BASE - __NR_SYSCALL_BASE)
@@ -258,14 +256,8 @@ __sys_trace:
mov r1, scno
add r0, sp, #S_OFF
bl syscall_trace_enter
-
- badr lr, __sys_trace_return @ return address
- mov scno, r0 @ syscall number (possibly new)
- add r1, sp, #S_R0 + S_OFF @ pointer to regs
- cmp scno, #NR_syscalls @ check upper syscall limit
- ldmccia r1, {r0 - r6} @ have to reload r0 - r6
- stmccia sp, {r4, r5} @ and update the stack args
- ldrcc pc, [tbl, scno, lsl #2] @ call sys_* routine
+ mov scno, r0
+ invoke_syscall tbl, scno, r10, __sys_trace_return, reload=1
cmp scno, #-1 @ skip the syscall?
bne 2b
add sp, sp, #S_OFF @ restore stack
@@ -317,6 +309,10 @@ sys_syscall:
bic scno, r0, #__NR_OABI_SYSCALL_BASE
cmp scno, #__NR_syscall - __NR_SYSCALL_BASE
cmpne scno, #NR_syscalls @ check range
+#ifdef CONFIG_CPU_SPECTRE
+ movhs scno, #0
+ csdb
+#endif
stmloia sp, {r5, r6} @ shuffle args
movlo r0, r1
movlo r1, r2
diff --git a/arch/arm/kernel/entry-header.S b/arch/arm/kernel/entry-header.S
index e056c9a9aa9d..fa7c6e5c17e7 100644
--- a/arch/arm/kernel/entry-header.S
+++ b/arch/arm/kernel/entry-header.S
@@ -377,6 +377,31 @@
#endif
.endm
+ .macro invoke_syscall, table, nr, tmp, ret, reload=0
+#ifdef CONFIG_CPU_SPECTRE
+ mov \tmp, \nr
+ cmp \tmp, #NR_syscalls @ check upper syscall limit
+ movcs \tmp, #0
+ csdb
+ badr lr, \ret @ return address
+ .if \reload
+ add r1, sp, #S_R0 + S_OFF @ pointer to regs
+ ldmccia r1, {r0 - r6} @ reload r0-r6
+ stmccia sp, {r4, r5} @ update stack arguments
+ .endif
+ ldrcc pc, [\table, \tmp, lsl #2] @ call sys_* routine
+#else
+ cmp \nr, #NR_syscalls @ check upper syscall limit
+ badr lr, \ret @ return address
+ .if \reload
+ add r1, sp, #S_R0 + S_OFF @ pointer to regs
+ ldmccia r1, {r0 - r6} @ reload r0-r6
+ stmccia sp, {r4, r5} @ update stack arguments
+ .endif
+ ldrcc pc, [\table, \nr, lsl #2] @ call sys_* routine
+#endif
+ .endm
+
/*
* These are the registers used in the syscall handler, and allow us to
* have in theory up to 7 arguments to a function - r0 to r6.
```
>[1 Click and see details.](http://lkml.iu.edu/hypermail/linux/kernel/1811.2/07047.html)
>[2 Click and see details.](https://lore.kernel.org/patchwork/patch/1000781/)

### invalid instruction

```text 
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/kernel/entry-common.S:519:3: error: invalid instruction
  stmloia sp, {r5, r6} @ shuffle args
  ^
```

##### solutions

>Use unified assembler in assembly files. Update stmloia to stmialo.
>Same to stmneia, ldrneb, ldreqb, strneb, eoreqs, stmeqia, rsbccs, ldmccia, stmccia
>strnebt, ldmgtia, ldmeqia, sbcnes, adcnes, ldrneh, etc.
>[Click and see details.](https://lore.kernel.org/patchwork/patch/1040350/) BYW, patches in 
>this link are not complete.

###  too many positional arguments

```text
<instantiation>:40:47: error: too many positional arguments
  str8w r0, r3, r4, r5, r6, r7, r8, r9, ip, , abort=19f
                                              ^
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/lib/copy_template.S:247:5: note: while in macro instantiation
18: forward_copy_shift pull=24 push=8
    ^
```

##### solutions

>Remove `,`.
>[Click and see detials.](https://lkml.org/lkml/2019/1/3/545)

###  invalid instruction

```text
<instantiation>:5:2: error: invalid instruction, did you mean: str, strb, strd, strh, strt, trap?
 stralt r3, [r0], #4
 ^
<instantiation>:1:1: note: while in macro instantiation
.rept 1
^
<instantiation>:1:1: note: while in macro instantiation
usracc str, r3, r0, 4, al, 1, 21f
^
<instantiation>:1:1: note: while in macro instantiation
strusr r3, r0, 4, abort=21f
^
<instantiation>:54:3: note: while in macro instantiation
  str1w r0, r3, abort=21f
  ^
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/lib/copy_template.S:247:5: note: while in macro instantiation
18: forward_copy_shift pull=24 push=8
    ^
```

##### solutions

>Just like above, stralt -> strtal.
>[Click and see details.](https://lkml.org/lkml/2019/2/12/1037)

### invalid instruction

```text
<instantiation>:1:1: error: invalid instruction, did you mean: ldrb?
ldralb lr, [r1], #1
^
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/lib/copy_template.S:162:3: note: while in macro instantiation
  ldr1b r1, lr, abort=21f
  ^
```

##### solutions

>Just like above, ldralb -> ldrbal.
>[Click and see details.](https://patchwork.kernel.org/patch/10808639/)

### instruction 'subge' can not set flags 

```text
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/boot/compressed/lib1funcs.S:185:2: error: instruction 'subge' can not set flags, but 's' suffix specified
 subges r2, r2, #4
 ^
/tmp/lib1funcs-8af47e.s:474:2: note: while in macro instantiation
 ARM_MOD_BODY r0, r1, r2, r3
 ^
```

##### solutions

>just like above, subges -> subsge.

###  operand must be a register in range [r0, r14] or apsr_nzcv

```text
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/boot/compressed/head.S:1150:16: error: operand must be a register in range [r0, r14] or apsr_nzcv
1: mrc p15, 0, r15, c7, c14, 3 @ test,clean,invalidate D cache
               ^
```

##### solutions

>LLVM's integrated assembler does not accept r15 as mrc operand.
>[Click and see details.](https://lkml.org/lkml/2019/11/1/717)

### parameter references not allowed in naked functions

```text
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/mm/copypage-v4wb.c:47:9: error: parameter references not allowed in naked functions
        : "r" (kto), "r" (kfrom), "I" (PAGE_SIZE / 64));
               ^
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/mm/copypage-v4wb.c:25:13: note: attribute is here
static void __naked
            ^
/home/liuqiang/Desktop/linux-3.18.20/include/linux/compiler-gcc.h:80:35: note: expanded from macro '__naked'
#define __naked                         __attribute__((naked)) noinline __noclone notrace
                                                       ^
1 error generated.
```

##### solutions

>[Click and see details.](https://lkml.org/lkml/2018/10/16/104)

### expected string in directive

```text
/home/liuqiang/Desktop/linux-3.18.20/arch/arm/mm/proc-arm926.S:477:30: error: expected string in directive
 .section ".proc.info.init", #alloc, #execinstr
```

##### solutions

>Replace Sun/Solaris style flag on section directive.
>[Click and see details.](https://lkml.org/lkml/2019/10/30/807)
