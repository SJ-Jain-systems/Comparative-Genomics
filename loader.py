"""Reading genomes off disk.

The layout is one folder per label, and the folder name is the label:

    data/raw/toy/
        alphacoccus/
            alphacoccus_1.fasta
            ...
        betabacter/
            ...

Each FASTA file counts as one sample. If a file happens to hold several
records (contigs), we just glue them together into one sequence. No external
libraries here on purpose, plain standard library is plenty for reading FASTA.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Genome:
    sample_id: str
    sequence: str
    label: str


def read_fasta(path):
    """Pull the sequence out of a FASTA file, upper-cased.

    Header lines (the ones starting with '>') and blank lines get skipped, and
    everything else is joined together. If there are multiple records they end
    up concatenated, which is what we want here.
    """
    parts = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(">"):
                continue
            parts.append(line.upper())
    return "".join(parts)


def load_dataset(root):
    """Load every FASTA under a label-per-folder directory.

    Returns a list of Genome samples, sorted so you get the same order every
    run. The folder name becomes the label.
    """
    genomes = []
    for label in sorted(os.listdir(root)):
        label_dir = os.path.join(root, label)
        if not os.path.isdir(label_dir):
            continue
        for fname in sorted(os.listdir(label_dir)):
            if not fname.lower().endswith((".fasta", ".fa", ".fna")):
                continue
            seq = read_fasta(os.path.join(label_dir, fname))
            if not seq:
                continue  # skip empty files rather than choke on them
            sample_id = os.path.splitext(fname)[0]
            genomes.append(Genome(sample_id, seq, label))

    if not genomes:
        raise ValueError(f"Didn't find any FASTA files under {root!r}")
    return genomes


if __name__ == "__main__":
    import sys

    # quick way to eyeball what got loaded: python -m src.loader data/raw/toy
    root = sys.argv[1] if len(sys.argv) > 1 else "data/raw/toy"
    data = load_dataset(root)
    print(f"Loaded {len(data)} samples from {root}")
    for g in data:
        print(f"  {g.sample_id:20s} {g.label:14s} {len(g.sequence)} bp")
