import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

# Constantes
MIN_LINE_HEIGHT = 18
LINE_MERGE_DELTA = 8
PADDING_FRAC = 0.15
OPEN_VERT_H = 10
H_DILATE_MAX = 150
H_DILATE_FRAC = 0.25

_K_RULED = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
_K_OPEN_V = cv2.getStructuringElement(cv2.MORPH_RECT, (1, OPEN_VERT_H))


def enhance_image(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    clahe = cv2.createCLAHE(2.0, (8, 8))
    applied = clahe.apply(gray)

    if applied.shape[0] >= 3 and applied.shape[1] >= 3:
        grp = cv2.GaussianBlur(applied, (3, 3), 0)
    else:
        grp = applied

    return cv2.adaptiveThreshold(
        grp, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15, 2
    )


def remove_lines(image: np.ndarray, horizontal=True, vertical=True) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    bin_img = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 15, -2)

    result = image.copy()

    if horizontal:
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (60, 1))
        h_lines = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, h_kernel, iterations=2)
        result[h_lines == 255] = (255, 255, 255) if image.ndim == 3 else 255

    if vertical:
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60))
        v_lines = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, v_kernel, iterations=2)
        result[v_lines == 255] = (255, 255, 255) if image.ndim == 3 else 255

    return result


def debug_compare(original: np.ndarray, cleaned: np.ndarray, aligned: np.ndarray):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original")
    axes[1].imshow(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB))
    axes[1].set_title("Removed Lines")
    axes[2].imshow(cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB))
    axes[2].set_title("Aligned")
    for ax in axes:
        ax.axis('off')
    plt.tight_layout()
    plt.show()


def remove_ruled_lines(bin_img: np.ndarray) -> np.ndarray:
    ruled = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, _K_RULED)
    return cv2.subtract(bin_img, ruled)


def _fallback_projection(bin_img: np.ndarray):
    rows = bin_img.sum(axis=1) / 255
    smooth = gaussian_filter1d(rows, 3)
    peaks, _ = find_peaks(smooth, prominence=50)

    limits = [0] + [
        np.argmin(smooth[p:q]) + p
        for p, q in zip(peaks[:-1], peaks[1:])
    ] + [bin_img.shape[0]]

    return [
        (a, b) for a, b in zip(limits, limits[1:])
        if b - a >= MIN_LINE_HEIGHT
    ]


def detect_lines(img: np.ndarray, dbg: bool = False):
    H, W = img.shape[:2]
    bin0 = enhance_image(img)
    binary = remove_ruled_lines(bin0)

    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, _K_OPEN_V)
    kw = min(H_DILATE_MAX, int(W * H_DILATE_FRAC))
    k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (kw, 1))
    dil = cv2.dilate(opened, k2)

    n, _, stats, _ = cv2.connectedComponentsWithStats(dil)
    boxes = [
        (y, y + h)
        for _, y, w, h, _ in stats[1:]
        if h >= MIN_LINE_HEIGHT and w > W * 0.25
    ]
    boxes.sort()

    merged = []
    for y0, y1 in boxes:
        if not merged or y0 - merged[-1][1] > LINE_MERGE_DELTA:
            merged.append([y0, y1])
        else:
            merged[-1][1] = max(merged[-1][1], y1)

    if len(merged) < 3 or (len(merged) == 1 and merged[0][1] - merged[0][0] > 0.7 * H):
        merged = _fallback_projection(binary)

    pad = []
    for y0, y1 in merged:
        p = int((y1 - y0) * PADDING_FRAC)
        pad.append((max(0, y0 - p), min(H, y1 + p)))

    if dbg:
        vis = img.copy()
        for a, b in pad:
            cv2.line(vis, (0, a), (W-1, a), (255, 0, 0), 1)
            cv2.line(vis, (0, b), (W-1, b), (0, 255, 0), 1)
        plt.figure(figsize=(10, 5))
        plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

    return pad


def deskew_line_shear(line_img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(line_img, cv2.COLOR_BGR2GRAY) if line_img.ndim == 3 else line_img
    thr = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15, 2
    )
    h, w = thr.shape

    mask = thr > 0
    rev_mask = mask[::-1, :]
    rev_any = rev_mask.any(axis=0)
    first_rev = rev_mask.argmax(axis=0)
    last_line = np.where(rev_any, h - 1 - first_rev, -1).astype(np.float32)

    base = np.maximum.accumulate(last_line)
    base[base < 0] = h / 2
    base = gaussian_filter1d(base, sigma=max(1, w // 100))

    xs = np.arange(w, dtype=np.float32)
    p = np.polyfit(xs, base, 1)
    slope = p[0]

    M = np.array([[1, -slope, 0],
                  [0, 1, 0]], dtype=np.float32)
    return cv2.warpAffine(
        line_img, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


def preprocess_align(img: np.ndarray, show_debug=False) -> np.ndarray:
    cleaned = remove_lines(img, horizontal=True, vertical=True)

    H, W = img.shape[:2]
    canvas = np.full_like(img, 255)

    for y0, y1 in detect_lines(cleaned):
        block = cleaned[y0:y1, :]
        canvas[y0:y1, :] = deskew_line_shear(block)

    if show_debug:
        debug_compare(img, cleaned, canvas)

    return canvas



