from __future__ import annotations

import re


_NON_LABEL_CHARS = re.compile(r"[^a-z0-9_]+")
_FINAL_ANSWER_PATTERN = re.compile(r"final\s+answer\s*:\s*([^\n\r]+)", re.IGNORECASE)


def normalize_label(text: str) -> str:
    return _NON_LABEL_CHARS.sub("_", text.strip().lower()).strip("_")


def parse_single_label(raw_output: str, allowed_answers: list[str]) -> str | None:
    allowed_map = {normalize_label(answer): answer for answer in allowed_answers}
    candidate = normalize_label(raw_output)
    if candidate in allowed_map:
        return allowed_map[candidate]

    match = _FINAL_ANSWER_PATTERN.search(raw_output)
    if not match:
        return None

    final_answer = normalize_label(match.group(1))
    return allowed_map.get(final_answer)
