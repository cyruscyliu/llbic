# overview 

+ specific `mips` `3.18.20`
+ buildable kernel `linux-3.18.20 patched by OpenWrt`
+ toolchains `mips-openwrt-linux-`
+ patch `linux-3.18.20.sh`

# issues

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
grep fault@function -rl | xargs -l sed -i -r "s/fault@function/fault,@function/"
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
