#!/bin/bash
#SBATCH --job-name=pmpnn_baseline
#SBATCH --output=/home/rjurado1/metal_binding_project/dEVA/logs/baseline_%j.out
#SBATCH --error=/home/rjurado1/metal_binding_project/dEVA/logs/baseline_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00

mkdir -p /home/rjurado1/metal_binding_project/dEVA/logs
mkdir -p /home/rjurado1/metal_binding_project/dEVA/baseline_results

source ~/miniconda3/etc/profile.d/conda.sh
conda activate deva_env

PMPNN_SCRIPT="/home/rjurado1/metal_binding_project/dEVA/ProteinMPNN/protein_mpnn_run.py"
PDB_DIR="/home/rjurado1/metal_binding_project/dEVA/inputs"
OUT_DIR="/home/rjurado1/metal_binding_project/dEVA/baseline_results"

proteins=("4ggf" "2WCB" "1ODB" "3PSR")

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

echo "=== All baseline runs complete ==="
chmod +x run_baseline_proteinmpnn.sh