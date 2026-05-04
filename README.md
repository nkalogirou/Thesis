# RAG Thesis Project

This repository contains multiple Retrieval-Augmented Generation implementations for comparing baseline retrieval, vector database retrieval, reranking, hybrid retrieval, and hybrid retrieval with reranking.

## Project Structure

```text
notebooks/              Jupyter notebooks for each RAG implementation
src/                    Python helper scripts for logging, evaluation, and ground truth
scripts/                Utility scripts, including Milvus startup script
config/                 Milvus configuration files
prompts/                Prompt templates
data/ground_truth/      Ground-truth evaluation data
results/experimental/   Generated experiment results, ignored by Git
results/final/          Final curated results for submission
docs/                   Project documentation
volumes/                Local Milvus runtime data, ignored by Git
```

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Start Ollama

```bash
ollama serve
```

Required models:

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

## Start Milvus

```bash
bash scripts/standalone_embed.sh start
```

Stop Milvus:

```bash
bash scripts/standalone_embed.sh stop
```

Restart Milvus:

```bash
bash scripts/standalone_embed.sh restart
```

## Start Jupyter

```bash
jupyter notebook
```

Then open the notebooks from the `notebooks/` folder.

## Running Experiments

Run the notebooks in this order:

1. `notebooks/rag_basic.ipynb`
2. `notebooks/rag_vectordb.ipynb`
3. `notebooks/rag_reranker.ipynb`
4. `notebooks/rag_hybrid.ipynb`
5. `notebooks/rag_hybrid_&_rerank.ipynb`

Generated experiment results are saved to:

```text
results/experimental/rag_results.csv
```

## Evaluation

Run deterministic evaluation with:

```bash
python src/deterministic_eval.py
```

This creates:

```text
results/experimental/deterministic_eval_results.csv
results/experimental/deterministic_eval_summary.csv
```

When results are final, copy them into:

```text
results/final/
```

## Notes

- The `volumes/` folder contains local Milvus data and is ignored by Git.
- The `results/experimental/` folder contains generated experiment outputs and is ignored by Git.
- Only clean, final result files should be committed under `results/final/`.
