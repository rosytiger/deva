def get_ca_list(path):
    lst = []
    with open(path) as f:
        for line in f:
            if line.startswith("ATOM"):
                name = line[12:16].strip()
                if name == "CA":
                    chain = line[21]
                    resi = int(line[22:26])
                    resn = line[17:20].strip()
                    lst.append((chain, resi, resn))
    return lst

orig = get_ca_list("inputs/5k89_dEVA.pdb")
new  = get_ca_list("outputs/5k89_hisasp_v3/packed/5k89_dEVA_s0_gen40_ind1.pdb")

orig_A = [x for x in orig if x[0] == 'A']
orig_H = [x for x in orig if x[0] == 'H']
new_A = [x for x in new if x[0] == 'A']

print(f"orig chain A count: {len(orig_A)}, new chain A count: {len(new_A)}")
print(f"orig chain H count: {len(orig_H)}")
print()

targets = [('A', 17), ('A', 27), ('H', 87), ('H', 90)]

for chain, resi in targets:
    orig_list = orig_A if chain == 'A' else orig_H
    idx = next((i for i, (c, r, n) in enumerate(orig_list) if r == resi), None)
    if idx is None:
        print(f"{chain}{resi}: not found in original chain {chain}")
        continue
    orig_resn = orig_list[idx][2]
    if chain == 'A':
        if idx < len(new_A):
            new_resn = new_A[idx][2]
            new_num = new_A[idx][1]
            print(f"{chain}{resi} (orig={orig_resn}) -> ordinal position {idx} in new chain A = resi {new_num} ({new_resn})")
        else:
            print(f"{chain}{resi} (orig={orig_resn}) -> OUT OF RANGE in new chain A (only {len(new_A)} residues)")
    else:
        combined_idx = len(orig_A) + idx
        if combined_idx < len(new):
            new_resn = new[combined_idx][2]
            new_chain_actual = new[combined_idx][0]
            new_num = new[combined_idx][1]
            print(f"{chain}{resi} (orig={orig_resn}) -> combined ordinal position {combined_idx} in new file = chain {new_chain_actual} resi {new_num} ({new_resn})")
        else:
            print(f"{chain}{resi} (orig={orig_resn}) -> OUT OF RANGE (only {len(new)} total residues)")
