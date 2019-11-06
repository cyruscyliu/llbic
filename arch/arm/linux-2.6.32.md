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
