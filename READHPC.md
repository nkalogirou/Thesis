# HPC Run Guide

This guide describes the HPC workflow for running the notebooks in `notebooks-hpc/`.

## 1) Login to Cyclone

```bash
ssh <your_username>@front01.hpcf.cyi.ac.cy
```

## 2) Start model services (vLLM)

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

## 3) Start Jupyter on HPC

```bash
cd ~/Thesis/scripts
sbatch launch_jupyter.sh
```

After submission, open the generated `connection_info.txt` in `scripts/` and use:
- the SSH tunnel command
- the local Jupyter URL
- the one-time password

## 4) Run the HPC notebooks

Run notebooks from:

```text
notebooks-hpc/
```

## 5) Results output (HPC)

HPC runs save to:

```text
data/results/experimental/rag_results_hpc.csv
```

This is intentionally separate from local runs (`rag_results.csv`).