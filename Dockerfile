FROM ubuntu:20.04
LABEL author="Rodrigo Martin <contact@rodrigomartin.dev>"

ENV PATH=$PATH:$HOME/bin
ARG DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    python3 \
    python3-pip \
    git \
    wget \
    samtools \
    biobambam2 \
    bwa


RUN mkdir $HOME/bin

# art_illumina
RUN wget https://www.niehs.nih.gov/research/resources/assets/docs/artbinmountrainier2016.06.05linux64.tgz
RUN tar -xvzf artbinmountrainier2016.06.05linux64.tgz
RUN cp art_bin_MountRainier/art_illumina $HOME/bin

RUN export PATH=$PATH:$HOME/bin

RUN git clone --recurse-submodules --remote-submodules https://github.com/Rapsssito/fasta2bam
