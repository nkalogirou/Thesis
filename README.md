# RAG Thesis Project

This repository contains multiple Retrieval-Augmented Generation implementations for comparing baseline retrieval, vector database retrieval, reranking, hybrid retrieval, and hybrid retrieval with reranking.

## Project Structure

```text
notebooks/                      Jupyter notebooks for each RAG implementation
src/                            Python helper scripts for logging, evaluation, and ground truth
scripts/                        Utility scripts, including Milvus startup script
config/                         Milvus configuration files
data/dummy_data/                OrchestrAI synthetic enterprise corpus (DOCX files)
data/ground_truth/              Ground-truth evaluation data
data/results/experimental/      Generated experiment results, ignored by Git
data/results/final/             Final curated results for submission
volumes/                        Local Milvus runtime data, ignored by Git
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
ollama pull mxbai-embed-large
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
3. `notebooks/rag_vectordb_tuned.ipynb` (tuned chunking variant)
4. `notebooks/rag_reranker.ipynb`
5. `notebooks/rag_hybrid.ipynb`
6. `notebooks/rag_hybrid_&_rerank.ipynb`

Generated experiment results are saved to:

```text
data/results/experimental/rag_results.csv
```

## Evaluation

Run deterministic evaluation with:

```bash
python src/deterministic_eval.py
```

This creates:

```text
data/results/experimental/deterministic_eval_results.csv
data/results/experimental/deterministic_eval_summary.csv
```

When results are final, copy them into:

```text
data/results/final/
```

### Evaluation Metrics

The summary CSV contains the following columns, averaged per implementation:

**Answer quality** (higher is better):

- `manual_score` — expert judgment of answer correctness (0–1)
- `rougeL_f1` — word-level overlap with ground truth (longest common subsequence)
- `bertscore_f1` — semantic similarity using contextual BERT embeddings
- `semantic_similarity` — cosine similarity of sentence embeddings (all-MiniLM-L6-v2)

**Retrieval quality** (higher is better):

- `retrieval_hit` — whether at least one relevant document was retrieved (0 or 1)
- `retrieval_precision` — fraction of retrieved documents that are relevant
- `retrieval_recall` — fraction of relevant documents that were retrieved
- `retrieval_f1` — harmonic mean of precision and recall

**Other**:

- `answer_length` — average word count of generated answers
- `indexing_time_s` — time to index all documents (seconds)
- `retrieval_time_s` — average retrieval time per query (seconds)
- `generation_time_s` — average LLM generation time per query (seconds)

### Visualizations

Generate charts from the final results:

Open `notebooks/rag_visualizations.ipynb` and run all cells. Figures are saved to `data/results/figures/`.

## Notes

- The `volumes/` folder contains local Milvus data and is ignored by Git.
- The `data/results/experimental/` folder contains generated experiment outputs and is ignored by Git.
- Only clean, final result files should be committed under `data/results/final/`.
