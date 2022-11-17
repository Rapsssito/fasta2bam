# fasta2bam - FASTA to SAM/BAM/CRAM generator<!-- omit in toc -->

fasta2bam is a tool for generating alignment files (SAM/BAM/CRAM) from FASTA files. The tool is written in Python and uses the sequencing simulator `art_illumina` from [ART](https://www.niehs.nih.gov/research/resources/software/biostatistics/art/index.cfm) under the hood to generate the simulated reads from the FASTA file. The tool is provided as a standalone Python script with a command-line interface and is optimized for running in a HPC environment (taking advantage of the processing power of multiple cores).

## Table of contents<!-- omit in toc -->
- [Getting started](#getting-started)
- [Usage](#usage)
- [Scripts](#scripts)
  - [fasta2bam](#fasta2bam)
- [License](#license)

## Getting started

You can build the docker image with the following command:

```bash
docker build -t fasta2bam .
```

## Usage

Following is an example of how to generate two 30X CRAM files from a reference genome in a 16-core machine:
```
python3 -O src/fasta2bam/main.py -i ref.fa -f ref.fa -c 30 -p 16 -o normal_30X.cram -s 0
python3 -O src/fasta2bam/main.py -i ref.fa -f ref.fa -c 30 -p 16 -o normal_2_30X.cram -s 564
```

## Scripts
### fasta2bam
Its source code can be found in the [src/fasta2bam](src/fasta2bam) directory.

#### Dependencies<!-- omit in toc -->
The following programs must be installed and available in the PATH:
* [SAMtools](http://www.htslib.org/)
* [BWA-MEM](https://github.com/lh3/bwa)
* [biobambam2](https://gitlab.com/german.tischler/biobambam2)
* `art_illumina` from [ART](https://www.niehs.nih.gov/research/resources/software/biostatistics/art/index.cfm)

## License

This project is licensed under the terms of the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
