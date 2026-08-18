#!/bin/bash
#SBATCH --job-name=deva_5k89_his3asp_dimer_v5
#SBATCH --partition=gpu
#SBATCH --nodelist=slurm017
#SBATCH --time=01:00:00
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/deva_5k89_his3asp_dimer_v5_%j.out
#SBATCH --error=logs/deva_5k89_his3asp_dimer_v5_%j.err

# Activate conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate deva_env

# Move to project directory
cd ~/metal_binding_project/dEVA

# Fix pytorch cache path
export PYTORCH_KERNEL_CACHE_PATH=~/metal_binding_project/dEVA/.pytorch_cache
mkdir -p ~/metal_binding_project/dEVA/.pytorch_cache

echo "=== Running 5K89 His3Asp site | Gen50/Ind2 ==="
echo "Start: $(date)"
python run.py --config configs/5k89_his3asp.yml --models seq_model metal3d_model
echo "End: $(date)"
echo "=== Run complete ==="