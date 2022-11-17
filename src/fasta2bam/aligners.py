# Copyright 2022 - Rodrigo Martin
# GNU GPLv3 License

import os
import subprocess
import logging
import glob


def _index_alignment(alignment_path, max_processes):
    """
    Index an alignment file.
    """
    index_args = ['samtools', 'index', '-@', str(max_processes), alignment_path]
    logging.info(f'Indexing with: {" ".join(index_args)}')
    return subprocess.run(index_args, check=True)


def _sort_alignment_from_aligner(fasta_ref, aligner_output_file, input_format, output_path, max_processes):
    """
    Sort an alignment output.
    """
    tmp_file_prefix = output_path+'bamsormadup_tmp_'
    sort_args = ['bamsormadup', f'inputformat={input_format}', 'outputformat=bam',
                 f'threads={str(max_processes)}', f'tmpfile={tmp_file_prefix}']
    input_file = open(aligner_output_file, 'rb')
    # Translate to cram if needed
    if output_path.endswith('.cram'):
        pre_sort_proc = subprocess.Popen(sort_args + ['level=0'], stdin=input_file, stdout=subprocess.PIPE)
        logging.info(f'Sorting with: {" ".join(pre_sort_proc.args)}')
        cram_args = ['samtools', 'view', '-', '-T', fasta_ref, '-o', output_path, '-@', str(max_processes)]
        logging.info(f'Converting to CRAM with: {" ".join(cram_args)}')
        sort_proc = subprocess.Popen(cram_args, stdin=pre_sort_proc.stdout)
        pre_sort_proc.stdout.close()
    else:
        with open(output_path, 'wb') as f_out:
            sort_proc = subprocess.Popen(sort_args, stdin=input_file, stdout=f_out)
            logging.info(f'Sorting with: {" ".join(sort_proc.args)}')
    sort_proc.communicate()
    # Remove temporal files from bamsormadup
    for tmp_file in glob.glob(tmp_file_prefix+'*'):
        os.remove(tmp_file)
    # Check if the process was successful
    if sort_proc.returncode != 0:
        raise subprocess.CalledProcessError(sort_proc.returncode, " ".join(sort_proc.args))
    # Index the resulting alignment
    _index_alignment(output_path, max_processes)


def run_bwa_mem(fasta_ref, fastq_paths, output_path, max_processes):
    """
    Align a FASTQ file to a reference FASTA file using BWA-MEM and samtools.
    """
    # Call BWA-MEM and samtools
    bwa_args = ['bwa', 'mem', '-Y', '-K', '400000000', '-R', '@RG\\tID:INSILICO\\tSM:NORMAL',
                '-t', str(max_processes), fasta_ref, fastq_paths[0], fastq_paths[1]]
    logging.info(f'Aligning FASTQs with BWA-MEM: {" ".join(bwa_args)}')
    bwa_output_file = output_path+'.bwa.sam'
    bwa_proc = subprocess.Popen(bwa_args, stdout=open(bwa_output_file, 'wb'))
    bwa_proc.communicate()
    for fastq_path in fastq_paths:
        os.remove(fastq_path)
    _sort_alignment_from_aligner(fasta_ref, bwa_output_file, 'sam', output_path, max_processes)
    os.remove(bwa_output_file)
