#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

TOP_N = 15
GEN_LINE_RE = re.compile(
    r"generation (\d+), index (\d+), pmpnn=([\d.]+) pmetal=([\d.]+)"
)
SEQ_LINE_RE = re.compile(r"^final sequence: (\S+)")
# Captures non-covalent bond profiles (e.g., plip_hbonds=4 or hbonds: 3)
PLIP_LINE_RE = re.compile(r"(?:plip_hbonds|hbonds|interactions)[=\s:]+(\d+)", re.IGNORECASE)

def parse_log(path):
    current_structure = None
    results = defaultdict(list)
    pending_entry = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            
            header_match = re.match(r"=== Running (\S+)", line)
            if header_match:
                current_structure = header_match.group(1)
                continue

            gen_match = GEN_LINE_RE.search(line)
            if gen_match and current_structure:
                pending_entry = {
                    "generation": int(gen_match.group(1)),
                    "index": int(gen_match.group(2)),
                    "pmpnn": float(gen_match.group(3)),
                    "pmetal": float(gen_match.group(4)),
                    "plip": 0,  # Default value if no PLIP interaction line is found
                    "sequence": None,
                }
                continue

            # Extracts the PLIP profile from neighboring text rows
            plip_match = PLIP_LINE_RE.search(line)
            if plip_match and pending_entry is not None:
                pending_entry["plip"] = int(plip_match.group(1))
                continue

            seq_match = SEQ_LINE_RE.match(line)
            if seq_match and pending_entry is not None:
                pending_entry["sequence"] = seq_match.group(1)
                results[current_structure].append(pending_entry)
                pending_entry = None

    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python find_top_pmetal.py <path_to_deva_out_log>")
        sys.exit(1)

    log_path = sys.argv[1]
    results = parse_log(log_path)

    if not results:
        print("No structures found in log. Check the log format / path.")
        return

    for structure, entries in results.items():
        if not entries:
            continue

        top = sorted(entries, key=lambda e: e["pmetal"], reverse=True)[:TOP_N]

        print(f"\n=== {structure}: top {len(top)} by pmetal ===")
        print(f"{'Rank':<5}{'Gen':<6}{'Idx':<5}{'pmpnn':<10}{'pmetal':<10}{'PLIP':<10}")
        print("-" * 50)
        for rank, e in enumerate(top, 1):
            print(f"{rank:<5}{e['generation']:<6}{e['index']:<5}"
                  f"{e['pmpnn']:<10.4f}{e['pmetal']:<10.4f}{e['plip']:<10}")

        best = top[0]
        print(f"\nBest sequence (gen {best['generation']}, "
              f"idx {best['index']}, pmetal={best['pmetal']:.4f}, PLIP={best['plip']}):")
        print(best["sequence"])
        print()

if __name__ == "__main__":
    main()
