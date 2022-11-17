# Copyright 2022 - Rodrigo Martin
# GNU GPLv3 License

import os
import shutil
import subprocess
import logging
from concurrent.futures import ProcessPoolExecutor


def _run_art_illumina_process(process_num, common_args, filename, coverage, seed):
    """
    Run ART-Illumina.
    """
    seed += process_num
    art_illumina_args = common_args + ['-f', str(coverage), '-rs', str(seed), '-o', filename, '--id', f'{process_num}_x{coverage}_']
    subprocess.run(art_illumina_args, check=True, stdout=subprocess.DEVNULL)
    return filename+'1.fq', filename+'2.fq'


def run_art_illumina(fasta_ref, coverage, fastq_paths, max_processes, seed):
    """
    Run ART-Illumina to generate FASTQ files.
    """
    pool = ProcessPoolExecutor(max_workers=max_processes)

    # Split coverage in chunks for parallel processing
    if coverage < max_processes:
        art_processes = coverage
        coverages_per_process = [1] * art_processes
    else:
        art_processes = max_processes
        coverages_per_process = [int(coverage/art_processes)] * art_processes
        remainder = coverage % art_processes
        for i in range(remainder):
            coverages_per_process[i] += 1

    fasta_size = float(os.path.getsize(fasta_ref)) / (1024 * 1024 * 1024)  # GB
    expected_size_per_process = [c*fasta_size*2.25 for c in coverages_per_process]
    logging.info(f'ART-Illumina processes: {art_processes}, with coverages: {coverages_per_process}')

    futures = []
    # Call ART-Illumina
    art_illumina_common_args = ['art_illumina', '-q', '-p', '-na', '-ss', 'HS25', '-l',
                                str(150), '-m', str(500), '-s', str(20), '-i', fasta_ref]
    logging.info(f'Running ART-Illumina with common args: {" ".join(art_illumina_common_args)}')
    for i in range(art_processes):
        process_coverage = coverages_per_process[i]
        tmp_filename = f'{fastq_paths[0]}{str(i)}_x{str(process_coverage)}_out'
        futures.append(pool.submit(_run_art_illumina_process, i,
                       art_illumina_common_args, tmp_filename, process_coverage, seed))

    # Wait for ART-Illumina to finish and concat each process temporal file
    dst_fastq_1 = open(fastq_paths[0], 'w')
    dst_fastq_2 = open(fastq_paths[1], 'w')
    # Invert order
    futures = reversed(futures)
    for future in futures:
        tmp_fastq_1, tmp_fastq_2 = future.result()
        # Concat FASTQ temporal files
        with open(tmp_fastq_1, 'r') as src_fastq:
            shutil.copyfileobj(src_fastq, dst_fastq_1)
        with open(tmp_fastq_2, 'r') as src_fastq:
            shutil.copyfileobj(src_fastq, dst_fastq_2)
        # Remove temporal files
        os.remove(tmp_fastq_1)
        os.remove(tmp_fastq_2)
    dst_fastq_1.close()
    dst_fastq_2.close()
    logging.info(f'Concatenated FASTQ files: {fastq_paths[0]} and {fastq_paths[1]}')

    pool.shutdown()
