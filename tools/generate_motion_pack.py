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
    "idle": {"seconds": 4, "loop": True, "emotion": "neutral", "display_name": "待机", "description": "gentle breathing and weight shift"},
    "listen": {"seconds": 3, "loop": True, "emotion": "attentive", "display_name": "聆听", "description": "attentive listening pose"},
    "think": {"seconds": 3, "loop": True, "emotion": "thoughtful", "display_name": "思考", "description": "contemplative pose"},
    "speak": {"seconds": 3, "loop": True, "emotion": "engaged", "display_name": "说话", "description": "conversational gesture"},
    "nod": {"seconds": 2, "loop": False, "emotion": "affirmative", "display_name": "点头", "description": "gentle affirmative nod"},
    "wave": {"seconds": 3, "loop": False, "emotion": "happy", "display_name": "挥手", "description": "friendly greeting wave"},
    "happy": {"seconds": 3, "loop": False, "emotion": "happy", "display_name": "开心", "description": "joyful reaction"},
    "surprised": {"seconds": 2, "loop": False, "emotion": "surprised", "display_name": "惊讶", "description": "pleasant surprise"},
    "confused": {"seconds": 3, "loop": False, "emotion": "confused", "display_name": "疑惑", "description": "friendly puzzled reaction"},
    "comfort": {"seconds": 3, "loop": False, "emotion": "caring", "display_name": "安慰", "description": "reassuring gesture"},
    "goodbye": {"seconds": 3, "loop": False, "emotion": "happy", "display_name": "告别", "description": "friendly farewell wave"},
}


def render_transform(subject: Image.Image, phase: float, action: str) -> Image.Image:
    wave = math.sin(phase * math.tau)
    if action == "idle":
        scale_x, scale_y = 1.0 - 0.001 * wave, 1.0 + 0.003 * wave
        rotation, x_shift, y_shift = 0.12 * wave, 0.4 * wave, -0.8 * wave
    elif action == "listen":
        scale_x, scale_y = 1.003, 1.003
        rotation, x_shift, y_shift = 0.8 + 0.35 * wave, 2.0 + 0.8 * wave, -1.5
    elif action in {"think", "confused"}:
        scale_x, scale_y = 1.001, 1.001
        rotation, x_shift, y_shift = 0.45 * wave, 0.8 * wave, -0.5
    elif action in {"happy", "surprised"}:
        pulse = math.sin(phase * math.pi)
        scale_x, scale_y = 1.0 + 0.008 * pulse, 1.0 + 0.008 * pulse
        rotation, x_shift, y_shift = 0.15 * wave, 0.3 * wave, -4.0 * pulse
    elif action in {"wave", "goodbye"}:
        scale_x, scale_y = 1.0, 1.0
        rotation, x_shift, y_shift = 0.55 * wave, 1.1 * wave, -0.5
    elif action == "nod":
        pulse = math.sin(phase * math.pi)
        scale_x, scale_y = 1.0, 1.0 - 0.006 * pulse
        rotation, x_shift, y_shift = 0.0, 0.0, 2.0 * pulse
    elif action == "comfort":
        pulse = math.sin(phase * math.pi)
        scale_x, scale_y = 1.0 + 0.004 * pulse, 1.0 + 0.004 * pulse
        rotation, x_shift, y_shift = 0.15 * wave, 0.5 * wave, -1.0 * pulse
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
        "loop": config["loop"],
        "return_to": "idle",
        "interruptible": True,
        "emotion": config["emotion"],
        "display_name": config["display_name"],
        "menu_order": config["menu_order"],
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
    parser.add_argument("--poses-dir", type=Path)
    args = parser.parse_args()

    master = Image.open(args.master).convert("RGBA")
    for menu_order, (action, config) in enumerate(ACTION_CONFIG.items(), start=1):
        config["menu_order"] = menu_order
        pose_path = args.poses_dir / f"{action}.png" if args.poses_dir else None
        pose = Image.open(pose_path).convert("RGBA") if pose_path and pose_path.exists() else master
        subject = prepare_subject(pose)
        build_action(subject, args.output, action, config)


if __name__ == "__main__":
    main()
