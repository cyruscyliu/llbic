sed -i -r "s/asm volatile\(\"\\\\n->\" #sym \" %0 \" #val : : \"i\" \(val\)\)/asm volatile\(\"\\\\n\.ascii \\\\\"->\" #sym \" %0 \" #val \"\\\\\"\" : : \"i\" \(val\)\)/" include/linux/kbuild.h
sed -i -r "s/asm volatile\(\"\\\\n->\" : : \)/asm volatile\(\"\\\\n\.ascii \\\\\"->\" : : \)/" include/linux/kbuild.h
sed -i -r "s/asm volatile\(\"\\\\n->#\" x\)/asm volatile\(\"\\\\n\.ascii \\\\\"->#\" x \"\\\\\"\"\)/" include/linux/kbuild.h
sed -i -r "/\"\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/i\ \ \ \ \"s:\[\[:space:\]\]\*\\\\\.ascii\[\[:space:]]\*\\\\\"\\\\\(\.\*\\\\\)\\\\\":\\\\1:; \\\\" Kbuild
sed -i -r "s/\"\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/\/\^->\/\{s:->#\\\\\(\.\*\\\\\):\/\* \\\\1 \*\/:; \\\\/" Kbuild
sed -i -r "/csum_ipv6_magic\(const struct in6_addr \*saddr,/{N;N;N;N;s/$/\n\t__wsum tmp;\n/}" arch/mips/include/asm/checksum.h
sed -i -r "s/: \"=r\" \(sum\), \"=r\" \(proto\)/: \"=\&r\" \(sum\), \"=\&r\" \(tmp\)/" arch/mips/include/asm/checksum.h
sed -i -r "s/\"0\" \(htonl\(len\)\), \"1\" \(htonl\(proto\)\), \"r\" \(sum\)\);/\"0\" \(htonl\(len\)\), \"r\" \(htonl\(proto\)\), \"r\" \(sum\)\);/" arch/mips/include/asm/checksum.h
grep fault@function -rl | xargs -l sed -i -r "s/fault@function/fault,@function/"
sed -i -r "s/__BUILD_clear_\\\\clear/__build_clear_\\\\clear/" arch/mips/kernel/genex.S
sed -i -r "/MIPS_ISA_LEVEL_RAW/d" arch/mips/kernel/entry.S
sed -i -r "/if \(cpu_has_mips16\)/{n;N;d}" arch/mips/kernel/branch.c
sed -i -r "/if \(cpu_has_mips16\)/a\\\t\tunion mips16e_instruction inst_mips16e;\n\n\t\tinst_mips16e.full = inst;\n\t\tif (inst_mips16e.ri.opcode == MIPS16e_jal_op\)" arch/mips/kernel/branch.c
