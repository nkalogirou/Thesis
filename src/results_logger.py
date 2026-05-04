from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Optional, Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_CSV = PROJECT_ROOT / "data" / "results" / "experimental" / "rag_results.csv"

RESULTS_COLUMNS = [
    "implementation",
    "scenario_id",
    "question",
    "generated_answer",
    "retrieved_sources",
    "retrieved_departments",
    "retrieved_contexts",
    "num_retrieved_docs",
    "retriever_top_k",
    "reranker_top_k",
    "indexing_time_s",
    "retrieval_time_s",
    "generation_time_s",
]


def _safe_meta(doc: Any) -> dict:
    meta = getattr(doc, "meta", {}) or {}
    return meta if isinstance(meta, dict) else {}


def extract_doc_metadata(top_docs: Optional[Iterable[Any]]) -> tuple[list[str], list[str], list[str]]:
    sources: list[str] = []
    departments: list[str] = []
    contexts: list[str] = []

    for d in top_docs or []:
        meta = _safe_meta(d)
        source = meta.get("file_name", meta.get("file_path", "unknown source"))
        department = meta.get("department", "unknown department")
        content = getattr(d, "content", "") or ""

        sources.append(str(source))
        departments.append(str(department))
        contexts.append(" ".join(str(content).split()))

    return sources, departments, contexts


def ensure_results_file(results_csv: str | Path = DEFAULT_RESULTS_CSV) -> Path:
    results_path = Path(results_csv)

    if not results_path.exists():
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(results_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=RESULTS_COLUMNS)
            writer.writeheader()

    return results_path


def read_results_rows(results_csv: str | Path = DEFAULT_RESULTS_CSV) -> list[dict]:
    results_path = ensure_results_file(results_csv)

    with open(results_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_results_rows(rows: list[dict], results_csv: str | Path = DEFAULT_RESULTS_CSV) -> Path:
    results_path = Path(results_csv)

    with open(results_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULTS_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return results_path


def clear_results_for_implementation(
    implementation: str,
    results_csv: str | Path = DEFAULT_RESULTS_CSV,
) -> Path:
    rows = read_results_rows(results_csv)
    filtered_rows = [row for row in rows if row.get("implementation") != implementation]

    write_results_rows(filtered_rows, results_csv)
    print(f"Cleared existing rows for implementation='{implementation}'")
    return Path(results_csv)


def save_result_row(
    implementation: str,
    scenario_id: str,
    question: str,
    generated_answer: str,
    top_docs: Optional[Iterable[Any]],
    retriever_top_k: Optional[int] = None,
    reranker_top_k: Optional[int] = None,
    indexing_time_s: Optional[float] = None,
    retrieval_time_s: Optional[float] = None,
    generation_time_s: Optional[float] = None,
    results_csv: str | Path = DEFAULT_RESULTS_CSV,
) -> Path:
    results_path = ensure_results_file(results_csv)
    sources, departments, contexts = extract_doc_metadata(top_docs)

    top_docs_list = list(top_docs) if top_docs is not None else []

    new_row = {
        "implementation": implementation,
        "scenario_id": scenario_id,
        "question": question,
        "generated_answer": generated_answer,
        "retrieved_sources": " | ".join(sources),
        "retrieved_departments": " | ".join(departments),
        "retrieved_contexts": " ||| ".join(contexts),
        "num_retrieved_docs": len(top_docs_list),
        "retriever_top_k": retriever_top_k,
        "reranker_top_k": reranker_top_k,
        "indexing_time_s": indexing_time_s,
        "retrieval_time_s": retrieval_time_s,
        "generation_time_s": generation_time_s,
    }

    rows = read_results_rows(results_path)

    replaced = False
    for i, row in enumerate(rows):
        if (
            row.get("implementation") == implementation
            and row.get("scenario_id") == scenario_id
        ):
            rows[i] = new_row
            replaced = True
            break

    if not replaced:
        rows.append(new_row)

    write_results_rows(rows, results_path)

    action = "Updated" if replaced else "Saved"
    print(f"{action} result in {results_path}")
    return results_path