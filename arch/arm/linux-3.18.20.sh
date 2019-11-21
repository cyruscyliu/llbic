find ./arch/arm -name "*.[hSc]" -exec sed -i -r "s/^((\s*[._a-zA-Z0-9]*[\:\(])?\s*)([a-z]{3})(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)([a-z]{1,2})(\s)/\1\3\5\4\6/" {} \;
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/copy_from_user.S
sed -i -r "s/str\\\\cond\\\\\(\)b/strb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/copy_to_user.S
sed -i -r "s/ldr\\\\cond\\\\\(\)b/ldrb\\\\cond/" arch/arm/lib/memcpy.S
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)bt/\\\\instr\\\\\(\)bt\\\\cond/" arch/arm/include/asm/assembler.h 
sed -i -r "s/\\\\instr\\\\cond\\\\\(\)t/\\\\instr\\\\\(\)t\\\\cond/" arch/arm/include/asm/assembler.h 
sed -i -r "s/strneb/strbne/" arch/arm/lib/testclearbit.S
sed -i -r "s/streqb/strbeq/" arch/arm/lib/testsetbit.S
sed -i -r "s/lenhgt/length/" arch/arm/mm/mmu.c
sed -i -r "s/sigdne/signed/" arch/arm/mm/alignment.c
sed -i -r "s/sigdne/signed/" arch/arm/kernel/ptrace.c
sed -i -r "s/r0, r3, r4, r5, r6, r7, r8, r9, ip, , abort=19f/r0, r3, r4, r5, r6, r7, r8, r9, ip, abort=19f/" arch/arm/lib/copy_template.S
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/mm/proc-arm926.S
