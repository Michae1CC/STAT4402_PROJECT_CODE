#!/bin/bash
#SBATCH --job-name=aggregate_chem
#SBATCH --output=/home/s4430291/Courses/STAT4402/STAT4402_PROJECT_CODE/data/batch_out/aggregate_chem_out.txt
#SBATCH --error=/home/s4430291/Courses/STAT4402/STAT4402_PROJECT_CODE/data/batch_out/aggregate_chem_err.txt
#SBATCH --time=1-0:00
#SBATCH --mem=30GB
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2

export OMP_NUM_THREADS=2

DATE=$(date +"%Y%m%d%H%M")
echo "time started  "$DATE
echo "This is job '$SLURM_JOB_NAME' (id: $SLURM_JOB_ID) running on the following nodes:"
echo $SLURM_NODELIST
echo "running with SLURM_TASKS_PER_NODE= $SLURM_TASKS_PER_NODE "
echo "running with SLURM_NTASKS total  = $SLURM_NTASKS "
export TIMEFORMAT="%E sec"

python3.6 /home/s4430291/Courses/STAT4402/STAT4402_PROJECT_CODE/src_data/aggregate_data.py

DATE=$(date +"%Y%m%d%H%M")
echo "time finished "$DATE