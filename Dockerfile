FROM ubuntu:18.04

USER root

RUN apt-get update 
RUN apt-get install -y build-essential wget \
      lsb-core software-properties-common
RUN apt-get install -y clang-6.0 && \
      ln -s /usr/bin/llvm-config-6.0 /usr/bin/llvm-config
RUN apt-get install -y python3 python3-pip && \
      python3 -m pip install --upgrade pip && \
      pip3 install networkx graphviz && \
      ln -sf /usr/bin/python3 /usr/bin/python
