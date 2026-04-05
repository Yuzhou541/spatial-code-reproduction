from __future__ import annotations

from pathlib import Path

from spatialcode_mini.schema import Object3D, Sample


def _format_vector(values: list[float]) -> str:
    return "[" + ", ".join(f"{value:.3f}" for value in values) + "]"


def _format_object_block(obj: Object3D, include_size: bool) -> list[str]:
    lines = [
        f"- id: {obj.object_id}",
        f"  label: {obj.label}",
        f"  position_3d: {_format_vector(obj.position_3d)}",
    ]
    if include_size:
        lines.append(f"  size_3d: {_format_vector(obj.size_3d)}")
    lines.append(f"  orientation: {_format_vector(obj.orientation)}")
    return lines


def render_spatial_code_block(sample: Sample, include_size: bool) -> str:
    lines = [
        "Scene:",
        f"- scene_id: {sample.scene_id}",
        f"- room_type: {sample.room_type}",
        f"- size_metric: {sample.size_metric}",
        "",
        "Objects:",
    ]
    for obj in sample.objects:
        lines.extend(_format_object_block(obj, include_size=include_size))
        lines.append("")
    lines.append(f"Queried objects: {', '.join(sample.allowed_answers)}")
    return "\n".join(lines).strip()


def render_prompt(sample: Sample, template_path: str | Path, include_size: bool) -> str:
    template_text = Path(template_path).read_text(encoding="utf-8")
    spatial_code_block = render_spatial_code_block(sample, include_size=include_size)
    return template_text.format(
        SPATIAL_CODE_BLOCK=spatial_code_block,
        QUESTION=sample.question,
        ALLOWED_ANSWERS=", ".join(sample.allowed_answers),
    )
