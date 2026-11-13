import cv2
import numpy as np


# signature for every effect: fn(frame, bbox, ctx, **params)
# ctx: beat_pos, beat_phase, t (0-1 progress inside the cue), elapsed


# ==========================================
# HELPERS
# ==========================================

LOOKS = {  # gain is BGR
    "cool":    {"gain": (1.28, 1.00, 0.82), "sat": 1.10, "contrast": 1.12},
    "warm":    {"gain": (0.62, 0.92, 1.35), "sat": 1.35, "contrast": 1.10},
    "neutral": {"gain": (1.00, 1.00, 1.00), "sat": 1.15, "contrast": 1.08},
    "brown":   {"gain": (0.85, 0.97, 1.12), "sat": 1.05, "contrast": 1.10},
}

_lut_cache = {}
_edge_cache = {}


def _look_lut(name):
    if name not in _lut_cache:
        p = LOOKS[name]
        x = np.arange(256, dtype=np.float32)
        lut = np.stack(
            [np.clip((x * g - 128) * p["contrast"] + 128, 0, 255)
             for g in p["gain"]],
            axis=1
        )
        _lut_cache[name] = lut.astype(np.uint8).reshape(256, 1, 3)
    return _lut_cache[name]


def grade(frame, name):
    out = cv2.LUT(frame, _look_lut(name))
    s = LOOKS[name]["sat"]
    gray = cv2.cvtColor(
        cv2.cvtColor(out, cv2.COLOR_BGR2GRAY),
        cv2.COLOR_GRAY2BGR
    )
    return cv2.addWeighted(out, s, gray, 1 - s, 0)


def scale_about(frame, cx, cy, z):
    # full-frame zoom anchored on (cx, cy); z >= 1 never leaves the image
    if abs(z - 1.0) < 1e-3:
        return frame
    h, w = frame.shape[:2]
    M = np.float32([[z, 0, cx * (1 - z)],
                    [0, z, cy * (1 - z)]])
    return cv2.warpAffine(
        frame, M, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )


# ==========================================
# SHOT  (stands in for the reel's clip cuts:
# each "shot" = different grade + framing)
# ==========================================

def fx_shot(frame, bbox, ctx, look="neutral", zoom=1.0, zoom_end=None):
    x, y, w, h = bbox
    z = zoom if zoom_end is None else zoom + (zoom_end - zoom) * ctx["t"]
    frame = scale_about(frame, x + w / 2, y + h / 2, z)
    return grade(frame, look)


# ==========================================
# SOFT FEATHERED EDGE (reel's blurred frame border)
# ==========================================

def fx_soft_edge(frame, bbox, ctx, margin=0.04):
    h, w = frame.shape[:2]
    key = (h, w, margin)
    if key not in _edge_cache:
        m = max(2, int(min(h, w) * margin))
        mask = np.zeros((h, w), np.float32)
        mask[m:h - m, m:w - m] = 1.0
        k = m * 2 + 1
        mask = cv2.GaussianBlur(mask, (k, k), m * 0.6)
        _edge_cache[key] = mask[..., None]
    return (frame * _edge_cache[key]).astype(np.uint8)


# ==========================================
# WHITE FLASH TRANSITION
# peaks 0.2 beat BEFORE each beat, gone 0.1 beat after
# (the shot cut sits right at the peak)
# ==========================================

def _cut_flash_env(p):
    if 0.55 <= p < 0.8:
        return (p - 0.55) / 0.25
    if p >= 0.8:
        return 1 - (p - 0.8) / 0.3
    if p < 0.1:
        return 1 - (p + 0.2) / 0.3
    return 0.0


def fx_flash_cut(frame, bbox, ctx, peak=0.9):
    a = _cut_flash_env(ctx["beat_pos"] % 1.0) * peak
    if a <= 0:
        return frame
    return cv2.addWeighted(frame, 1 - a, np.full_like(frame, 255), a, 0)


# ==========================================
# WHITE HEAD SILHOUETTE (used instead of a flash on some cuts)
# ==========================================

def fx_face_blob(frame, bbox, ctx):
    x, y, w, h = bbox
    a = min(1.0, ctx["t"] * 2.5)
    mask = np.zeros(frame.shape[:2], np.uint8)
    cv2.ellipse(
        mask,
        (x + w // 2, y + int(h * 0.45)),
        (int(w * 0.62), int(h * 0.85)),
        0, 0, 360, 255, -1
    )
    mask = cv2.GaussianBlur(mask, (0, 0), 3).astype(np.float32)[..., None] / 255 * a
    return (frame * (1 - mask) + 255 * mask).astype(np.uint8)


# ==========================================
# HORIZONTAL WHITE LINES SWEEPING DOWN
# ==========================================

def fx_line_sweep(frame, bbox, ctx, thickness=0.012):
    h = frame.shape[0]
    t = ctx["t"]
    th = max(2, int(h * thickness))
    for pos in (0.16 + 0.14 * t, 0.52 + 0.32 * t):
        y = int(h * pos)
        frame[y:y + th] = 255
    return frame


# ==========================================
# EYE WINDOW
# style "slab": slanted white slab wipes in, then shows an alternate
#               zoomed/graded copy of the eye area with a white outline
# style "box" : near-flat box over the eyes, black outline, graded copy
# content: a LOOKS name, "bw" or "invert"
# ==========================================

def fx_eye_window(frame, bbox, ctx, style="slab", content="neutral", zoom=1.8):
    x, y, w, h = bbox
    H, W = frame.shape[:2]
    t = ctx["t"]

    cx, cy = x + w / 2, y + h * 0.38

    if style == "slab":
        bw, bh, tilt, skew = w * 1.7, h * 0.30, -12, 0.45
        reveal = min(1.0, t / 0.35)
    else:
        bw, bh, tilt, skew = w * 1.8, h * 0.34, -4, 0.0
        reveal = 1.0

    pts = np.array([
        [-bw / 2, bh / 2],
        [-bw / 2, -bh / 2],
        [-bw / 2 + bw * reveal, -bh / 2],
        [-bw / 2 + bw * reveal, bh / 2],
    ], np.float32)

    pts[:, 0] -= skew * pts[:, 1]

    a = np.deg2rad(tilt)
    R = np.array([[np.cos(a), -np.sin(a)],
                  [np.sin(a), np.cos(a)]], np.float32)

    poly = (pts @ R.T + np.array([cx, cy], np.float32)).astype(np.int32)

    mask = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(mask, poly, 255)
    m = mask > 0

    if style == "slab" and t < 0.35:
        frame[m] = 255
    else:
        alt = scale_about(frame, cx, cy, zoom)
        if content == "bw":
            g = cv2.cvtColor(alt, cv2.COLOR_BGR2GRAY)
            alt = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        elif content == "invert":
            alt = cv2.bitwise_not(alt)
        else:
            alt = grade(alt, content)

        if style == "box" and t < 0.3:
            alt = cv2.addWeighted(alt, 0.4, np.full_like(alt, 255), 0.6, 0)

        frame[m] = alt[m]

    if style == "slab":
        cv2.polylines(frame, [poly], True, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        cv2.polylines(frame, [poly], True, (0, 0, 0), 6, cv2.LINE_AA)

    return frame


REEL_EFFECTS = {
    "shot":        fx_shot,
    "soft_edge":   fx_soft_edge,
    "flash_cut":   fx_flash_cut,
    "face_blob":   fx_face_blob,
    "line_sweep":  fx_line_sweep,
    "eye_window":  fx_eye_window,
}
