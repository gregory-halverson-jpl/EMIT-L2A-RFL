#!/bin/bash

#SBATCH --job-name=hls-kings-ravine
#SBATCH --output=logs/hls_kings_ravine_%j.log
#SBATCH --error=logs/hls_kings_ravine_%j.err
#SBATCH --open-mode=append
#SBATCH --time=48:00:00
#SBATCH --mem=2GB
#SBATCH --cpus-per-task=4
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=${USER}@example.com

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate EMITL2ARFL

# Critical for HPC/network filesystems when reading NetCDF/HDF5 files
export HDF5_USE_FILE_LOCKING=FALSE

# Navigate to project directory
cd $HOME/data/EMIT-L2A-RFL

# Run the dataset generation script
echo "Starting EMIT dataset generation"
python -u generate_kings_canyon_timeseries_ravine.py

echo "EMIT dataset generation completed with exit code: $?"
