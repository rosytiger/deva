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
orig_A = [x for x in orig if x[0] == 'A']
orig_B = [x for x in orig if x[0] == 'B']

# find ordinal index of A90 and B26 in the ORIGINAL numbering
idx_a90 = next(i for i, (c, r, n) in enumerate(orig_A) if r == 90)
idx_b26 = next(i for i, (c, r, n) in enumerate(orig_B) if r == 26)
print(f"A90 ordinal index: {idx_a90} (orig={orig_A[idx_a90][2]})")
print(f"B26 ordinal index: {idx_b26} (orig={orig_B[idx_b26][2]})")

import glob
for path in sorted(glob.glob("outputs/4eto_zinc_split/packed/4ETO_s0_gen*_ind*.pdb"))[:10]:
    new = get_ca_list(path)
    new_A = [x for x in new if x[0] == 'A']
    new_B = [x for x in new if x[0] == 'B']
    a90 = new_A[idx_a90][2] if idx_a90 < len(new_A) else "N/A"
    b26 = new_B[idx_b26][2] if idx_b26 < len(new_B) else "N/A"
    print(f"{path}: A90={a90}  B26={b26}")
