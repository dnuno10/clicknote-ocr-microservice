import os
import cv2
import torch
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


from .preprocessing import preprocess_align, detect_lines


from .trocr.model import get_model, device
from ..core.config import settings


def ocr_batch(crops, processor, model, max_new_tokens=settings.MAX_NEW_TOKENS):
    pil_imgs = []
    for c in crops:
        gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY) if c.ndim == 3 else c
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        resized = cv2.resize(rgb, (384, 384))
        pil_imgs.append(Image.fromarray(resized))


    pixel_values = processor(
        pil_imgs,
        return_tensors="pt",
        padding=True
    ).pixel_values.to(device)


    with torch.no_grad():
        ids = model.generate(pixel_values, max_new_tokens=max_new_tokens)


    return processor.batch_decode(ids, skip_special_tokens=True)

def infer_page(path: str, dbg=False) -> str:
    print(f"Loading image from:{path}")
    processor, model = get_model()
    print("Model and processor loaded correctly.")


    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {path}")


    img_aligned = preprocess_align(img, show_debug=dbg)
    print(f"Aligned image:{img_aligned.shape}")


    lines = detect_lines(img_aligned, dbg=dbg)
    print(f"Detected lines: {len(lines)}")

    crops = []
    for y0, y1 in lines:
        crops.append(img_aligned[y0:y1, :])

    print(f"Total crops (lines for OCR): {len(crops)}")

    os.makedirs("debug_crops", exist_ok=True)

    texts = ocr_batch(crops, processor, model)
    results = [t.strip() for t in texts if t.strip()]
    print(f"Model predictions: {results}")


    return "\n".join(results) if results else "No text recognized in the image."
