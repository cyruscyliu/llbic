# How to add patches?

1. Create a new directory named after the Linux kernel version.

```
mkdir 3.18.20
```

2. Create a patch script.

```
touch linux-3.18.20.sh
```

3. Write patch/sed commands in the patch script.

```
echo sed ... >> linux-3.18.20.sh
echo patch kernel/fork.c xxx.diff >> linux-3.18.20.sh
echo issue_and_soluation >> linux-3.18.20.md # optional
```

P.S.
+ Use relative path for diff patches that are under the same directory with linux-3.18.20.sh
because we will copy the patches to the Linux kernel source directory.
+ Use relative path for files in the Linux kernel because we will
chdir to the Linux kernel source directory.
