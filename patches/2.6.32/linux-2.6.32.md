### omit the defined()?

```text
Can't use 'defined(@array)' (Maybe you should just omit the defined()?) at kernel/timeconst.pl line 373.
/home/liuqiang/Desktop/linux-2.6.32/kernel/Makefile:129: recipe for target 'kernel/timeconst.h' failed

change "if (!defined(@array)) {" to "if (!@array) {"
```

```shell script
# fix it before building
sed -i -r "s/defined\(@val\)/@val/" kernel/timeconst.pl
```

# issues

### invalid instruction

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
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/lib/copy_template.S:247:5: note: while in macro instantiation
18: forward_copy_shift lsr=24 lsl=8
    ^
```

##### solutions

>Remove `,`.
>[Click and see detials.](https://lkml.org/lkml/2019/1/3/545)

```shell script
sed -i -r "s/r0, r3, r4, r5, r6, r7, r8, r9, ip, , abort=19f/r0, r3, r4, r5, r6, r7, r8, r9, ip, abort=19f/" arch/arm/lib/copy_template.S
```

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

```shell script
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/mm/proc-feroceon.S
sed -i -r "s/#alloc, #execinstr/\ \"ax\"/" arch/arm/boot/compressed/head.S
sed -i -r "s/#alloc/\ \"a\"/" arch/arm/boot/compressed/piggy.S
```

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
>[Click and see details](https://www.redhat.com/archives/dm-devel/2014-September/msg00110.html) for SHASH_DESC_ON_STACK.  

```shell script
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
```

### operand must be a register in range [r0, r14] or apsr_nzcv

```text 
/home/liuqiang/Desktop/linux-2.6.32/arch/arm/boot/compressed/head.S:946:16: error: operand must be a register in range [r0, r14] or apsr_nzcv
1: mrc p15, 0, r15, c7, c14, 3 @ test,clean,invalidate D cache
               ^
```

##### solutions

>LLVM's integrated assembler does not accept r15 as mrc operand.
>[Click and see details.](https://lkml.org/lkml/2019/11/1/717)

```shell script
sed -i -r "s/p15, 0, r15, c7, c14, 3/p15, 0, APSR_nzcv, c7, c14, 3/" arch/arm/boot/compressed/head.S
```
