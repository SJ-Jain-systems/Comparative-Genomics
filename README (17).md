# Comparative Genomics

A machine learning project built around a simple question. How much can you tell
about an organism just from its DNA?

A genome is really just a very long string over a four-letter alphabet, and a lot
of things we care about turn out to be predictable from patterns in that string.
Things like what species it is, what a gene does, or whether it carries a
resistance gene. This project takes that idea and runs with it, starting from
basic k-mer counts and classical models and working up toward learned embeddings
and deep sequence models.

It's early days. This README describes where the project is headed more than what
already exists.

## Why bother

Comparative genomics is about how genomes differ across species and strains, and
what those differences mean. That maps onto machine learning pretty naturally. You
turn sequences into numbers, train a model to predict some label, and check
whether it actually learned anything real. Along the way you get to look at the
structure the model finds and compare it against what biologists already know
about how these organisms are related.

## What you could predict

The pipeline is the same regardless of the label, so you can pick whatever sounds
interesting.

| Task | Label | Type |
|------|-------|------|
| Taxonomic classification | species or genus | multi-class |
| Promoter detection | promoter or not | binary |
| Gene function prediction | functional category | multi-class |
| Resistance-gene screening | AMR gene or not | binary |
| Pathogen vs. commensal | pathogenic or benign | binary |

I'd suggest starting with taxonomic classification, mostly because the labels are
easy to come by and there's plenty of data.

## How it's structured

The plan is a series of phases. Each one is usable on its own, and each builds on
the plumbing from the last.

### Phase 1, a solid baseline

Parse FASTA files, count k-mers, turn each genome into a fixed-length vector of
frequencies, and train something like a random forest or gradient boosting on top.
Then evaluate it honestly with cross-validation, a confusion matrix, ROC and PR
curves, and a look at which k-mers mattered most. The goal here is just to beat a
majority-class baseline and understand why it works.

### Phase 2, exploring the structure

Reduce the k-mer vectors down to two dimensions with PCA or UMAP and see whether
the taxa separate on their own. Cluster them and compare the clusters against
known taxonomy. As a sanity check, build a MinHash sketch distance matrix and draw
a quick dendrogram, which is a fast, alignment-free way to approximate a
phylogenetic tree.

### Phase 3, learning representations

This is the more interesting part. Instead of hand-counting k-mers, learn genome
embeddings, either with a k-mer2vec style approach or a small neural network over
the raw sequence. Visualize the embedding space, see whether taxa separate there,
and use those embeddings as features to compare against the Phase 1 baseline.

### Phase 4, deep sequence models if it's worth it

Train a 1D CNN or a small transformer end to end on sequence windows and benchmark
it against the simpler models. Part of the exercise is figuring out where the deep
model actually helps and where it's overkill.

## Layout

```
Comparative-Genomics/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/            # downloaded genomes (FASTA), gitignored
│   └── processed/      # feature matrices, splits
├── src/
│   ├── io.py           # FASTA parsing, dataset assembly
│   ├── features.py     # k-mer counting into feature vectors
│   ├── sketch.py       # MinHash sketching and distances (Phase 2)
│   ├── models.py       # model definitions and training helpers
│   └── evaluate.py     # metrics and plots
├── notebooks/
│   ├── 01_baseline.ipynb
│   ├── 02_eda_clustering.ipynb
│   └── 03_embeddings.ipynb
└── tests/
```

## Data

No genomic data lives in the repo. Some good places to pull it from are NCBI
RefSeq and GenBank for reference genomes and annotations, the NCBI Datasets CLI or
API for bulk downloads by taxon, and curated benchmark sets like collections of
bacterial genomes put together for classification work.

You don't need much to get going. A handful of genomes across two or three taxa is
enough to build the whole pipeline before you scale it up.

## Getting started

```bash
# Install dependencies
pip install -r requirements.txt

# Drop a few FASTA files under data/raw/, grouped by label

# Featurize and train the baseline
python -m src.features --input data/raw --k 4 --out data/processed/features.parquet
python -m src.models --features data/processed/features.parquet --task taxon
```

Those commands show the interface I'm aiming for. The scripts themselves get
written as Phase 1 comes together.

## Tools

Python throughout, with pandas and NumPy for the data wrangling, scikit-learn and
XGBoost for the classical models, matplotlib, seaborn, and UMAP for plots, and
PyTorch once the embedding work starts. Biopython handles sequence parsing, and
sourmash or Mash are options for the sketching in Phase 2.

## License

To be decided.
