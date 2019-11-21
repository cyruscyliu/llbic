FROM ubuntu:16.04

USER root
WORKDIR /home/root

COPY sources.list /etc/apt/sources.list
RUN apt-get update && apt-get install -y build-essential wget
RUN apt-get install -y lsb-core software-properties-common
RUN wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && ./llvm.sh 9
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt install -y python3.7 && \
apt install -y python3-pip && python3.7 -m pip install --upgrade pip
RUN rm /usr/bin/python && ln -s /usr/bin/python3.7 /usr/bin/python && \
ln -s /usr/bin/pip3.7 /usr/bin/pip
RUN pip install networkx
RUN ln -s /mnt/llbic llbic && ln -s /mnt/llbic/build build
