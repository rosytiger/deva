#!/bin/bash
PDB="outputs/4eto_zinc_100/packed/4ETO_s0_gen29_ind0.pdb"
echo "Chains present:"
awk '$0 ~ /^ATOM/ {print substr($0,22,1)}' "$PDB" | sort -u
echo ""
echo "Chain A residue range:"
awk '$0 ~ /^ATOM/ && substr($0,22,1)=="A" {print substr($0,23,4)+0}' "$PDB" | sort -n | uniq | sed -n '1p;$p'
echo ""
echo "Chain B residue range:"
awk '$0 ~ /^ATOM/ && substr($0,22,1)=="B" {print substr($0,23,4)+0}' "$PDB" | sort -n | uniq | sed -n '1p;$p'
