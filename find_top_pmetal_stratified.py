#!/usr/bin/env python3
"""
Selects top-pmetal individuals in a STRATIFIED way across the full
generation history, to avoid selection bias toward whichever region
of the run happened to score highest.

Splits the generation range into N_BINS evenly-spaced bins and picks
the single best-pmetal individual from each bin. With 100 generations
and N_BINS=15, each bin covers ~6-7 generations, giving a candidate
set that represents ~15% of the run, spread across its full length.
"""

import sys
import re
from collections import defaultdict

N_BINS = 15  # ~15% of a 100-generation run

GEN_LINE_RE = re.compile(
    r"generation (\d+), index (\d+), pmpnn=([\d.]+) pmetal=([\d.]+)"
)
SEQ_LINE_RE = re.compile(r"^final sequence: (\S+)")


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
                    "sequence": None,
                }
                continue

            seq_match = SEQ_LINE_RE.match(line)
            if seq_match and pending_entry is not None:
                pending_entry["sequence"] = seq_match.group(1)
                results[current_structure].append(pending_entry)
                pending_entry = None

    return results


def stratified_top(entries, n_bins):
    if not entries:
        return []

    min_gen = min(e["generation"] for e in entries)
    max_gen = max(e["generation"] for e in entries)
    span = max_gen - min_gen + 1
    bin_size = max(1, span / n_bins)

    bins = defaultdict(list)
    for e in entries:
        bin_idx = int((e["generation"] - min_gen) / bin_size)
        bin_idx = min(bin_idx, n_bins - 1)
        bins[bin_idx].append(e)

    selected = []
    for bin_idx in sorted(bins.keys()):
        best_in_bin = max(bins[bin_idx], key=lambda e: e["pmetal"])
        selected.append(best_in_bin)

    return selected


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_top_pmetal_stratified.py <path_to_deva_out_log>")
        sys.exit(1)

    log_path = sys.argv[1]
    results = parse_log(log_path)

    if not results:
        print("No structures found in log. Check the log format / path.")
        return

    for structure, entries in results.items():
        if not entries:
            continue

        selected = stratified_top(entries, N_BINS)
        selected_sorted = sorted(selected, key=lambda e: e["generation"])

        print(f"\n=== {structure}: {len(selected)} stratified picks "
              f"across generation range (~{N_BINS} bins) ===")
        print(f"{'Bin':<5}{'Gen':<6}{'Idx':<5}{'pmpnn':<10}{'pmetal':<10}")
        print("-" * 40)
        for rank, e in enumerate(selected_sorted, 1):
            print(f"{rank:<5}{e['generation']:<6}{e['index']:<5}"
                  f"{e['pmpnn']:<10.4f}{e['pmetal']:<10.4f}")

        best = max(selected, key=lambda e: e["pmetal"])
        print(f"\nHighest-pmetal pick among the stratified set "
              f"(gen {best['generation']}, idx {best['index']}, "
              f"pmetal={best['pmetal']:.4f})")
        print()


if __name__ == "__main__":
    main()
