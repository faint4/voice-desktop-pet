"""Build identity-stable desktop-pet micro-motion frames from one RGBA master."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image

CANVAS = (360, 640)
FPS = 24

ACTION_CONFIG = {
    "idle": {"seconds": 4, "emotion": "neutral", "description": "gentle breathing and weight shift"},
    "listen": {"seconds": 3, "emotion": "attentive", "description": "subtle attentive lean and sway"},
    "speak": {"seconds": 3, "emotion": "engaged", "description": "conversational body rhythm"},
}


def render_transform(subject: Image.Image, phase: float, action: str) -> Image.Image:
    wave = math.sin(phase * math.tau)
    if action == "idle":
        scale_x, scale_y = 1.0 - 0.001 * wave, 1.0 + 0.003 * wave
        rotation, x_shift, y_shift = 0.12 * wave, 0.4 * wave, -0.8 * wave
    elif action == "listen":
        scale_x, scale_y = 1.003, 1.003
        rotation, x_shift, y_shift = 0.8 + 0.35 * wave, 2.0 + 0.8 * wave, -1.5
    else:
        scale_x, scale_y = 1.0 + 0.002 * wave, 1.0 + 0.005 * wave
        rotation, x_shift, y_shift = 0.32 * wave, 1.2 * wave, -1.2 * abs(wave)

    width = round(subject.width * scale_x)
    height = round(subject.height * scale_y)
    transformed = subject.resize((width, height), Image.Resampling.LANCZOS)
    transformed = transformed.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    x = round((CANVAS[0] - transformed.width) / 2 + x_shift)
    y = round(CANVAS[1] - transformed.height - 8 + y_shift)
    canvas.alpha_composite(transformed, (x, y))
    return canvas


def prepare_subject(master: Image.Image) -> Image.Image:
    alpha_box = master.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError("The master image has no visible alpha content")
    cropped = master.crop(alpha_box)
    scale = min(332 / cropped.width, 608 / cropped.height)
    size = (round(cropped.width * scale), round(cropped.height * scale))
    return cropped.resize(size, Image.Resampling.LANCZOS)


def build_action(subject: Image.Image, output_root: Path, action: str, config: dict) -> None:
    action_dir = output_root / action
    action_dir.mkdir(parents=True, exist_ok=True)
    frame_count = round(config["seconds"] * FPS)
    first_frame: Image.Image | None = None
    for index in range(frame_count):
        # Exact matching endpoints make the final-to-first loop seam invisible.
        phase = index / (frame_count - 1)
        frame = first_frame.copy() if index == frame_count - 1 else render_transform(subject, phase, action)
        if first_frame is None:
            first_frame = frame.copy()
        frame.save(action_dir / f"frame_{index + 1:04d}.png", optimize=True)

    metadata = {
        "id": action,
        "fps": FPS,
        "frame_count": frame_count,
        "loop": True,
        "return_to": "idle",
        "interruptible": True,
        "emotion": config["emotion"],
        "description": config["description"],
        "generator": "tools/generate_motion_pack.py",
    }
    (action_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    master = Image.open(args.master).convert("RGBA")
    subject = prepare_subject(master)
    for action, config in ACTION_CONFIG.items():
        build_action(subject, args.output, action, config)


if __name__ == "__main__":
    main()
