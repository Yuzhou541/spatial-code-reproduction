from __future__ import annotations

import argparse
import itertools
import math
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spatialcode_mini.dataio import write_jsonl
from spatialcode_mini.metrics import difficulty_bucket


QUESTION_TEMPLATES = [
    "Which object has the larger 3D volume, the {a} or the {b}?",
    "Between the {a} and the {b}, which object is larger?",
    "Compare the 3D sizes of the {a} and the {b}. Which one is larger?",
]


def yaw_quaternion(yaw_degrees: float) -> list[float]:
    yaw_radians = math.radians(yaw_degrees)
    half_yaw = yaw_radians / 2.0
    return [0.0, 0.0, round(math.sin(half_yaw), 6), round(math.cos(half_yaw), 6)]


SCENE_BANK = [
    {
        "scene_id": "living_room_a",
        "room_type": "living_room",
        "objects": [
            {"label": "sofa", "position_3d": [1.10, 0.48, 2.30], "size_3d": [2.10, 0.95, 0.88], "yaw": 90},
            {"label": "coffee_table", "position_3d": [1.95, 0.28, 2.10], "size_3d": [1.20, 0.55, 0.45], "yaw": 0},
            {"label": "armchair", "position_3d": [0.35, 0.48, 1.75], "size_3d": [0.90, 0.95, 0.90], "yaw": 35},
            {"label": "floor_lamp", "position_3d": [2.70, 0.85, 1.65], "size_3d": [0.35, 0.35, 1.70], "yaw": 0},
            {"label": "bookshelf", "position_3d": [3.10, 0.95, 2.75], "size_3d": [1.00, 0.35, 1.90], "yaw": 90},
        ],
    },
    {
        "scene_id": "kitchen_a",
        "room_type": "kitchen",
        "objects": [
            {"label": "refrigerator", "position_3d": [0.40, 0.90, 0.60], "size_3d": [0.90, 0.80, 1.80], "yaw": 0},
            {"label": "oven", "position_3d": [1.60, 0.45, 0.70], "size_3d": [0.76, 0.72, 0.90], "yaw": 0},
            {"label": "dining_chair", "position_3d": [2.60, 0.42, 1.30], "size_3d": [0.50, 0.55, 0.85], "yaw": 180},
            {"label": "kitchen_island", "position_3d": [2.10, 0.48, 2.35], "size_3d": [1.60, 0.90, 0.95], "yaw": 90},
            {"label": "trash_bin", "position_3d": [3.00, 0.30, 0.85], "size_3d": [0.35, 0.35, 0.65], "yaw": 0},
        ],
    },
    {
        "scene_id": "bedroom_a",
        "room_type": "bedroom",
        "objects": [
            {"label": "bed", "position_3d": [1.50, 0.30, 2.10], "size_3d": [2.05, 1.65, 0.60], "yaw": 90},
            {"label": "nightstand", "position_3d": [2.65, 0.28, 1.40], "size_3d": [0.50, 0.45, 0.55], "yaw": 0},
            {"label": "dresser", "position_3d": [0.30, 0.55, 0.85], "size_3d": [1.20, 0.55, 1.00], "yaw": 0},
            {"label": "desk_lamp", "position_3d": [0.55, 0.72, 0.95], "size_3d": [0.25, 0.25, 0.50], "yaw": 0},
            {"label": "wardrobe", "position_3d": [3.10, 1.00, 2.80], "size_3d": [1.50, 0.65, 2.00], "yaw": 90},
        ],
    },
    {
        "scene_id": "bathroom_a",
        "room_type": "bathroom",
        "objects": [
            {"label": "bathtub", "position_3d": [0.85, 0.30, 1.10], "size_3d": [1.70, 0.80, 0.60], "yaw": 0},
            {"label": "sink_cabinet", "position_3d": [2.10, 0.43, 0.65], "size_3d": [0.90, 0.50, 0.85], "yaw": 0},
            {"label": "toilet", "position_3d": [2.90, 0.38, 1.85], "size_3d": [0.70, 0.45, 0.75], "yaw": 90},
            {"label": "laundry_basket", "position_3d": [1.60, 0.32, 2.35], "size_3d": [0.55, 0.55, 0.65], "yaw": 0},
            {"label": "mirror_cabinet", "position_3d": [2.10, 1.30, 0.65], "size_3d": [0.80, 0.18, 0.90], "yaw": 0},
        ],
    },
    {
        "scene_id": "office_a",
        "room_type": "office",
        "objects": [
            {"label": "office_desk", "position_3d": [1.40, 0.40, 1.95], "size_3d": [1.40, 0.70, 0.76], "yaw": 90},
            {"label": "swivel_chair", "position_3d": [1.20, 0.50, 1.05], "size_3d": [0.70, 0.70, 1.05], "yaw": 45},
            {"label": "filing_cabinet", "position_3d": [0.25, 0.66, 2.80], "size_3d": [0.46, 0.62, 1.32], "yaw": 0},
            {"label": "printer_stand", "position_3d": [2.75, 0.36, 2.50], "size_3d": [0.60, 0.45, 0.72], "yaw": 0},
            {"label": "whiteboard", "position_3d": [3.20, 1.15, 1.40], "size_3d": [1.40, 0.10, 1.00], "yaw": 90},
        ],
    },
    {
        "scene_id": "garage_a",
        "room_type": "garage",
        "objects": [
            {"label": "suv", "position_3d": [2.60, 0.85, 3.40], "size_3d": [4.60, 1.90, 1.70], "yaw": 90},
            {"label": "workbench", "position_3d": [0.60, 0.48, 1.05], "size_3d": [1.80, 0.75, 0.95], "yaw": 0},
            {"label": "toolbox", "position_3d": [0.95, 0.22, 0.95], "size_3d": [0.65, 0.35, 0.40], "yaw": 0},
            {"label": "bicycle", "position_3d": [4.20, 0.60, 1.20], "size_3d": [1.75, 0.25, 1.10], "yaw": 90},
            {"label": "ladder", "position_3d": [5.00, 0.90, 2.20], "size_3d": [0.45, 0.15, 1.80], "yaw": 75},
        ],
    },
    {
        "scene_id": "classroom_a",
        "room_type": "classroom",
        "objects": [
            {"label": "teacher_desk", "position_3d": [1.25, 0.42, 1.70], "size_3d": [1.40, 0.75, 0.76], "yaw": 90},
            {"label": "student_chair", "position_3d": [2.60, 0.40, 1.15], "size_3d": [0.48, 0.52, 0.82], "yaw": 0},
            {"label": "bookshelf", "position_3d": [0.30, 0.85, 3.10], "size_3d": [0.95, 0.32, 1.70], "yaw": 90},
            {"label": "podium", "position_3d": [1.80, 0.58, 0.85], "size_3d": [0.62, 0.50, 1.15], "yaw": 0},
            {"label": "whiteboard", "position_3d": [3.40, 1.10, 3.40], "size_3d": [2.20, 0.12, 1.20], "yaw": 90},
        ],
    },
    {
        "scene_id": "dining_room_a",
        "room_type": "dining_room",
        "objects": [
            {"label": "dining_table", "position_3d": [1.85, 0.40, 1.95], "size_3d": [1.80, 0.95, 0.76], "yaw": 0},
            {"label": "sideboard", "position_3d": [0.35, 0.48, 3.15], "size_3d": [1.60, 0.45, 0.90], "yaw": 90},
            {"label": "bar_stool", "position_3d": [2.90, 0.39, 0.95], "size_3d": [0.42, 0.42, 0.78], "yaw": 0},
            {"label": "serving_cart", "position_3d": [3.35, 0.41, 2.80], "size_3d": [0.75, 0.45, 0.82], "yaw": 0},
            {"label": "potted_plant", "position_3d": [0.85, 0.55, 0.75], "size_3d": [0.50, 0.50, 1.10], "yaw": 0},
        ],
    },
    {
        "scene_id": "studio_a",
        "room_type": "studio",
        "objects": [
            {"label": "couch", "position_3d": [1.10, 0.46, 2.45], "size_3d": [1.95, 0.90, 0.88], "yaw": 90},
            {"label": "easel", "position_3d": [2.90, 0.82, 1.60], "size_3d": [0.70, 0.60, 1.65], "yaw": 15},
            {"label": "tripod", "position_3d": [3.25, 0.78, 2.40], "size_3d": [0.70, 0.70, 1.55], "yaw": 0},
            {"label": "storage_shelf", "position_3d": [0.30, 0.92, 3.05], "size_3d": [1.10, 0.38, 1.85], "yaw": 90},
            {"label": "stool", "position_3d": [2.05, 0.34, 0.95], "size_3d": [0.38, 0.38, 0.68], "yaw": 0},
        ],
    },
    {
        "scene_id": "playroom_a",
        "room_type": "playroom",
        "objects": [
            {"label": "play_table", "position_3d": [1.50, 0.30, 1.85], "size_3d": [1.10, 0.65, 0.55], "yaw": 0},
            {"label": "toy_box", "position_3d": [0.55, 0.25, 2.60], "size_3d": [0.80, 0.45, 0.50], "yaw": 0},
            {"label": "slide", "position_3d": [2.95, 0.48, 2.95], "size_3d": [1.55, 0.65, 0.95], "yaw": 90},
            {"label": "bean_bag", "position_3d": [2.30, 0.38, 0.85], "size_3d": [0.85, 0.80, 0.70], "yaw": 0},
            {"label": "cube_shelf", "position_3d": [0.30, 0.68, 1.15], "size_3d": [1.20, 0.32, 1.25], "yaw": 90},
        ],
    },
]


def volume(size_3d: list[float]) -> float:
    return size_3d[0] * size_3d[1] * size_3d[2]


def build_records(ambiguity_ratio_threshold: float) -> list[dict]:
    records: list[dict] = []
    sample_index = 0
    for scene in SCENE_BANK:
        scene_id = scene["scene_id"]
        room_type = scene["room_type"]
        objects = []
        for raw_object in scene["objects"]:
            objects.append(
                {
                    "id": f"{scene_id}_{raw_object['label']}",
                    "label": raw_object["label"],
                    "position_3d": raw_object["position_3d"],
                    "size_3d": raw_object["size_3d"],
                    "orientation": yaw_quaternion(raw_object["yaw"]),
                }
            )

        for left, right in itertools.combinations(objects, 2):
            left_volume = volume(left["size_3d"])
            right_volume = volume(right["size_3d"])
            size_ratio = max(left_volume, right_volume) / min(left_volume, right_volume)
            if size_ratio < ambiguity_ratio_threshold:
                continue

            sample_index += 1
            answer = left["label"] if left_volume > right_volume else right["label"]
            question_template = QUESTION_TEMPLATES[(sample_index - 1) % len(QUESTION_TEMPLATES)]
            question = question_template.format(a=left["label"], b=right["label"])
            bucket = difficulty_bucket(size_ratio)

            records.append(
                {
                    "sample_id": f"{scene_id}_q_{sample_index:03d}",
                    "scene_id": scene_id,
                    "room_type": room_type,
                    "question_type": "object_size",
                    "size_metric": "bbox_volume",
                    "question": question,
                    "objects": [left, right],
                    "answer": answer,
                    "metadata": {
                        "volumes": {
                            left["label"]: round(left_volume, 6),
                            right["label"]: round(right_volume, 6),
                        },
                        "size_ratio": round(size_ratio, 6),
                        "difficulty_bucket": bucket,
                    },
                }
            )
    return records


def build_small_split(records: list[dict], small_count: int, seed: int) -> list[dict]:
    random.seed(seed)
    buckets: dict[str, list[dict]] = {"hard": [], "medium": [], "easy": []}
    for record in records:
        buckets[record["metadata"]["difficulty_bucket"]].append(record)
    for bucket_records in buckets.values():
        random.shuffle(bucket_records)

    picked: list[dict] = []
    bucket_order = ["hard", "medium", "easy"]
    cursor = 0
    while len(picked) < small_count:
        bucket_name = bucket_order[cursor % len(bucket_order)]
        if buckets[bucket_name]:
            picked.append(buckets[bucket_name].pop())
        cursor += 1
        if not any(buckets.values()):
            break
    picked.sort(key=lambda item: item["sample_id"])
    return picked


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the object-size evaluation subsets.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "object_size_eval.jsonl",
        help="Path for the main evaluation JSONL.",
    )
    parser.add_argument(
        "--small-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "object_size_eval_small.jsonl",
        help="Path for the pilot evaluation JSONL.",
    )
    parser.add_argument(
        "--ambiguity-ratio-threshold",
        type=float,
        default=1.10,
        help="Filter out near ties below this size ratio.",
    )
    parser.add_argument(
        "--small-count",
        type=int,
        default=10,
        help="Number of pilot samples to keep.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for pilot split selection.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = build_records(ambiguity_ratio_threshold=args.ambiguity_ratio_threshold)
    small_records = build_small_split(records=records, small_count=args.small_count, seed=args.seed)

    write_jsonl(args.output, records)
    write_jsonl(args.small_output, small_records)

    print(f"Wrote {len(records)} records to {args.output}")
    print(f"Wrote {len(small_records)} pilot records to {args.small_output}")


if __name__ == "__main__":
    main()
