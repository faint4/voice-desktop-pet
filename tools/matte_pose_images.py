"""Extract people from generated pose images with the local U2Net model."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter


def mask_for(session: ort.InferenceSession, image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    resized = rgb.resize((320, 320), Image.Resampling.LANCZOS)
    values = np.asarray(resized, dtype=np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    tensor = ((values - mean) / std).transpose(2, 0, 1)[None]
    prediction = session.run(None, {session.get_inputs()[0].name: tensor})[0][:, 0]
    prediction = np.squeeze(prediction)
    lo, hi = float(prediction.min()), float(prediction.max())
    normalized = np.zeros_like(prediction) if hi - lo < 1e-6 else (prediction - lo) / (hi - lo)
    mask = Image.fromarray((normalized.clip(0, 1) * 255).astype(np.uint8))
    return mask.resize(rgb.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    session = ort.InferenceSession(
        str(args.model), providers=["DmlExecutionProvider", "CPUExecutionProvider"]
    )
    for source in sorted(args.input_dir.glob("*.png")):
        image = Image.open(source).convert("RGB")
        image.putalpha(mask_for(session, image))
        destination = args.output_dir / source.name
        image.save(destination, optimize=True)
        print(f"matted: {source.name}", flush=True)


if __name__ == "__main__":
    main()
