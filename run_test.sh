#!/bin/bash
#SBATCH --job-name=deva_test
#SBATCH --partition=gpu
#SBATCH --nodelist=slurm017
#SBATCH --time=00:30:00
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/test_%j.out
#SBATCH --error=logs/test_%j.err

# Activate conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate deva_env

# Move to project directory
cd ~/metal_binding_project/dEVA

# Fix pytorch cache path
export PYTORCH_KERNEL_CACHE_PATH=~/metal_binding_project/dEVA/.pytorch_cache
mkdir -p ~/metal_binding_project/dEVA/.pytorch_cache

# Run dEVA test on 4GGF only
python run.py --config configs/4ggf_vanadium.yml --models seq_model metal3d_model