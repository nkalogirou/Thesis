# Setup and Run Guide

## Project overview

This project contains multiple notebook-based RAG implementations:

* `rag_basic.ipynb`
* `rag_vectordb.ipynb`
* `rag_reranker.ipynb`
* `rag_hybrid.ipynb`
* `rag_hybrid_&_rerank.ipynb`

Shared helper code lives in Python files such as:

* `results_logger.py`

Generated evaluation outputs are saved into:

* `rag_results.csv`

Milvus persistent storage is stored under:

* `volumes/milvus/`

---

## 1. Prerequisites

Make sure you have the following installed on your machine:

* Python 3.12
* `pip`
* `venv`
* Docker Desktop
* Ollama
* Jupyter Notebook or JupyterLab

Recommended Ollama models:

* `llama3.1`
* `nomic-embed-text`

If you use reranking:

* `sentence-transformers`

---

## 2. Open the project folder

```bash
cd ~/Thesis
```

If your project is somewhere else, replace the path accordingly.

---

## 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

If the environment does not exist yet, create it first:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Then install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If needed, also install notebook tooling:

```bash
python -m pip install notebook jupyterlab ipykernel
```

---

## 4. Start Ollama

Open a new terminal window/tab and run:

```bash
ollama serve
```

Leave that terminal running.

To check that Ollama is available:

```bash
curl http://localhost:11434/api/tags
```

To check your installed models:

```bash
ollama list
```

If needed, pull the models:

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

---

## 5. Start Milvus

Open another terminal window/tab, go to the project, and run:

```bash
cd ~/Thesis
bash standalone_embed.sh start
```

Leave that terminal running.

To verify Milvus is up:

```bash
docker ps
```

You should see a Milvus-related container running.

To stop Milvus later:

```bash
cd ~/Thesis
bash standalone_embed.sh stop
```

---

## 6. Start Jupyter

Open another terminal window/tab:

```bash
cd ~/Thesis
source .venv/bin/activate
jupyter notebook
```

If you prefer Lab:

```bash
jupyter lab
```

If a URL appears, copy it into your browser.

### Note for macOS + Desktop/iCloud paths

If Jupyter appears to hang, this may be due to macOS trash handling inside an iCloud-backed Desktop folder. In that case, try:

```bash
jupyter notebook --no-browser --FileContentsManager.delete_to_trash=False
```

---

## 7. Verify the Python kernel inside the notebook

In a notebook cell, run:

```python
import sys
print(sys.executable)
```

It should point to your project virtual environment, for example:

```text
/Users/nikos/Thesis
```

If it does not, switch to the correct Jupyter kernel.

---

## 8. Notebook execution order

For each notebook, follow this order:

1. Run import cells
2. Run configuration cells
3. Run indexing/document loading cells
4. Run pipeline creation cells
5. Run the helper query functions
6. Run the `run_and_save_*` scenario cells

 - All notebooks now use deterministic generation with temperature=0.0, top_p=1.0, and seed=42.
---

## 9. Available notebooks

### `rag_basic.ipynb`

Baseline RAG with in-memory retrieval.

### `rag_vectordb.ipynb`

Dense retrieval using Milvus.

### `rag_reranker.ipynb`

Dense retrieval with reranking.

### `rag_hybrid.ipynb`

Hybrid retrieval using dense + sparse/BM25 logic.

### `rag_hybrid_&_rerank.ipynb`

Hybrid retrieval followed by reranking.

---

## 10. Results logging

Results are saved into a single combined CSV:

* `rag_results.csv`

Shared logging logic lives in:

* `results_logger.py`

Before running scenarios in a notebook, reload the logger:

```python
import importlib
import results_logger

importlib.reload(results_logger)
from results_logger import save_result_row, clear_results_for_implementation
```

Then clear only the rows for the implementation you are about to rerun.

### For `rag_basic.ipynb`

```python
clear_results_for_implementation("basic")
```

### For `rag_vectordb.ipynb`

```python
clear_results_for_implementation("vectordb")
```

### For `rag_reranker.ipynb`

```python
clear_results_for_implementation("reranker")
```

### For `rag_hybrid.ipynb`

```python
clear_results_for_implementation("hybrid")
```

### For `rag_hybrid_&_rerank.ipynb`

```python
clear_results_for_implementation("hybrid_rerank")
```

This keeps other implementations in the CSV and replaces only the rows for the implementation you rerun.

---

## 11. Running scenarios

Each notebook uses wrapper functions such as:

* `run_and_save_basic(...)`
* `run_and_save_vectordb(...)`
* `run_and_save_reranker(...)`
* `run_and_save_hybrid(...)`
* `run_and_save_hybrid_rerank(...)`

Example:

```python
top_docs_basic_s1, answer_basic_s1 = run_and_save_basic(
    "What is the first-response SLA for a Sev-1 support incident?",
    scenario_id="s1",
)
```

These wrappers:

1. run the query
2. print retrieved documents and answer
3. save the result to `rag_results.csv`

---

## 12. Inspect saved results

In a notebook cell:

```python
import pandas as pd

df = pd.read_csv("rag_results.csv")
df
```

To inspect only the latest rows:

```python
df.tail(10)
```

---

## 13. Timing fields

If your notebooks measure timings, the CSV may store values like:

* `indexing_time_s`
* `retrieval_time_s`
* `generation_time_s`

These should be measured in the notebooks and then passed into `save_result_row(...)`.

---

## 14. Milvus storage location

Milvus data is stored locally under:

```text
volumes/milvus/
```

This is generated runtime data and should generally **not** be committed to GitHub.

Important subfolders may include:

* `volumes/milvus/rdb_data`
* `volumes/milvus/rdb_data_meta_kv`
* `volumes/milvus/etcd`
* `volumes/milvus/data`

---

## 15. Recommended `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
volumes/
.DS_Store
.env
```

---

## 16. Common troubleshooting

### Jupyter does not start

Try:

```bash
jupyter notebook --no-browser --FileContentsManager.delete_to_trash=False
```

Or:

```bash
jupyter lab --no-browser
```

### Wrong Python kernel in notebook

Check:

```python
import sys
print(sys.executable)
```

### Ollama not responding

Check:

```bash
curl http://localhost:11434/api/tags
```

### Milvus not running

Check:

```bash
docker ps
```

Then restart:

```bash
bash standalone_embed.sh stop
bash standalone_embed.sh start
```

### Duplicate CSV rows

Make sure you:

1. reload `results_logger`
2. call `clear_results_for_implementation(...)`
3. then rerun that notebookâs scenarios

---

## 17. Recommended daily startup workflow

### Terminal 1

```bash
cd ~/Desktop/rag-ollama
source .venv/bin/activate
ollama serve
```

### Terminal 2

```bash
cd ~/Desktop/rag-ollama
bash standalone_embed.sh start
```

### Terminal 3

```bash
cd ~/Desktop/rag-ollama
source .venv/bin/activate
jupyter notebook --no-browser --FileContentsManager.delete_to_trash=False
```

Then open the printed URL in your browser and run the notebook you want.

---

## 18. Shutdown workflow

### Stop Jupyter

Press:

```text
Ctrl + C
```

### Stop Ollama

Press:

```text
Ctrl + C
```

### Stop Milvus

```bash
cd ~/Desktop/rag-ollama
bash st
```
