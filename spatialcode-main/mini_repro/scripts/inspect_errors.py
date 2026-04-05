from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spatialcode_mini.dataio import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export incorrect cases for manual error analysis.")
    parser.add_argument("--dataset", type=Path, required=True, help="Reference dataset JSONL.")
    parser.add_argument("--predictions", type=Path, required=True, help="Prediction JSONL.")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = {record["sample_id"]: record for record in read_jsonl(args.dataset)}
    predictions = read_jsonl(args.predictions)

    rows: list[dict[str, str]] = []
    for prediction in predictions:
        if prediction["is_correct"]:
            continue
        sample = dataset[prediction["sample_id"]]
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "condition": prediction["condition"],
                "question": sample["question"],
                "allowed_answers": ", ".join(prediction["allowed_answers"]),
                "gold_answer": sample["answer"],
                "parsed_prediction": prediction["parsed_prediction"] or "",
                "raw_output": prediction["raw_output"],
                "difficulty_bucket": sample["metadata"]["difficulty_bucket"],
                "size_ratio": str(sample["metadata"]["size_ratio"]),
                "initial_error_category": "invalid_output" if prediction["parsed_prediction"] is None else "",
                "manual_error_category": "",
                "diagnosis": "",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sample_id",
                "condition",
                "question",
                "allowed_answers",
                "gold_answer",
                "parsed_prediction",
                "raw_output",
                "difficulty_bucket",
                "size_ratio",
                "initial_error_category",
                "manual_error_category",
                "diagnosis",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} error cases to {args.output}")


if __name__ == "__main__":
    main()
