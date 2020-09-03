find ./arch/arm -name "*.[hSc]" -exec sed -i -r "s/^((\s*[._a-zA-Z0-9]*[\:\(])?\s*)([a-z]{3})(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)([a-z]{1,2})(\s)/\1\3\5\4\6/" {} \;
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/copy_from_user.S
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/copy_to_user.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)bt/\\\\instr\\\\\(\)bt\\\\cond/" arch/arm/include/asm/assembler.h 
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)t/\\\\instr\\\\\(\)t\\\\cond/" arch/arm/include/asm/assembler.h 
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)b\\\\\(\)/\\\\instr\\\\\(\)b\\\\cond\\\\\(\)/" arch/arm/include/asm/assembler.h 
sed -i -r "s/ldrht/ldrh/" arch/arm/kernel/entry-armv.S
sed -i -r "s/strneb/strbne/" arch/arm/lib/testclearbit.S
sed -i -r "s/streqb/strbeq/" arch/arm/lib/testsetbit.S
sed -i -r "s/lenhgt/length/" arch/arm/mm/mmu.c
sed -i -r "s/sigdne/signed/" arch/arm/mm/alignment.c
sed -i -r "s/sigdne/signed/" arch/arm/kernel/ptrace.c
sed -i -r "s/r0, r3, r4, r5, r6, r7, r8, r9, ip, , abort=19f/r0, r3, r4, r5, r6, r7, r8, r9, ip, abort=19f/" arch/arm/lib/copy_template.S
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/mm/proc-arm926.S
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/mm/proc-v6.S
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/mm/proc-v7.S
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/boot/compressed/head.S
sed -i -r "s/#alloc/\ \"a\"/" arch/arm/boot/compressed/piggy.xzkern.S
# dirty hack of this insn as I didn't find any documented solution
sed -i -r "s/p15, 0, r15, c7, c14, 3/p15, 0, r14, c7, c14, 3/" arch/arm/boot/compressed/head.S
sed -i -r "s/asm volatile\(\"\\\\n->\" #sym \" %0 \" #val : : \"i\" \(val\)\)/asm volatile\(\"\\\\n\.ascii \\\\\"->\" #sym \" %0 \" #val \"\\\\\"\" : : \"i\" \(val\)\)/" include/linux/kbuild.h
sed -i -r "s/asm volatile\(\"\\\\n->\" : : \)/asm volatile\(\"\\\\n\.ascii \\\\\"->\" : : \)/" include/linux/kbuild.h
sed -i -r "s/asm volatile\(\"\\\\n->#\" x\)/asm volatile\(\"\\\\n\.ascii \\\\\"->#\" x \"\\\\\"\"\)/" include/linux/kbuild.h
sed -i -r "/\"\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/i\ \ \ \ \"s:\[\[:space:\]\]\*\\\\\.ascii\[\[:space:]]\*\\\\\"\\\\\(\.\*\\\\\)\\\\\":\\\\1:; \\\\" Kbuild
sed -i -r "s/\"\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/" Kbuild
sed -i -r "/csum_ipv6_magic\(const struct in6_addr \*saddr,/{N;N;N;N;s/$/\n\t__wsum tmp;\n/}" arch/mips/include/asm/checksum.h
sed -i -r "s/: \"=r\" \(sum\), \"=r\" \(proto\)/: \"=\&r\" \(sum\), \"=\&r\" \(tmp\)/" arch/mips/include/asm/checksum.h
sed -i -r "s/\"0\" \(htonl\(len\)\), \"1\" \(htonl\(proto\)\), \"r\" \(sum\)\);/\"0\" \(htonl\(len\)\), \"r\" \(htonl\(proto\)\), \"r\" \(sum\)\);/" arch/mips/include/asm/checksum.h
grep fault@function -rl arch/mips | xargs -l sed -i -r "s/fault@function/fault,@function/"
sed -i -r "s/__BUILD_clear_\\\\clear/__build_clear_\\\\clear/" arch/mips/kernel/genex.S
sed -i -r "/MIPS_ISA_LEVEL_RAW/d" arch/mips/kernel/entry.S
sed -i -r "/if \(cpu_has_mips16\)/{n;N;d}" arch/mips/kernel/branch.c
sed -i -r "/if \(cpu_has_mips16\)/a\\\t\tunion mips16e_instruction inst_mips16e;\n\n\t\tinst_mips16e.full = inst;\n\t\tif (inst_mips16e.ri.opcode == MIPS16e_jal_op\)" arch/mips/kernel/branch.c
