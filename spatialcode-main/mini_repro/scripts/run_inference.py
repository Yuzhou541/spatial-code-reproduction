from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spatialcode_mini.dataio import read_jsonl, write_jsonl
from spatialcode_mini.inference import HFCausalLMRunner
from spatialcode_mini.parsing import parse_single_label
from spatialcode_mini.prompting import render_prompt
from spatialcode_mini.schema import Sample


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixed local HF model on the object-size set.")
    parser.add_argument("--input", type=Path, required=True, help="Input dataset JSONL.")
    parser.add_argument("--template", type=Path, required=True, help="Prompt template path.")
    parser.add_argument(
        "--condition",
        choices=["structured", "reduced"],
        required=True,
        help="Representation condition.",
    )
    parser.add_argument("--model-id", required=True, help="Hugging Face model id.")
    parser.add_argument("--output", type=Path, required=True, help="Output predictions JSONL.")
    parser.add_argument("--max-new-tokens", type=int, default=256, help="Max generated tokens.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Generation temperature.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for debugging.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.input)
    if args.limit > 0:
        records = records[: args.limit]

    runner = HFCausalLMRunner(
        model_id=args.model_id,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
    )

    predictions: list[dict] = []
    for record in records:
        sample = Sample.from_dict(record)
        prompt = render_prompt(
            sample=sample,
            template_path=args.template,
            include_size=(args.condition == "structured"),
        )
        raw_output = runner.generate(prompt)
        parsed_prediction = parse_single_label(raw_output, sample.allowed_answers)
        predictions.append(
            {
                "sample_id": sample.sample_id,
                "condition": args.condition,
                "model_id": args.model_id,
                "question": sample.question,
                "allowed_answers": sample.allowed_answers,
                "gold_answer": sample.answer,
                "raw_output": raw_output,
                "parsed_prediction": parsed_prediction,
                "is_correct": parsed_prediction == sample.answer,
            }
        )
        print(
            f"{sample.sample_id}: gold={sample.answer} "
            f"pred={parsed_prediction if parsed_prediction is not None else 'INVALID'}"
        )

    write_jsonl(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()
