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
    parser = argparse.ArgumentParser(description="Evaluate prediction JSONL files.")
    parser.add_argument("--dataset", type=Path, required=True, help="Reference dataset JSONL.")
    parser.add_argument(
        "--predictions",
        type=Path,
        nargs="+",
        required=True,
        help="One or more prediction JSONL files.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path.")
    return parser.parse_args()


def percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return 100.0 * numerator / denominator


def main() -> None:
    args = parse_args()
    dataset = {record["sample_id"]: record for record in read_jsonl(args.dataset)}
    rows: list[dict[str, str | int | float]] = []

    for prediction_path in args.predictions:
        predictions = read_jsonl(prediction_path)
        if not predictions:
            continue

        total = len(predictions)
        valid = sum(1 for row in predictions if row["parsed_prediction"] is not None)
        correct = sum(1 for row in predictions if row["is_correct"])
        invalid = total - valid
        condition = predictions[0]["condition"]
        model_id = predictions[0]["model_id"]

        bucket_totals = {"hard": 0, "medium": 0, "easy": 0}
        bucket_correct = {"hard": 0, "medium": 0, "easy": 0}
        for prediction in predictions:
            sample = dataset[prediction["sample_id"]]
            bucket = sample["metadata"]["difficulty_bucket"]
            bucket_totals[bucket] += 1
            if prediction["is_correct"]:
                bucket_correct[bucket] += 1

        row = {
            "condition": condition,
            "model_id": model_id,
            "num_samples": total,
            "accuracy": round(percentage(correct, total), 2),
            "invalid_rate": round(percentage(invalid, total), 2),
            "hard_accuracy": round(percentage(bucket_correct["hard"], bucket_totals["hard"]), 2),
            "medium_accuracy": round(percentage(bucket_correct["medium"], bucket_totals["medium"]), 2),
            "easy_accuracy": round(percentage(bucket_correct["easy"], bucket_totals["easy"]), 2),
            "source_file": str(prediction_path),
        }
        rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "condition",
                "model_id",
                "num_samples",
                "accuracy",
                "invalid_rate",
                "hard_accuracy",
                "medium_accuracy",
                "easy_accuracy",
                "source_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(
            f"{row['condition']}: accuracy={row['accuracy']}% "
            f"invalid={row['invalid_rate']}% samples={row['num_samples']}"
        )
    print(f"Wrote summary metrics to {args.output}")


if __name__ == "__main__":
    main()
