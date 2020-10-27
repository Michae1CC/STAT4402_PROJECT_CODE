#!/usr/bin/env python3

__author__ = 'Michael Ciccotosto-Camp'
__version__ = ''

import os
import sys
import csv
import shutil
import socket
import itertools
import argparse

if sys.platform.startswith('win32'):
    ROOT_DIR = os.path.join(
        'D:\\', '2020', 'S2', 'STAT_4402', 'ASSESSMENT', 'STAT4402_PROJECT_CODE')

elif sys.platform.startswith('linux'):
    ROOT_DIR = os.path.join(
        '/', 'home', 's4430291', 'Courses', 'STAT4402', 'STAT4402_PROJECT_CODE')


JOB_TIME = "0-3:00"
JOB_MEM = "16GB"
JOB_NODES = 1
JOB_NTASKS_PER_NODE = 1
JOB_CPUS_PER_TASK = 2

PYTHON_VERSION = "3.6"

JOB_TEMPLATE = """#!/bin/bash
#SBATCH --job-name={file_name}
#SBATCH --output={stdout_file}
#SBATCH --error={stderr_file}
#SBATCH --time={job_time}
#SBATCH --mem={job_mem}
#SBATCH --nodes={job_nodes}
#SBATCH --ntasks-per-node={job_ntasks_per_node}
#SBATCH --cpus-per-task={job_cpus_per_task}

export OMP_NUM_THREADS={job_cpus_per_task}

DATE=$(date +"%Y%m%d%H%M")
echo "time started  "$DATE
echo "This is job '$SLURM_JOB_NAME' (id: $SLURM_JOB_ID) running on the following nodes:"
echo $SLURM_NODELIST
echo "running with SLURM_TASKS_PER_NODE= $SLURM_TASKS_PER_NODE "
echo "running with SLURM_NTASKS total  = $SLURM_NTASKS "
export TIMEFORMAT="%E sec"

python{py_ver_short} -W ignore {python_filepath!r} {param_str}

DATE=$(date +"%Y%m%d%H%M")
echo "time finished "$DATE
"""


def convert_bool_arg(arg_in):
    """
    Converts a boolean command line argument into a python boolean object.

    Parameters:
        arg_in:
            The given command line argument.

    Return:
        The interrupted boolean value of the command line argument.
    """

    false_options = ('f', 'false', '0', 'n', 'no', 'nan', 'none')

    if arg_in.lower() in false_options:
        return False

    return True


class JobCreator:
    "Creates (and possibly runs) job scripts for creating annotated images."

    def __init__(self, slurm_dir: str, param_csv_path: str, submit: bool = False, temp: bool = False, dry_run: bool = False):
        """
        Initializes a job creator.

        Parameters:
            slurm_dir (str):
                A full path to a directory that will hold stdout and stderr of 
                the submitted jobs.

            submit (bool):
                If True the created jobs will be immediately submitted.

            temp (bool):
                An argument to specif if the batch files should only be 
                temporarily held.

            dry_run (bool):
                If True, creates the batch files for the jobs and simulates
                job submission.
        """

        self.slurm_dir = slurm_dir
        self.param_csv_path = param_csv_path

        self.arg1s = ["hi", "hello"]

        # A full path to a directory that will hold the created job files.
        self.output_dir = os.path.join(self.slurm_dir, "batch_scripts")

        self.slurm_out = os.path.join(self.slurm_dir, "batch_out")
        self.slurm_err = os.path.join(self.slurm_dir, "batch_err")

        # Make sure new directories exist
        for folder in [self.output_dir, self.slurm_out, self.slurm_err]:
            if not os.path.exists(folder):
                os.makedirs(folder)

        self.submit = submit
        self.temp = temp
        self.dry_run = dry_run

        self.begin_job_procession()

    def begin_job_procession(self):
        """
        Creates, submits (if requested) and removes (if requested) jobs for
        all the tiles within the project directory.
        """

        # Begin by creating all the required job files
        self.create_job_files()

        # Submit all the created jobs
        if self.submit:
            self.submit_jobs()

        # Delete all the created jobs
        if self.temp:
            self.delete_jobs()

        return

    def create_job_files(self):
        """
        Creates a job files for each tile within the project folder.
        """

        with open(self.param_csv_path, 'r', newline='') as param_csv_file:

            # Open the parameters combination file
            param_reader = csv.DictReader(param_csv_file, delimiter=',')

            for param_id, line_ in enumerate(param_reader, 2):

                # Create a string of all the parameter names with their
                # corresponding parameter values.
                param_str = ' '.join(
                    f'--{param_name} {param_value}' for param_name, param_value in line_.items())

                file_name = f"id_{param_id}"

                stdout_path = os.path.join(
                    self.slurm_out, f"{file_name}_out.txt")
                stderr_path = os.path.join(
                    self.slurm_err, f"{file_name}_err.txt")

                FORMATTED_TEMPLATE = JOB_TEMPLATE.format(
                    py_ver_short=PYTHON_VERSION.rsplit(".", maxsplit=1)[0],
                    file_name=file_name,
                    python_filepath=os.path.join(
                        ROOT_DIR, "src_model", "cluster_auto_params.py"),
                    stdout_file=stdout_path,
                    stderr_file=stderr_path,
                    param_str=param_str,
                    job_time=JOB_TIME,
                    job_mem=JOB_MEM,
                    job_nodes=JOB_NODES,
                    job_ntasks_per_node=JOB_NTASKS_PER_NODE,
                    job_cpus_per_task=JOB_CPUS_PER_TASK
                )

                job_filename = f"{file_name}_job.sh"
                job_path = os.path.join(self.output_dir, job_filename)

                with open(job_path, "w+") as job_file:
                    print(FORMATTED_TEMPLATE, end='',
                          file=job_file, flush=True)

        return

    def submit_jobs(self):
        """
        Submit the jobs via slurm on the current machine.
        """

        # Make a list of all the job files within the output directory
        job_file_list = [filename for filename in os.listdir(
            self.output_dir) if filename.endswith(".sh")]
        # Get the full path to each of the filenames
        job_file_list = list(map(lambda filename: os.path.join(
            self.output_dir, filename), job_file_list))

        job_file_list = sorted(job_file_list)

        # Submit each of the jobs within the job file list
        for job_file in job_file_list:

            if self.dry_run:
                print(f"[DRY RUN] sbatch {job_file}")
            else:
                os.system(f"sbatch {job_file}")

        return

    def delete_jobs(self):
        """
        Deletes all the job files within the output directory.
        """

        shutil.rmtree(self.output_dir)

        return


def main():

    parser = argparse.ArgumentParser(description="Creates (and possibly runs) "
                                     "job scripts for MLP parameter tunning.")

    parser.add_argument('--slurm_dir', type=str, default=os.path.join(ROOT_DIR, "batch", "auto_params"),
                        help='A full path to a directory to create slurm and batch files.')
    parser.add_argument('--param_csv_path', type=str, default=os.path.join(ROOT_DIR, "data", "auto_param.csv"),
                        help='A full path to a files containing all the different parameter settings.')

    parser.add_argument('-s', '--submit', type=convert_bool_arg, default=False, const=True, nargs='?',
                        help='If True the created jobs will be immediately submitted.')
    parser.add_argument('-t', '--temp', type=convert_bool_arg, default=False, const=True, nargs='?',
                        help='If True the created job folder will be deleted immediately after submitting the jobs.')
    parser.add_argument('-d', '--dry_run', type=convert_bool_arg, default=False, const=False, nargs='?',
                        help='If True the created job folder will be deleted immediately after submitting the jobs.')

    args = parser.parse_args()

    JobCreator(args.slurm_dir, args.param_csv_path,
               submit=args.submit, temp=args.temp, dry_run=args.dry_run)


if __name__ == "__main__":

    main()

    exit(0)
