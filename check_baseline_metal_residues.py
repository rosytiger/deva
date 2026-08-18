#!/usr/bin/env python3
"""
Checks whether ProteinMPNN baseline sequences preserved the His/Asp
metal-coordinating residues at the var_residues positions used in the
dEVA vanadium-binding designs.
"""

import os
from collections import Counter

STRUCTURES = {
    "4ggf": {
        "pdb": "inputs/4ggf.pdb",
        "fa": "baseline_results/4ggf/seqs/4ggf.fa",
        "var_residues": ["A17", "A83", "A87", "C28", "C30"],
    },
    "2WCB": {
        "pdb": "inputs/2WCB.pdb",
        "fa": "baseline_results/2WCB/seqs/2WCB.fa",
        "var_residues": ["B15", "B85", "B89", "B25"],
    },
    "1ODB": {
        "pdb": "inputs/1ODB.pdb",
        "fa": "baseline_results/1ODB/seqs/1ODB.fa",
        "var_residues": ["B15", "B85", "B89", "B25"],
    },
    "3PSR": {
        "pdb": "inputs/3PSR.pdb",
        "fa": "baseline_results/3PSR/seqs/3PSR.fa",
        "var_residues": ["A17", "A86", "A90", "A24"],
    },
}


def parse_chain_resnum_order(pdb_path):
    chain_resnums = {}
    seen = {}
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith("ATOM"):
                continue
            atom_name = line[12:16].strip()
            if atom_name != "CA":
                continue
            chain_id = line[21].strip()
            resnum = int(line[22:26].strip())
            icode = line[26].strip()
            key = (chain_id, resnum, icode)
            if key in seen.setdefault(chain_id, set()):
                continue
            seen[chain_id].add(key)
            chain_resnums.setdefault(chain_id, []).append(resnum)
    return chain_resnums


def build_resnum_to_index(chain_resnums):
    mapping = {}
    for chain_id, resnums in chain_resnums.items():
        mapping[chain_id] = {resnum: i for i, resnum in enumerate(resnums)}
    return mapping


def parse_fa_sequences(fa_path):
    with open(fa_path) as f:
        lines = [l.strip() for l in f if l.strip()]

    records = []
    header = None
    for line in lines:
        if line.startswith(">"):
            header = line
        else:
            records.append((header, line))

    designed = [seq for header, seq in records[1:]]
    return [seq.split("/") for seq in designed]


def get_var_residue_matrix(chain_seqs, resnum_to_index, var_residues):
    result = {}
    for var_res in var_residues:
        chain_id = var_res[0]
        resnum = int(var_res[1:])
        if chain_id not in resnum_to_index:
            result[var_res] = None
            continue
        idx = resnum_to_index[chain_id].get(resnum)
        if idx is None:
            result[var_res] = None
            continue
        try:
            chain_pos = list(resnum_to_index.keys()).index(chain_id)
            seq = chain_seqs[chain_pos]
        except (IndexError, ValueError):
            result[var_res] = None
            continue
        if idx >= len(seq):
            result[var_res] = None
            continue
        result[var_res] = seq[idx]
    return result


def main():
    print(f"{'Structure':<10} {'Position':<10} {'H/D preserved':<15} {'Fraction':<10} {'AA seen (top3)'}")
    print("-" * 70)

    for name, info in STRUCTURES.items():
        pdb_path = info["pdb"]
        fa_path = info["fa"]
        var_residues = info["var_residues"]

        if not os.path.isfile(pdb_path):
            print(f"{name}: PDB not found at {pdb_path}, skipping")
            continue
        if not os.path.isfile(fa_path):
            print(f"{name}: .fa not found at {fa_path}, skipping")
            continue

        chain_resnums = parse_chain_resnum_order(pdb_path)
        resnum_to_index = build_resnum_to_index(chain_resnums)
        designed_seqs = parse_fa_sequences(fa_path)

        if not designed_seqs:
            print(f"{name}: no designed sequences found in {fa_path}")
            continue

        per_position_aa = {vr: [] for vr in var_residues}
        for chain_seqs in designed_seqs:
            aa_map = get_var_residue_matrix(chain_seqs, resnum_to_index, var_residues)
            for vr, aa in aa_map.items():
                per_position_aa[vr].append(aa)

        for vr in var_residues:
            aas = per_position_aa[vr]
            valid = [a for a in aas if a is not None]
            preserved = sum(1 for a in valid if a in ("H", "D"))
            frac = preserved / len(valid) if valid else 0.0
            top = Counter(valid).most_common(3)
            top_str = ", ".join(f"{aa}:{c}" for aa, c in top)
            print(f"{name:<10} {vr:<10} {preserved}/{len(valid):<13} {frac:<10.2f} {top_str}")
        print()


if __name__ == "__main__":
    main()
