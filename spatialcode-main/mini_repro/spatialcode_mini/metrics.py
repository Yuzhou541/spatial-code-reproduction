from __future__ import annotations


def difficulty_bucket(size_ratio: float) -> str:
    if size_ratio >= 2.0:
        return "easy"
    if size_ratio >= 1.5:
        return "medium"
    return "hard"
