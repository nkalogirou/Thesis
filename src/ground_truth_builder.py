from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_CSV = PROJECT_ROOT / "data" / "results" / "experimental" / "rag_results.csv"
GROUND_TRUTH_CSV = PROJECT_ROOT / "data" / "ground_truth" / "rag_ground_truth.csv"

GROUND_TRUTH_COLUMNS = [
    "implementation",
    "scenario_id",
    "question",
    "generated_answer",
    "ground_truth_answer",
    "supporting_documents",
    "manual_score",
    "manual_label",
    "manual_notes",
]


def build_ground_truth_sheet(
    results_csv: str | Path = RESULTS_CSV,
    ground_truth_csv: str | Path = GROUND_TRUTH_CSV,
    overwrite: bool = True,
) -> Path:
    results_path = Path(results_csv)
    ground_truth_path = Path(ground_truth_csv)

    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    with open(results_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        results_rows = list(reader)

    output_rows = []
    for row in results_rows:
        output_rows.append({
            "implementation": row.get("implementation", ""),
            "scenario_id": row.get("scenario_id", ""),
            "question": row.get("question", ""),
            "generated_answer": row.get("generated_answer", ""),
            "ground_truth_answer": "",
            "supporting_documents": "",
            "manual_score": "",
            "manual_label": "",
            "manual_notes": "",
        })

    if ground_truth_path.exists() and not overwrite:
        raise FileExistsError(
            f"{ground_truth_path} already exists. Use overwrite=True to replace it."
        )

    ground_truth_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ground_truth_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=GROUND_TRUTH_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Created {ground_truth_path} with {len(output_rows)} rows.")
    return ground_truth_path