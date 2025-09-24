#!/bin/bash
#SBATCH --job-name=osda_insertion
#SBATCH --output=job.out
#SBATCH --error=job.err
#SBATCH --partition=short
#SBATCH --account=zeocrystal
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=80
#SBATCH --cpus-per-task=1
#SBATCH --qos=high


source ~/.bashrc

#conda activate DFT
#echo $CONDA_PREFIX

export OMP_NUM_THREADS=1
python 01_submit_rerun.py
