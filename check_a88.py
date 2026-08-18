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
idx_a88 = next(i for i, (c, r, n) in enumerate(orig_A) if r == 88)
print(f"A88 ordinal index: {idx_a88} (orig={orig_A[idx_a88][2]})")

import glob
paths = sorted(glob.glob("outputs/4eto_zinc_split_v2/packed/4ETO_s0_gen*_ind*.pdb"))
print(f"Found {len(paths)} packed files in 4eto_zinc_split_v2/packed/")
for path in paths[:10]:
    new = get_ca_list(path)
    new_A = [x for x in new if x[0] == 'A']
    a88 = new_A[idx_a88][2] if idx_a88 < len(new_A) else "OUT OF RANGE"
    print(f"{path}: A88={a88}")
