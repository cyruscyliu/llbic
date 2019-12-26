FROM ubuntu:16.04

USER root
WORKDIR /home/root

COPY sources.list /etc/apt/sources.list
RUN apt-get update && apt-get install -y build-essential wget
RUN apt-get install -y lsb-core software-properties-common
RUN apt-get install -y vim
RUN wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && ./llvm.sh 9
RUN ln -s /usr/bin/clang-9 /usr/bin/clang && ln -s /usr/bin/llvm-link-9 /usr/bin/llvm-link && ln -s /usr/bin/opt-9 /usr/bin/opt
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt install -y python3.7 && \
apt install -y python3-pip && python3.7 -m pip install --upgrade pip
RUN rm /usr/bin/python && ln -s /usr/bin/python3.7 /usr/bin/python && \
rm /usr/local/bin/pip && ln -s /usr/local/bin/pip3.7 /usr/local/bin/pip
RUN pip install networkx && pip install matplotlib &&  pip install graphviz
RUN ln -s /mnt/llbic llbic && ln -s /mnt/build build
