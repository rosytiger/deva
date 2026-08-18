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

orig = get_ca_list("inputs/4ETO.pdb")
new  = get_ca_list("outputs/4eto_zinc_split_v6/packed/4ETO_s0_gen11_ind0.pdb")

orig_A = [x for x in orig if x[0] == 'A']
orig_B = [x for x in orig if x[0] == 'B']
new_A  = [x for x in new  if x[0] == 'A']
new_B  = [x for x in new  if x[0] == 'B']

print(f"orig chain A count: {len(orig_A)}, new chain A count: {len(new_A)}")
print(f"orig chain B count: {len(orig_B)}, new chain B count: {len(new_B)}")
print()

targets = [('A', 17), ('A', 27), ('A', 87), ('A', 91), ('A', 88),
           ('B', 17), ('B', 27), ('B', 87), ('B', 91), ('B', 26)]

for chain, resi in targets:
    orig_list = orig_A if chain == 'A' else orig_B
    new_list  = new_A  if chain == 'A' else new_B
    idx = next((i for i, (c, r, n) in enumerate(orig_list) if r == resi), None)
    if idx is None:
        print(f"{chain}{resi}: not found in original chain {chain}")
        continue
    orig_resn = orig_list[idx][2]
    if idx < len(new_list):
        new_resn = new_list[idx][2]
        new_num = new_list[idx][1]
        print(f"{chain}{resi} (orig={orig_resn}) -> ordinal position {idx} in new file = resi {new_num} ({new_resn})")
    else:
        print(f"{chain}{resi} (orig={orig_resn}) -> OUT OF RANGE (only {len(new_list)} residues)")
