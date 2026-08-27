"""Turning a sequence into numbers a model can use.

The idea is simple. Slide a window of length k along the sequence, count how
often each k-mer shows up, and normalise by the total so a long genome and a
short one are comparable. For DNA there are 4**k possible k-mers, so k=4 gives
you a tidy 256-length vector per genome. That vector is your feature row.

This is the piece most worth trusting, because a bug in here quietly poisons
everything downstream. Keep it simple and check it.
"""
from __future__ import annotations

from itertools import product

import numpy as np
import pandas as pd

BASES = "ACGT"


def all_kmers(k):
    """Every possible k-mer over ACGT, in a fixed order.

    Fixing the order matters. It's what lets a k-mer always land in the same
    column, so rows from different genomes line up.
    """
    return ["".join(p) for p in product(BASES, repeat=k)]


def kmer_counts(sequence, k):
    """Count k-mers in one sequence and return them as normalised fractions.

    Anything with a letter outside ACGT (an N, say) gets skipped rather than
    counted, so ambiguous bases don't sneak into the totals. If nothing valid
    is left we just hand back zeros.
    """
    index = {kmer: i for i, kmer in enumerate(all_kmers(k))}
    counts = np.zeros(len(index), dtype=float)

    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i + k]
        j = index.get(kmer)
        if j is not None:  # None means it had a non-ACGT letter, skip it
            counts[j] += 1

    total = counts.sum()
    if total == 0:
        return counts
    return counts / total


def build_feature_matrix(genomes, k=4):
    """Featurise a whole dataset.

    Takes the Genome list from io.load_dataset and returns a DataFrame with one
    row per genome, one column per k-mer, plus label and sample_id columns
    tacked on so you don't lose track of which row is which.
    """
    columns = all_kmers(k)
    rows = [kmer_counts(g.sequence, k) for g in genomes]

    X = pd.DataFrame(rows, columns=columns)
    X.insert(0, "sample_id", [g.sample_id for g in genomes])
    X.insert(1, "label", [g.label for g in genomes])
    return X


if __name__ == "__main__":
    import argparse

    # works whether you run `python -m src.features` or `python src/features.py`
    try:
        from .loader import load_dataset
    except ImportError:
        from loader import load_dataset

    ap = argparse.ArgumentParser(description="Turn FASTA files into a k-mer table.")
    ap.add_argument("--input", default="data/raw/toy", help="label-per-folder directory")
    ap.add_argument("--k", type=int, default=4, help="k-mer length")
    ap.add_argument("--out", default="data/processed/features.parquet",
                    help="where to write the table")
    args = ap.parse_args()

    genomes = load_dataset(args.input)
    table = build_feature_matrix(genomes, k=args.k)

    try:
        table.to_parquet(args.out, index=False)
        print(f"Wrote {table.shape[0]} rows x {table.shape[1] - 2} k-mer features to {args.out}")
    except Exception as e:
        # parquet needs pyarrow. if it's missing, fall back to csv so you're not stuck.
        fallback = args.out.rsplit(".", 1)[0] + ".csv"
        table.to_csv(fallback, index=False)
        print(f"(parquet failed: {e})")
        print(f"Wrote CSV instead: {fallback}")
