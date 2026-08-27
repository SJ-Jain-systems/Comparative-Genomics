"""Make a little fake dataset so the pipeline has something to chew on.

Real genomes are big and take a while to download, and when you're still
writing the code you don't want to wait on that. So this just makes up three
"species" where each one favours different letters. That gives them different
k-mer profiles, which is enough for a simple model to tell them apart. None of
this is real biology, it's just scaffolding. Swap in actual genomes from NCBI
once the code works.

    python scripts/make_toy_data.py

Files land in data/raw/toy/<species>/<species>_<n>.fasta
"""
import os
import random

# how much each fake species likes A, C, G, T
# spread them out on purpose so the classes are easy to separate at first
SPECIES = {
    "alphacoccus": [0.40, 0.10, 0.10, 0.40],  # lots of A and T
    "betabacter":  [0.10, 0.40, 0.40, 0.10],  # lots of C and G
    "gammaspira":  [0.25, 0.25, 0.25, 0.25],  # no preference
}

BASES = "ACGT"
GENOMES_EACH = 4
LENGTH = 5000
SEED = 42  # fixed so you get the same data every time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "raw", "toy")


def make_sequence(weights, length, rng):
    return "".join(rng.choices(BASES, weights=weights, k=length))


def write_fasta(path, header, seq, width=70):
    with open(path, "w") as fh:
        fh.write(">" + header + "\n")
        # wrap the sequence so the file looks like a normal FASTA
        for i in range(0, len(seq), width):
            fh.write(seq[i:i + width] + "\n")


def main():
    rng = random.Random(SEED)
    for species, weights in SPECIES.items():
        folder = os.path.join(OUT, species)
        os.makedirs(folder, exist_ok=True)
        for n in range(1, GENOMES_EACH + 1):
            seq = make_sequence(weights, LENGTH, rng)
            path = os.path.join(folder, f"{species}_{n}.fasta")
            write_fasta(path, f"{species}_{n} fake genome for testing", seq)
            print("wrote", os.path.relpath(path, os.path.join(HERE, "..")))


if __name__ == "__main__":
    main()
