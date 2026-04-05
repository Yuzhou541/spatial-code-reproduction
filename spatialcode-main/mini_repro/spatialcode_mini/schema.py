from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Object3D:
    object_id: str
    label: str
    position_3d: list[float]
    size_3d: list[float]
    orientation: list[float]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Object3D":
        return cls(
            object_id=data["id"],
            label=data["label"],
            position_3d=[float(value) for value in data["position_3d"]],
            size_3d=[float(value) for value in data["size_3d"]],
            orientation=[float(value) for value in data["orientation"]],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.object_id,
            "label": self.label,
            "position_3d": self.position_3d,
            "size_3d": self.size_3d,
            "orientation": self.orientation,
        }

    @property
    def volume(self) -> float:
        x_size, y_size, z_size = self.size_3d
        return x_size * y_size * z_size


@dataclass(frozen=True)
class Sample:
    sample_id: str
    scene_id: str
    room_type: str
    question_type: str
    size_metric: str
    question: str
    objects: list[Object3D]
    answer: str
    metadata: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sample":
        return cls(
            sample_id=data["sample_id"],
            scene_id=data["scene_id"],
            room_type=data["room_type"],
            question_type=data["question_type"],
            size_metric=data["size_metric"],
            question=data["question"],
            objects=[Object3D.from_dict(item) for item in data["objects"]],
            answer=data["answer"],
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "scene_id": self.scene_id,
            "room_type": self.room_type,
            "question_type": self.question_type,
            "size_metric": self.size_metric,
            "question": self.question,
            "objects": [obj.to_dict() for obj in self.objects],
            "answer": self.answer,
            "metadata": self.metadata,
        }

    @property
    def allowed_answers(self) -> list[str]:
        return [obj.label for obj in self.objects]
