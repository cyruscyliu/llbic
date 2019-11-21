FROM ubuntu:16.04

USER root
WORKDIR /home/root

RUN apt-get update && apt-get install -y build-essential wget
RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key|sudo apt-key add - && apt-get install -y clang-8 lldb-8 lld-8
RUN ln -s /mnt/llbic llbic && ln -s /mnt/llbic/build build
