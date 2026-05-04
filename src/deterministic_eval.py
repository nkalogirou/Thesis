from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
from rouge_score import rouge_scorer
from bert_score import score as bertscore_score
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_CSV = PROJECT_ROOT / "results" / "experimental" / "rag_results.csv"
GROUND_TRUTH_CSV = PROJECT_ROOT / "data" / "ground_truth" / "rag_ground_truth.csv"
OUTPUT_CSV = PROJECT_ROOT / "results" / "experimental" / "deterministic_eval_results.csv"
SUMMARY_CSV = PROJECT_ROOT / "results" / "experimental" / "deterministic_eval_summary.csv"


def normalize_text(text: str) -> str:
    if text is None:
        return ""
    return " ".join(str(text).split())


def split_pipe_values(value: str) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    return [part.strip().lower() for part in str(value).split("|") if part.strip()]


def retrieval_metrics(retrieved_sources: str, supporting_documents: str) -> tuple[int, float, float]:
    retrieved = set(split_pipe_values(retrieved_sources))
    supporting = set(split_pipe_values(supporting_documents))

    if not supporting:
        return 0, 0.0, 0.0

    intersection = retrieved.intersection(supporting)

    retrieval_hit = 1 if len(intersection) > 0 else 0
    retrieval_precision = len(intersection) / len(retrieved) if retrieved else 0.0
    retrieval_recall = len(intersection) / len(supporting) if supporting else 0.0

    return retrieval_hit, retrieval_precision, retrieval_recall


def main():
    results_df = pd.read_csv(RESULTS_CSV)
    gt_df = pd.read_csv(GROUND_TRUTH_CSV)

    merged = results_df.merge(
        gt_df[
            [
                "implementation",
                "scenario_id",
                "ground_truth_answer",
                "supporting_documents",
                "manual_score",
                "manual_label",
                "manual_notes",
            ]
        ],
        on=["implementation", "scenario_id"],
        how="inner",
    )

    print("Results rows:", len(results_df))
    print("Ground truth rows:", len(gt_df))
    print("Merged rows:", len(merged))

    merged["generated_answer_norm"] = merged["generated_answer"].apply(normalize_text)
    merged["ground_truth_answer_norm"] = merged["ground_truth_answer"].apply(normalize_text)

    rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    merged["rougeL_f1"] = merged.apply(
        lambda row: rouge.score(
            row["ground_truth_answer_norm"],
            row["generated_answer_norm"],
        )["rougeL"].fmeasure,
        axis=1,
    )

    preds = merged["generated_answer_norm"].tolist()
    refs = merged["ground_truth_answer_norm"].tolist()
    _, _, f1 = bertscore_score(preds, refs, lang="en", verbose=True)
    merged["bertscore_f1"] = [float(x) for x in f1]

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    gen_emb = model.encode(preds, convert_to_numpy=True)
    ref_emb = model.encode(refs, convert_to_numpy=True)

    sims = []
    for i in range(len(preds)):
        sim = cosine_similarity([gen_emb[i]], [ref_emb[i]])[0][0]
        sims.append(float(sim))
    merged["semantic_similarity"] = sims

    retrieval_values = merged.apply(
        lambda row: retrieval_metrics(
            row.get("retrieved_sources", ""),
            row.get("supporting_documents", ""),
        ),
        axis=1,
    )

    merged["retrieval_hit"] = [x[0] for x in retrieval_values]
    merged["retrieval_precision"] = [x[1] for x in retrieval_values]
    merged["retrieval_recall"] = [x[2] for x in retrieval_values]

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT_CSV, index=False)

    summary = (
        merged.groupby("implementation")[
            [
                "manual_score",
                "rougeL_f1",
                "bertscore_f1",
                "semantic_similarity",
                "retrieval_hit",
                "retrieval_precision",
                "retrieval_recall",
            ]
        ]
        .mean()
        .sort_values("manual_score", ascending=False)
    )

    summary.to_csv(SUMMARY_CSV)
    print("Saved:", OUTPUT_CSV)
    print("Saved:", SUMMARY_CSV)
    print(summary)


if __name__ == "__main__":
    main()