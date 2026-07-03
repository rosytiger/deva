#!/bin/bash
#SBATCH --job-name=pmpnn_baseline
#SBATCH --output=/home/rjurado1/metal_binding_project/dEVA/logs/baseline_%j.out
#SBATCH --error=/home/rjurado1/metal_binding_project/dEVA/logs/baseline_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00

# Ensure directories exist
mkdir -p /home/rjurado1/metal_binding_project/dEVA/logs
mkdir -p /home/rjurado1/metal_binding_project/dEVA/baseline_results

source activate deva_env 

# Adjust this path based on where you found protein_mpnn_run.py
PMPNN_SCRIPT="/home/rjurado1/metal_binding_project/dEVA/proteinmpnn/protein_mpnn_run.py"
PDB_DIR="/home/rjurado1/metal_binding_project/dEVA/pdbs"
OUT_DIR="/home/rjurado1/metal_binding_project/dEVA/baseline_results"

proteins=("4GGF" "2WCB" "1ODB" "3PSR")

for pdb in "${proteins[@]}"; do
    echo "=== Running $pdb baseline ==="
    python "$PMPNN_SCRIPT" \
        --pdb_path "${PDB_DIR}/${pdb}.pdb" \
        --out_folder "${OUT_DIR}/${pdb}/" \
        --num_seq_per_target 10 \
        --sampling_temp "0.1" \
        --batch_size 1 \
        --model_name v_48_020
done
