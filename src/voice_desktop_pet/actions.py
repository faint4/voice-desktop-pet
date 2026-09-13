"""Action-pack metadata and playback policy."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ActionSpec:
    """Runtime behavior for one frame-sequence action."""

    name: str
    fps: float = 24.0
    loop: bool = True
    return_to: str = "idle"
    interruptible: bool = True
    emotion: str = "neutral"

    @property
    def interval_ms(self) -> int:
        return max(1, round(1000 / self.fps))


def load_action_spec(action_dir: Path) -> ActionSpec:
    """Load optional metadata while remaining compatible with legacy folders."""

    metadata_path = action_dir / "metadata.json"
    if not metadata_path.exists():
        return ActionSpec(name=action_dir.name)

    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    return ActionSpec(
        name=str(data.get("id", action_dir.name)),
        fps=float(data.get("fps", 24.0)),
        loop=bool(data.get("loop", True)),
        return_to=str(data.get("return_to", "idle")),
        interruptible=bool(data.get("interruptible", True)),
        emotion=str(data.get("emotion", "neutral")),
    )


def discover_actions(actions_dir: Path) -> list[str]:
    """Return playable action directories in stable order."""

    if not actions_dir.exists():
        return []
    return sorted(
        path.name
        for path in actions_dir.iterdir()
        if path.is_dir() and any(path.glob("*.png"))
    )
