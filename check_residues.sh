#!/bin/bash
PDB="outputs/4eto_zinc_100/packed/4ETO_s0_gen29_ind0.pdb"
for resi in 17 27 87 91; do
  for chain in A B; do
    awk -v r="$resi" -v c="$chain" '
      $0 ~ /^ATOM/ {
        name = substr($0,13,4); gsub(/ /,"",name)
        ch = substr($0,22,1)
        rn = substr($0,23,4)+0
        resn = substr($0,18,3)
        if (name=="CA" && ch==c && rn==r) print c r": " resn
      }
    ' "$PDB"
  done
done
