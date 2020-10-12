#!/bin/bash
#SBATCH --job-name=IR_spec
#SBATCH --output=/home/s4430291/Courses/STAT4402/STAT4402_PROJECT_CODE/data/batch_out/IR_spec_out.txt
#SBATCH --error=/home/s4430291/Courses/STAT4402/STAT4402_PROJECT_CODE/data/batch_out/IR_spec_err.txt
#SBATCH --time=3-0:00
#SBATCH --mem=15GB
#SBATCH --nodes=1
#SBATCH --cpus-per-task=6

export OMP_NUM_THREADS=6

DATE=$(date +"%Y%m%d%H%M")
echo "time started  "$DATE
echo "This is job '$SLURM_JOB_NAME' (id: $SLURM_JOB_ID) running on the following nodes:"
echo $SLURM_NODELIST
echo "running with SLURM_TASKS_PER_NODE= $SLURM_TASKS_PER_NODE "
echo "running with SLURM_NTASKS total  = $SLURM_NTASKS "
export TIMEFORMAT="%E sec"

python3.6 /home/s4430291/Courses/STAT4402/STAT4402_PROJECT_CODE/src_data/jdxread_IR.py

DATE=$(date +"%Y%m%d%H%M")
echo "time finished "$DATE