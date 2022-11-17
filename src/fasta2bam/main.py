# Copyright 2022 - Rodrigo Martin
# GNU GPLv3 License

import argparse
import logging
import random

from sequencing_simulators import run_art_illumina
from aligners import run_bwa_mem


def build_alignment(fasta_input, fasta_ref, coverage, output_path, processes, seed):
    """
    Build an alignment file from a reference FASTA input file.
    """
    fastq_paths = [output_path+'_1.fastq', output_path+'_2.fastq']
    run_art_illumina(fasta_input, coverage, fastq_paths, processes, seed)
    alignment_path = run_bwa_mem(fasta_ref, fastq_paths, output_path, processes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--fasta-input', type=str, required=True, help='Input FASTA file.')
    parser.add_argument('-f', '--fasta-ref', type=str, required=True, help='Reference FASTA file.')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output file.')
    parser.add_argument('-c', '--coverage', type=int, required=True, help='Coverage of the simulated reads.')
    parser.add_argument('-p', '--processes', type=int, default=1, help='Max number of processes.')
    parser.add_argument('-s', '--seed', type=int, default=random.randint(0, 2**32), help='Random seed.')

    args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level='INFO')

    if not args.output.endswith('.cram') or args.output.endswith('.bam'):
        raise ValueError('Output file must be a BAM or CRAM file.')

    # Set random seed
    random.seed(args.seed)

    # Build reference plain alignment file
    build_alignment(args.fasta_input, args.fasta_ref, args.coverage, args.output, args.processes, args.seed)

    logging.info(f'Successfully built an alignment file from {args.fasta_ref} in {args.output}')
