# LLVM Linux Build Issues Collection

I guess most of you have troubles compiling old Linux kernels with clang,
while the solutions to issues are all over the internet, in a blog,
in commit comments, etc. The project is then aiming to put these solutions
together as a `build issues collection` and a learning material of clang usage.
BTW, `llbic` is short of LLVM Linux Build Issues Collection.

In general, this project will compile and link old Linux kernels in llvm bitcode.


```
+--+   gcc    +-----------+   llbic   +---+
+.c+  ----->  +makeout.txt+  -------> +.bc+
+--+          +-----------+           +---+
```

# Usage

## Docker

### Update volumes in build-docker.yml

For [openwrt-build-docker](), add `path/to/openwrt-build-docker/share:/root/firmware`.

### Create docker and run

```
sudo docker build . -t llbic:latest
sudo docker-compose up -d
sudo docker-compose run llbic /bin/bash
```

## Patch, Compile, and Link

```
# patch your kernel
cp patches/3.18.20/linux-3.18.20.sh $SOURCE
cd $SOURCE && ./linux-3.18.20.sh

# run llbic
cd ~/llbic && make compile && make link && make dependency
```

## Support List
+ linux-2.6.32 [patch](./patches/2.6.32/linux-2.6.32.sh) [documention](./patches/2.6.32/linux-2.6.32.md)
+ linux-3.18.20 [patch](./patches/3.18.20/linux-3.18.20.sh) [documention](./patches/3.18.20/linux-3.18.20.md)
+ linux-4.4.42 [patch](./patches/4.4.42/linux-4.4.42.sh) [documention](./patches/4.4.42/linux-4.4.42.md)
+ linux-4.14.167 [patch](./patches/4.14.167/linux-4.14.167.sh) [documention](./patches/4.14.167/linux-4.14.167.md)

## Others
+ The initial idea was inspired by [dr_checker](https://github.com/ucsb-seclab/dr_checker).
+ [port dr_checker to clang9](./doc/port-dr_checker-2-clang-9.md)
+ Check the [backgroud](./doc/backgroud.md) for WLLVM and LTO.

## Contact

If you have any problems, please fire issues!
