#!/bin/bash -l

#SBATCH --partition=debug
#SBATCH --account=desi
#SBATCH --nodes=1
#SBATCH --time=00:15:00
#SBATCH --job-name=dr8

echo Starting slurm script at `date`

# Set TMPDIR to be on the ramdisk
export TMPDIR=/dev/shm

# This must be the same as --nodes above
# 125 x 24 = 3000
nodes=1

# Edison nodes have 24 cores, but hyperthreading enabled.
cpu_per_core=2
node_cores=24

# Number of processes to run per node
node_proc=24

# Compute some parameters to srun
node_thread=$(( node_cores / node_proc ))
node_depth=$(( cpu_per_core * node_thread ))
procs=$(( nodes * node_proc ))

# Assume unthreaded python code
export OMP_NUM_THREADS=1

# NOTE: if using python multiprocessing and not MPI, remove the cpu_bind option
run="srun --cpu_bind=cores -n ${procs} -N ${nodes} -c ${node_depth}"

# Use DESI environment
source /project/projectdirs/desi/software/desi_environment.sh master

# Run it
time ${run} python extract.py

echo done with slurm script at `date`
