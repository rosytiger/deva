import re
import glob
import os
import sys

log_candidates = sorted(glob.glob("logs/deva_4eto_zinc_100_*.out"), key=os.path.getmtime)
if not log_candidates:
    print("No matching log file found in logs/ — pass the log path as an argument instead.")
    sys.exit(1)

log_path = sys.argv[1] if len(sys.argv) > 1 else log_candidates[-1]
print(f"Using log: {log_path}")

pattern = re.compile(r"generation (\d+), index (\d+), pmpnn=([\d.eE+-]+) pmetal=([\d.eE+-]+)")
results = []
with open(log_path) as f:
    for line in f:
        m = pattern.search(line)
        if m:
            gen, idx, pmpnn, pmetal = m.groups()
            results.append((int(gen), int(idx), float(pmpnn), float(pmetal)))

if not results:
    print("No generation lines found in this log — is this the right file, "
          "and did the run actually produce generation output?")
    sys.exit(1)

results.sort(key=lambda x: -x[3])
print("\nTop 5 by pmetal:")
for gen, idx, pmpnn, pmetal in results[:5]:
    print(f"  gen{gen} ind{idx}  pmpnn={pmpnn:.4f}  pmetal={pmetal:.4f}")

best_gen, best_idx, best_pmpnn, best_pmetal = results[0]
best_filename = f"4eto_nowater_s0_gen{best_gen}_ind{best_idx}.pdb"
best_path = os.path.join("outputs", "4eto_zinc_100_nowater", "packed", best_filename)
print(f"\nBest individual: gen{best_gen} ind{best_idx} (pmetal={best_pmetal:.4f})")
print(f"Expected packed PDB path: {best_path}")

if not os.path.exists(best_path):
    print(f"\nWARNING: file not found at that path. Run this to see what's actually there:")
    print(f"  ls outputs/4eto_zinc_100_nowater/packed/ | grep gen{best_gen}")
    sys.exit(1)

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

orig_path = "inputs/4eto_nowater.pdb"
if not os.path.exists(orig_path):
    print(f"\nWARNING: {orig_path} not found — edit orig_path in this script to match "
          f"your actual water-removed input filename.")
    sys.exit(1)

orig = get_ca_list(orig_path)
new = get_ca_list(best_path)

orig_A = [x for x in orig if x[0] == 'A']
orig_B = [x for x in orig if x[0] == 'B']
new_A = [x for x in new if x[0] == 'A']
new_B = [x for x in new if x[0] == 'B']

print(f"\norig chain A count: {len(orig_A)}, new chain A count: {len(new_A)}")
print(f"orig chain B count: {len(orig_B)}, new chain B count: {len(new_B)}")
print()

targets = [('A', 17), ('A', 27), ('A', 87), ('A', 91),
           ('B', 17), ('B', 27), ('B', 87), ('B', 91)]

for chain, resi in targets:
    orig_list = orig_A if chain == 'A' else orig_B
    new_list = new_A if chain == 'A' else new_B
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
        print(f"{chain}{resi} (orig={orig_resn}) -> OUT OF RANGE (only {len(new_list)} residues in new chain {chain})")
