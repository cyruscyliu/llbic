export BUILD=/home/root/build
export STAGING_DIR=/home/root/build/staging_dir
cd $BUILD/linux-3.18.20
make ARCH=mips CROSS_COMPILE=$STAGING_DIR/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux- V=1 > makeout.txt 2>&1
cp /home/root/llbic/arch/mips/linux-3.18.20.sh . && ./linux-3.18.20.sh
cd /home/root/llbic
python wrapper.py dr_checker compile $BUILD/linux-3.18.20/makeout.txt mips /usr/bin/clang-9 $STAGING_DIR/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/mips-openwrt-linux-gcc $BUILD/linux-3.18.20/ $BUILD/linux-3.18.20-llvm-bitcode
python wrapper.py dr_checker link $BUILD/linux-3.18.20/makeout.txt /usr/bin/llvm-link-9 $BUILD/linux-3.18.20-llvm-bitcode
