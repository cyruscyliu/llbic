### invalid instruction

```text
/root/linux-3.18.20/arch/arm/kernel/entry-common.S:475:2: error: invalid instruction
 ldmccia r1, {r0 - r6} @ have to reload r0 - r6
 ^
/root/linux-3.18.20/arch/arm/kernel/entry-common.S:476:2: error: invalid instruction
 stmccia sp, {r4, r5} @ and update the stack args
 ^
/root/linux-3.18.20/arch/arm/kernel/entry-common.S:523:3: error: invalid instruction
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
/root/linux-3.18.20/arch/arm/kernel/entry-common.S:519:3: error: invalid instruction
  stmloia sp, {r5, r6} @ shuffle args
  ^
```

##### solutions

>Use unified assembler in assembly files. Update stmloia to stmialo.
>Same to stmneia, ldrneb, ldreqb, strneb, eoreqs, stmeqia, rsbccs, ldmccia, stmccia
>strnebt, ldmgtia, ldmeqia, sbcnes, adcnes, ldrneh, etc.
>[Click and see details.](https://lore.kernel.org/patchwork/patch/1040350/) BYW, patches in 
>this link are not complete.

```shell script
find ./arch/arm -name "*.[hSc]" -exec sed -i -r "s/^((\s*[._a-zA-Z0-9]*[\:\(])?\s*)([a-z]{3})(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)([a-z]{1,2})(\s)/\1\3\5\4\6/" {} \;
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/copy_from_user.S
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/copy_to_user.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)bt/\\\\instr\\\\\(\)bt\\\\cond/" arch/arm/include/asm/assembler.h 
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)t/\\\\instr\\\\\(\)t\\\\cond/" arch/arm/include/asm/assembler.h 
sed -i -r "s/strneb/strbne/" arch/arm/lib/testclearbit.S
sed -i -r "s/streqb/strbeq/" arch/arm/lib/testsetbit.S
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
/root/linux-3.18.20/arch/arm/lib/copy_template.S:247:5: note: while in macro instantiation
18: forward_copy_shift pull=24 push=8
    ^
```

##### solutions

>Remove `,`.
>[Click and see detials.](https://lkml.org/lkml/2019/1/3/545)

```shell script
sed -i -r "s/r0, r3, r4, r5, r6, r7, r8, r9, ip, , abort=19f/r0, r3, r4, r5, r6, r7, r8, r9, ip, abort=19f/" arch/arm/lib/copy_template.S
```

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
/root/linux-3.18.20/arch/arm/lib/copy_template.S:247:5: note: while in macro instantiation
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
/root/linux-3.18.20/arch/arm/lib/copy_template.S:162:3: note: while in macro instantiation
  ldr1b r1, lr, abort=21f
  ^
```

##### solutions

>Just like above, ldralb -> ldrbal.
>[Click and see details.](https://patchwork.kernel.org/patch/10808639/)

### instruction 'subge' can not set flags 

```text
/root/linux-3.18.20/arch/arm/boot/compressed/lib1funcs.S:185:2: error: instruction 'subge' can not set flags, but 's' suffix specified
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
/root/linux-3.18.20/arch/arm/boot/compressed/head.S:1150:16: error: operand must be a register in range [r0, r14] or apsr_nzcv
1: mrc p15, 0, r15, c7, c14, 3 @ test,clean,invalidate D cache
               ^
```

##### solutions

>LLVM's integrated assembler does not accept r15 as mrc operand.
>[Click and see details.](https://lkml.org/lkml/2019/11/1/717)

### parameter references not allowed in naked functions

```text
/root/linux-3.18.20/arch/arm/mm/copypage-v4wb.c:47:9: error: parameter references not allowed in naked functions
        : "r" (kto), "r" (kfrom), "I" (PAGE_SIZE / 64));
               ^
/root/linux-3.18.20/arch/arm/mm/copypage-v4wb.c:25:13: note: attribute is here
static void __naked
            ^
/root/linux-3.18.20/include/linux/compiler-gcc.h:80:35: note: expanded from macro '__naked'
#define __naked                         __attribute__((naked)) noinline __noclone notrace
                                                       ^
1 error generated.
```

##### solutions

>[Click and see details.](https://lkml.org/lkml/2018/10/16/104)

### expected string in directive

```text
/root/linux-3.18.20/arch/arm/mm/proc-arm926.S:477:30: error: expected string in directive
 .section ".proc.info.init", #alloc, #execinstr
```

```shell script
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/mm/proc-arm926.S
```

##### solutions

>Replace Sun/Solaris style flag on section directive.
>[Click and see details.](https://lkml.org/lkml/2019/10/30/807)

### unexpected token at start of statement error

```text
/home/someone/linux-3.18.20/kernel/bounds.c:18:2: error: unexpected token at start of statement
        DEFINE(NR_PAGEFLAGS, __NR_PAGEFLAGS);
        ^
/home/someone/linux-3.18.20/include/linux/kbuild.h:5:25: note: expanded from macro 'DEFINE'
        asm volatile("\n->" #sym " %0 " #val : : "i" (val))
                        ^
<inline asm>:2:1: note: instantiated into assembly here
->NR_PAGEFLAGS 22 __NR_PAGEFLAGS
^
```

##### solutions: 

>KBuild abuses the asm statement to write to a file and clang chokes about these invalid asm statements. Hack it even more by fooling this is actual valid asm code. 
>[Click and see details](https://blog.geekofia.in/android/patches/2019/05/20/unexpected-token-at-start-of-statement-patch.html).

```shell script
sed -i -r "s/asm volatile\(\"\\\\n->\" #sym \" %0 \" #val : : \"i\" \(val\)\)/asm volatile\(\"\\\\n\.ascii \\\\\"->\" #sym \" %0 \" #val \"\\\\\"\" : : \"i\" \(val\)\)/" include/linux/kbuild.h
sed -i -r "s/asm volatile\(\"\\\\n->\" : : \)/asm volatile\(\"\\\\n\.ascii \\\\\"->\" : : \)/" include/linux/kbuild.h
sed -i -r "s/asm volatile\(\"\\\\n->#\" x\)/asm volatile\(\"\\\\n\.ascii \\\\\"->#\" x \"\\\\\"\"\)/" include/linux/kbuild.h
sed -i -r "/\"\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/i\ \ \ \ \"s:\[\[:space:\]\]\*\\\\\.ascii\[\[:space:]]\*\\\\\"\\\\\(\.\*\\\\\)\\\\\":\\\\1:; \\\\" Kbuild
sed -i -r "s/\"\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/" Kbuild
```

### unsupported inline asm: input with type '__be32' (aka 'unsigned int') matching output with type 'unsigned short'

```text
In file included from /home/someone/linux-3.18.20/kernel/cred.c:17:
In file included from /home/someone/linux-3.18.20/include/linux/init_task.h:15:
In file included from /home/someone/linux-3.18.20/include/net/net_namespace.h:22:
In file included from /home/someone/linux-3.18.20/include/net/netns/netfilter.h:5:
In file included from /home/someone/linux-3.18.20/include/linux/netfilter.h:5:
In file included from /home/someone/linux-3.18.20/include/linux/skbuff.h:29:
In file included from /home/someone/linux-3.18.20/include/net/checksum.h:26:
/home/someone/linux-3.18.20/arch/mips/include/asm/checksum.h:285:27: error: unsupported inline asm: input with type '__be32' (aka 'unsigned int') matching output with type 'unsigned short'
          "0" (htonl(len)), "1" (htonl(proto)), "r" (sum));
                                 ^~~~~~~~~~~~
/home/someone/linux-3.18.20/include/linux/byteorder/generic.h:138:18: note: expanded from macro 'htonl'
#define htonl(x) ___htonl(x)
                 ^~~~~~~~~~~
/home/someone/linux-3.18.20/include/linux/byteorder/generic.h:133:21: note: expanded from macro '___htonl'
#define ___htonl(x) __cpu_to_be32(x)
                    ^~~~~~~~~~~~~~~~
/home/someone/linux-3.18.20/include/uapi/linux/byteorder/little_endian.h:38:26: note: expanded from macro '__cpu_to_be32'
#define __cpu_to_be32(x) ((__force __be32)__swab32((x)))
                         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1 error generated.
```

##### solutions

>[Click and see details.](https://www.linux-mips.org/archives/linux-mips/2015-02/msg00185.html)

```shell script
sed -i -r "/csum_ipv6_magic\(const struct in6_addr \*saddr,/{N;N;N;N;s/$/\n\t__wsum tmp;\n/}" arch/mips/include/asm/checksum.h
sed -i -r "s/: \"=r\" \(sum\), \"=r\" \(proto\)/: \"=\&r\" \(sum\), \"=\&r\" \(tmp\)/" arch/mips/include/asm/checksum.h
sed -i -r "s/\"0\" \(htonl\(len\)\), \"1\" \(htonl\(proto\)\), \"r\" \(sum\)\);/\"0\" \(htonl\(len\)\), \"r\" \(htonl\(proto\)\), \"r\" \(sum\)\);/" arch/mips/include/asm/checksum.h
```

### macro defined with named parameters which are not used in macro body, possible positional parameter found in body which will have no effect

```text
/home/someone/linux-3.18.20/arch/mips/include/asm/asmmacro.h:23:2: warning: macro defined with named parameters which are not used in macro body, possible positional parameter found in body which will have no effect
 .macro local_irq_enable reg=$8
```

##### solutions

>Remove all unused macro argument reg=to.
>[Click and see details.](https://github.com/Fuzion24/LLVM-Linux-Kernel/blob/74a384cc891239b953e545532a31df7f3c1d8f88/arch/mips/patches/mips-ias-remove-unused-macro-args.patch)

### expected STT_<TYPE_IN_UPPER_CASE>, '#<type>', '@<type>', '%<type>' or "<type>"

```text
/home/someone/linux-3.18.20/arch/mips/kernel/r4k_fpu.S:273:22: error: expected STT_<TYPE_IN_UPPER_CASE>, '#<type>', '@<type>', '%<type>' or "<type>"
 .type fault@function
                     ^
```

##### solutions

>should be .type fault,@function
>[Click and see details.](https://sourceware.org/binutils/docs/as/Type.html#Type)

```shell script
grep fault@function -rl arch/mips | xargs -l sed -i -r "s/fault@function/fault,@function/"
```

### error: unknown instruction

```text
<instantiation>:6:2: error: unknown instruction
 __BUILD_clear_ade
 ^
<instantiation>:1:1: note: while in macro instantiation
__BUILD_HANDLER adel ade ade silent _int
^
/tmp/genex-6aae5c.s:1217:2: note: while in macro instantiation
 BUILD_HANDLER adel ade ade silent
 ^
```

##### solutions

>macro name is case sensitive
>[Click and see details.](https://source.puri.sm/Librem5/linux-emcraft/commit/158d3b2ad18ca4570c9929b9b31d298d86fa2c02)

```shell script
sed -i -r "s/__BUILD_clear_\\\\clear/__build_clear_\\\\clear/" arch/mips/kernel/genex.S
```

### unexpected token ,expected comma

```text
/home/someone/linux-3.18.20/arch/mips/kernel/entry.S:170:25: error: unexpected token, expected comma
 .set MIPS_ISA_LEVEL_RAW
                        ^
```

##### solutions

>MIPS_ISA_LEVEL_RAM is not defined, delete this line

```shell script
sed -i -r "/MIPS_ISA_LEVEL_RAW/d" arch/mips/kernel/entry.S
```

### cast to union type from type 'unsigned short' not present in union

```text
/home/someone/linux-3.18.20/arch/mips/kernel/branch.c:38:8: error: cast to union type from type 'unsigned short' not present in union
                if (((union mips16e_instruction)inst).ri.opcode
                     ^                          ~~~~
1 error generated.
```

##### solutions

>Remove a cast to the 'mips16e_instruction' union inside an if
condition and instead do an assignment to a local
'union mips16e_instruction' variable's 'full' member before the if
statement and use this variable in the if condition.
>[Click and see details.](https://github.com/Fuzion24/LLVM-Linux-Kernel/blob/master/arch/mips/patches/ARCHIVE/mips-fix-cast-to-type-not-present-in-union.patch)

```shell script
sed -i -r "/if \(cpu_has_mips16\)/{n;N;d}" arch/mips/kernel/branch.c
sed -i -r "/if \(cpu_has_mips16\)/a\\\t\tunion mips16e_instruction inst_mips16e;\n\n\t\tinst_mips16e.full = inst;\n\t\tif (inst_mips16e.ri.opcode == MIPS16e_jal_op\)" arch/mips/kernel/branch.c
```
