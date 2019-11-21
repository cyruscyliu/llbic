FROM ubuntu:16.04

USER root
WORKDIR /home/root

COPY sources.list /etc/apt/sources.list
RUN apt-get update && apt-get install -y build-essential wget
RUN apt-get install -y lsb-core software-properties-common
RUN wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && ./llvm.sh 9
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt install -y python3.7 && \
apt install -y python3-pip && ln -s /usr/bin/python python3.7 && ln -s /usr/bin/pip pip3.7

RUN ln -s /mnt/llbic llbic && ln -s /mnt/llbic/build build
