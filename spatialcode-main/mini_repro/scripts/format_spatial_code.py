from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spatialcode_mini.dataio import read_jsonl
from spatialcode_mini.prompting import render_prompt
from spatialcode_mini.schema import Sample


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render one sample into a spatial-code prompt.")
    parser.add_argument("--input", type=Path, required=True, help="Input JSONL dataset.")
    parser.add_argument("--sample-id", required=True, help="Sample id to render.")
    parser.add_argument("--template", type=Path, required=True, help="Prompt template path.")
    parser.add_argument(
        "--condition",
        choices=["structured", "reduced"],
        required=True,
        help="Whether to include size_3d in the spatial code.",
    )
    parser.add_argument("--output", type=Path, help="Optional output text file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.input)
    target = next((record for record in records if record["sample_id"] == args.sample_id), None)
    if target is None:
        available = ", ".join(record["sample_id"] for record in records[:10])
        raise SystemExit(f"Sample id not found: {args.sample_id}. First available ids: {available}")

    sample = Sample.from_dict(target)
    prompt = render_prompt(
        sample=sample,
        template_path=args.template,
        include_size=(args.condition == "structured"),
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(prompt, encoding="utf-8")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
