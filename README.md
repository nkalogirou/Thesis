# RAG Thesis Project

This repository contains multiple Retrieval-Augmented Generation implementations for comparing baseline retrieval, vector database retrieval, reranking, hybrid retrieval, and hybrid retrieval with reranking.

## Project Structure

```text
.
├── notebooks/
│   ├── rag_basic.ipynb                 Baseline RAG with in-memory retrieval
│   ├── rag_vectordb.ipynb              Dense retrieval using Milvus
│   ├── rag_vectordb_tuned.ipynb        VectorDB with tuned chunking parameters
│   ├── rag_reranker.ipynb              Dense retrieval + cross-encoder reranking
│   ├── rag_hybrid.ipynb                Hybrid retrieval (dense + BM25)
│   ├── rag_hybrid_&_rerank.ipynb       Hybrid retrieval + reranking
│   └── rag_visualizations.ipynb        Charts and figures for the thesis
│
├── src/
│   ├── results_logger.py               Shared CSV logging for all notebooks
│   ├── ground_truth_builder.py         Generates ground-truth template from results
│   └── deterministic_eval.py           Automated evaluation (ROUGE, BERTScore, etc.)
│
├── scripts/
│   └── standalone_embed.sh             Milvus start/stop/restart script
│
├── config/
│   ├── embedEtcd.yaml                  Milvus etcd configuration
│   └── user.yaml                       Milvus user configuration
│
├── data/
│   ├── dummy_data/                     OrchestrAI synthetic enterprise corpus
│   ├── ground_truth/
│   │   └── rag_ground_truth.csv        Manual scores and reference answers
│   └── results/
│       ├── experimental/               Generated outputs, ignored by Git
│       ├── final/                      Curated results for submission
│       └── figures/                    Exported charts
│
├── Thesis/                             LaTeX thesis source and compiled PDF
│   ├── _main.tex                       Main LaTeX entry point
│   ├── _main.pdf                       Compiled thesis PDF
│   ├── ADG.sty                         Thesis style/package configuration
│   ├── references.bib                  Bibliography entries
│   ├── 0_covers.tex                    Cover pages
│   ├── 0_prebody.tex                   Declaration, acknowledgements, abstract, abbreviations, TOC
│   ├── 01_introduction.tex             Chapter 1: Introduction
│   ├── 02_background.tex               Chapter 2: Background
│   ├── 03_literature_review.tex        Chapter 3: Literature review
│   ├── 04_methodology.tex              Chapter 4: Methodology
│   ├── 05_experiments.tex              Chapter 5: Experiments
│   ├── 06_results_discussion.tex       Chapter 6: Results and discussion
│   ├── 07_conclusion_future_work.tex   Chapter 7: Conclusion and future work
│   ├── appendices.tex                  Appendix material
│   ├── manuals.tex                     Installation and user manuals
│   └── images/                         Thesis figures and diagrams
│       ├── euc.jpg
│       ├── Multi-head_attention.png
│       ├── Transformer,_full_architecture.png
│       ├── rag-architecture.png
│       ├── fig01_overall_thesis_workflow.png
│       ├── fig02_simplified_transformer.png
│       ├── fig03_high_level_rag_pipeline.png
│       ├── fig04_plain_llm_vs_rag.png
│       ├── fig08_six_pipeline_variants.png
│       ├── fig09_answer_quality.png
│       ├── fig10_retrieval_quality.png
│       ├── fig11_timing_breakdown.png
│       ├── fig12_scenario_heatmap.png
│       └── fig13_radar_chart.png
│
├── volumes/                            Milvus runtime data, ignored by Git
├── requirements.txt                    Python dependencies
├── .gitignore
└── README.md
```

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Local vs HPC

- Local workflow uses notebooks in `notebooks/` and writes to `data/results/experimental/rag_results.csv`.
- HPC workflow uses notebooks in `notebooks-hpc/` and writes to `data/results/experimental/rag_results_hpc.csv`.
- HPC startup details (vLLM jobs + Jupyter tunnel) are documented in `READHPC.md`.

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

For HPC runs, execute the mirrored notebooks under `notebooks-hpc/` in the same order and use:

```text
data/results/experimental/rag_results_hpc.csv
```

## Evaluation

### Manual Ground Truth (Strict)

Manual evaluation lives in:

```text
data/ground_truth/rag_ground_truth.csv
```

For each `(implementation, scenario_id)` row, we derive `ground_truth_answer` **only from** the DOCX files in `data/dummy_data/` and then score `generated_answer` strictly using:

- `manual_score`: `1.0` (correct), `0.5` (partially correct), `0.0` (incorrect)
- `manual_label`: `correct`, `partially_correct`, `incorrect`

The fields `supporting_documents` and `manual_notes` must be evidence-based (only filenames that were actually used; no invented facts).

Run deterministic evaluation with:

```bash
python3 src/deterministic_eval.py
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
