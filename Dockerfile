FROM ubuntu:16.04

RUN useradd -md /home/llbic llbic && echo 'llbic:llbic' | chpasswd && usermod -aG sudo llbic

USER llbic
WORKDIR /home/llbic
