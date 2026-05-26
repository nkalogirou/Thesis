# HPC Run Guide

This guide describes the HPC workflow for running the notebooks in `notebooks-hpc/`.

## 1) Login to Cyclone

```bash
ssh <your_username>@front01.hpcf.cyi.ac.cy
```

## 2) Hugging Face token (one-time setup)

Gated models (for example Llama) need a Hugging Face token. Store it on the cluster only — **never in git**.

```bash
cd ~/Thesis
cp .env.example .env
chmod 600 .env
# edit .env and set: HF_TOKEN=hf_...
```

`rag-training2025-main/vllm/llm_launcher.sh` loads `~/Thesis/.env` automatically when you submit jobs. Do not put tokens in shell scripts or notebooks.

## 3) Start model services (vLLM)

From the vLLM launcher directory:

```bash
cd ~/Thesis/rag-training2025-main/vllm
bash serve_models.sh
```

This submits:

- `llm_launcher.sh`
- `embedder_launcher.sh`
- `ranker_launcher.sh`

Optional status check:

```bash
squeue -u $USER
```

## 4) Start Jupyter on HPC

```bash
cd ~/Thesis/scripts
sbatch launch_jupyter.sh
```

After submission, open the generated `scripts/connection_info.txt` (gitignored) and use:

- the SSH tunnel command
- the local Jupyter URL
- the one-time password

## 5) Run the HPC notebooks

Run notebooks from:

```text
notebooks-hpc/
```

Same order as local: `rag_basic` → `rag_vectordb` → `rag_vectordb_tuned` → `rag_reranker` → `rag_hybrid` → `rag_hybrid_&_rerank`.

## 6) Results output (HPC)

HPC runs append to:

```text
data/results/experimental/hpc_results.csv
```

This is separate from local runs (`data/results/experimental/rag_results.csv`).

## 7) Compare local vs HPC timing (optional)

From the repo root on a machine with matplotlib:

```bash
python scripts/compare_timing_local_hpc.py
```

Defaults: local `data/results/final/rag_results.csv`, HPC `notebooks-hpc/data/results/experimental/hpc_results.csv`. Curated comparison charts live under `data/results/local_vs_hpc/`.
