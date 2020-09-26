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
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/mm/proc-feroceon.S
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/boot/compressed/head.S
sed -i -r "s/#alloc/\ \"a\"/" arch/arm/boot/compressed/piggy.S
sed -i -r "s/#alloc/\ \"a\"/" arch/arm/boot/compressed/piggy.lzma.S
sed -i -r "/^struct shash_alg/i\#define SHASH_DESC_ON_STACK\(shash, ctx\) \\\\\n\tchar __##shash##_desc\[sizeof\(struct shash_desc\) \+ \\\\\n\t\tcrypto_shash_descsize\(ctx\)\] CRYPTO_MINALIGN_ATTR; \\\\\n\tstruct shash_desc \*shash = \(struct shash_desc \*\)__##shash##_desc\n" include/crypto/hash.h
sed -i -r "/crc32c\(u32 crc, const void \*address, unsigned int length\)/{n;n;N;N;N;d}" lib/libcrc32c.c
sed -i -r "/crc32c\(u32 crc, const void \*address, unsigned int length\)/{N;s/$/\n\tSHASH_DESC_ON_STACK\(shash, tfm\);\n\tu32 \*ctx = \(u32 \*\)shash_desc_ctx\(shash\);/}" lib/libcrc32c.c
sed -i -r "s/desc\.shash\.tfm = tfm;/shash->tfm = tfm;/" lib/libcrc32c.c
sed -i -r "s/desc\.shash\.flags = 0;/shash->flags = 0;/" lib/libcrc32c.c
sed -i -r "s/\*\(u32 \*\)desc\.ctx = crc;/\*ctx = crc;/" lib/libcrc32c.c
sed -i -r "s/err = crypto_shash_update\(\&desc\.shash, address, length\);/err = crypto_shash_update\(shash, address, length\);/" lib/libcrc32c.c
sed -i -r "s/return \*\(u32 \*\)desc\.ctx;/return \*ctx;/" lib/libcrc32c.c
sed -i -r "/struct crypto_shash \*hash = ctx->hash;/{n;N;N;N;d}" crypto/hmac.c
sed -i -r "/struct crypto_shash \*hash = ctx->hash;/a\\\tSHASH_DESC_ON_STACK\(shash, hash\);" crypto/hmac.c
sed -i -r "s/desc\.shash\.tfm = hash;/shash->tfm = hash;/" crypto/hmac.c
sed -i -r "s/desc\.shash\.flags = crypto_shash/shash->flags = crypto_shash/" crypto/hmac.c
sed -i -r "s/err = crypto_shash_digest\(\&desc\.shash, inkey, keylen, ipad\);/err = crypto_shash_digest\(shash, inkey, keylen, ipad\);/" crypto/hmac.c
sed -i -r "s/\&desc\.shash/shash/" crypto/hmac.c
sed -i -r "/do \{/{n;N;N;N;d}" crypto/testmgr.c
sed -i -r "/do \{/a\\\t\tSHASH_DESC_ON_STACK\(shash, tfm\);" crypto/testmgr.c
sed -i -r "s/sdesc\.shash\.tfm = tfm;/shash->tfm = tfm;/" crypto/testmgr.c
sed -i -r "s/sdesc\.shash\.flags = 0;/shash->flags = 0;/" crypto/testmgr.c
sed -i -r "/\*\(u32 \*\)sdesc\.ctx = le32/i\\\t\tu32 \*ctx = \(u32 \*\)\(\(unsigned long\)\(__shash_desc\n\t\t\t\t+ sizeof\(struct shash_desc\) + CRYPTO_MINALIGN - 1\)\n\t\t\t\t\& ~\(CRYPTO_MINALIGN -1\)\);" crypto/testmgr.c
sed -i -r "s/\*\(u32 \*\)sdesc\.ctx = le32/\*ctx = le32/" crypto/testmgr.c
sed -i -r "s/err = crypto_shash_final\(\&sdesc\.shash/err = crypto_shash_final\(shash/" crypto/testmgr.c
sed -i -r "s/p15, 0, r15, c7, c14, 3/p15, 0, APSR_nzcv, c7, c14, 3/" arch/arm/boot/compressed/head.S
sed -i -r "s/defined\(@val\)/@val/" kernel/timeconst.pl
