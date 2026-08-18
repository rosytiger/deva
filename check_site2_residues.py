#!/usr/bin/env python3
"""
Checks what amino acid actually ended up at each Site 2 target position
(A83, A87, C20, C30) in dEVA's packed/designed PDB output files.

Usage:
    python check_site2_residues.py outputs/4ggf_vanadium/packed/
"""

import sys
import os
import glob

# Site 2 target positions: (chain, resnum, expected_residue)
TARGETS = [
    ("A", 83, "HIS"),
    ("A", 87, "HIS"),
    ("C", 20, "HIS"),
    ("C", 30, "ASP"),
]


def get_residue_at(pdb_path, chain, resnum):
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith("ATOM"):
                continue
            atom_name = line[12:16].strip()
            if atom_name != "CA":
                continue
            line_chain = line[21].strip()
            try:
                line_resnum = int(line[22:26].strip())
            except ValueError:
                continue
            if line_chain == chain and line_resnum == resnum:
                return line[17:20].strip()
    return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_site2_residues.py <packed_pdb_directory>")
        sys.exit(1)

    packed_dir = sys.argv[1]
    pdb_files = sorted(glob.glob(os.path.join(packed_dir, "*.pdb")))

    if not pdb_files:
        print(f"No PDB files found in {packed_dir}")
        return

    print(f"{'File':<35}", end="")
    for chain, resnum, expected in TARGETS:
        print(f"{chain}{resnum}(exp {expected[:1]}){'':<3}", end="")
    print()
    print("-" * 90)

    for pdb_path in pdb_files:
        fname = os.path.basename(pdb_path)
        print(f"{fname:<35}", end="")
        for chain, resnum, expected in TARGETS:
            actual = get_residue_at(pdb_path, chain, resnum)
            match = "OK" if actual == expected else ("--" if actual is None else "X")
            print(f"{str(actual):<6}{match:<4}", end="")
        print()


if __name__ == "__main__":
    main()
