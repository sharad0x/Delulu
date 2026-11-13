
import cv2
import numpy as np
import random
from editing.timelines import TIMELINES, DEFAULT
from editing.reel_fx import REEL_EFFECTS
DEBUG = True   # True = show beat position overlay for tuning cues

def get_effect_bbox(frame, face_bbox):

    x, y, w, h = face_bbox

    # Expand effect region
    new_w = int(w * 1.4)
    new_h = int(h * 10.6)

    # Center around face
    cx = x + w // 2
    cy = y + h // 2

    x1 = max(0, cx - new_w // 2)
    y1 = max(0, cy - new_h // 2)

    x2 = min(frame.shape[1], cx + new_w // 2)
    y2 = min(frame.shape[0], cy + new_h // 2)

    return x1, y1, x2, y2


# ==========================================
# ZOOM
# ==========================================

def apply_zoom(frame, bbox, amount):

    x1, y1, x2, y2 = get_effect_bbox(
        frame, bbox
    )

    roi = frame[y1:y2, x1:x2]

    if roi.size == 0:
        return frame

    rh, rw = roi.shape[:2]

    factor = 1.0 + amount

    new_w = max(1, int(rw / factor))
    new_h = max(1, int(rh / factor))

    cx, cy = rw // 2, rh // 2

    sx = max(0, cx - new_w // 2)
    sy = max(0, cy - new_h // 2)

    cropped = roi[
        sy:sy + new_h,
        sx:sx + new_w
    ]

    zoomed = cv2.resize(
        cropped,
        (rw, rh),
        interpolation=cv2.INTER_LINEAR
    )

    frame[y1:y2, x1:x2] = zoomed

    return frame


# ==========================================
# SHAKE
# ==========================================

def apply_shake(frame, intensity):

    dx = random.randint(-intensity, intensity)
    dy = random.randint(-intensity, intensity)

    matrix = np.float32([
        [1, 0, dx],
        [0, 1, dy]
    ])

    return cv2.warpAffine(
        frame,
        matrix,
        (frame.shape[1], frame.shape[0])
    )


# ==========================================
# FLASH
# ==========================================

def apply_flash(frame, intensity):

    overlay = np.full_like(frame, 255)

    return cv2.addWeighted(
        frame,
        1 - intensity,
        overlay,
        intensity,
        0
    )


# ==========================================
# RGB SPLIT
# ==========================================

def apply_rgb_split(frame, bbox, offset=8):

    x1, y1, x2, y2 = get_effect_bbox(
        frame, bbox
    )

    roi = frame[y1:y2, x1:x2].copy()

    if roi.size == 0:
        return frame

    blue, green, red = cv2.split(roi)

    red = np.roll(red, offset, axis=1)
    blue = np.roll(blue, -offset, axis=1)

    frame[y1:y2, x1:x2] = cv2.merge([
        blue,
        green,
        red
    ])

    return frame


# ==========================================
# COLOR GRADING
# ==========================================

def apply_color_grade(frame):

    graded = cv2.convertScaleAbs(
        frame,
        alpha=1.18,
        beta=5
    )

    hsv = cv2.cvtColor(
        graded,
        cv2.COLOR_BGR2HSV
    )

    hsv[:, :, 1] = np.clip(
        hsv[:, :, 1].astype(np.float32) * 1.25,
        0,
        255
    ).astype(np.uint8)

    return cv2.cvtColor(
        hsv,
        cv2.COLOR_HSV2BGR
    )


# ==========================================
# BEAT-DRIVEN EFFECTS  (signature: frame, bbox, ctx, **params)
# ctx: beat_pos, beat_phase (0-1 in beat), t (0-1 in cue), elapsed
# ==========================================

def beat_env(ctx, decay=0.4):
    # 1.0 on beat hit -> 0.0 after `decay` of a beat
    return max(0.0, 1.0 - ctx["beat_phase"] / decay)


def fx_color_grade(frame, bbox, ctx):
    return apply_color_grade(frame)


def fx_zoom_pulse(frame, bbox, ctx, amount=0.15):
    return apply_zoom(frame, bbox, amount * beat_env(ctx))


def fx_zoom_ramp(frame, bbox, ctx, start=0.0, end=0.3):
    return apply_zoom(frame, bbox, start + (end - start) * ctx["t"])


def fx_shake_beat(frame, bbox, ctx, intensity=8):
    return apply_shake(frame, int(intensity * beat_env(ctx)))


def fx_rgb_beat(frame, bbox, ctx, offset=10):
    return apply_rgb_split(frame, bbox, int(offset * beat_env(ctx)))


def fx_flash_beat(frame, bbox, ctx, intensity=0.5):
    return apply_flash(frame, min(1.0, intensity * beat_env(ctx)))


def fx_bw(frame, bbox, ctx):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def fx_invert_beat(frame, bbox, ctx):
    return cv2.bitwise_not(frame) if beat_env(ctx) > 0.6 else frame


def fx_strobe(frame, bbox, ctx):
    # alternate bright/dark every half beat
    if int(ctx["beat_pos"] * 2) % 2 == 0:
        return cv2.convertScaleAbs(frame, alpha=1.0, beta=60)
    return cv2.convertScaleAbs(frame, alpha=0.6, beta=0)


def fx_glitch(frame, bbox, ctx, slices=6, max_shift=30):
    if beat_env(ctx) <= 0:
        return frame
    h = frame.shape[0]
    for _ in range(slices):
        y = random.randint(0, h - 1)
        sh = random.randint(5, max(6, h // 12))
        dx = random.randint(-max_shift, max_shift)
        frame[y:y + sh] = np.roll(frame[y:y + sh], dx, axis=1)
    return frame


_vig_cache = {}

def fx_vignette(frame, bbox, ctx, strength=0.6):
    h, w = frame.shape[:2]
    key = (h, w, strength)
    if key not in _vig_cache:
        ys, xs = np.ogrid[:h, :w]
        d = np.sqrt(((xs - w / 2) / (w / 2)) ** 2 + ((ys - h / 2) / (h / 2)) ** 2)
        _vig_cache[key] = (1 - strength * np.clip(d, 0, 1) ** 2)[..., None].astype(np.float32)
    return (frame * _vig_cache[key]).astype(np.uint8)


def fx_spotlight(frame, bbox, ctx):
    x, y, w, h = bbox
    mask = np.zeros(frame.shape[:2], np.float32)
    cv2.ellipse(mask, (x + w // 2, y + h // 2), (int(w * 0.9), int(h * 1.1)),
                0, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 35)[..., None]
    dark = (frame * 0.25).astype(np.float32)
    return (frame * mask + dark * (1 - mask)).astype(np.uint8)


EFFECTS = {
    "color_grade": fx_color_grade,
    "zoom_pulse":  fx_zoom_pulse,
    "zoom_ramp":   fx_zoom_ramp,
    "shake_beat":  fx_shake_beat,
    "rgb_beat":    fx_rgb_beat,
    "flash_beat":  fx_flash_beat,
    "bw":          fx_bw,
    "invert_beat": fx_invert_beat,
    "strobe":      fx_strobe,
    "glitch":      fx_glitch,
    "vignette":    fx_vignette,
    "spotlight":   fx_spotlight,
}
EFFECTS.update(REEL_EFFECTS)


# ==========================================
# TEMPLATE EFFECT ENGINE
# ==========================================

FADE_IN = 2.5    # matches afade in ffmpeg cmd
FADE_OUT = 1.5


def apply_template(frame, bbox, elapsed, template):

    tl = TIMELINES.get(template["name"], DEFAULT)

    beat_interval = 60.0 / template["bpm"]
    beat_pos = max(0.0, (elapsed - tl["offset"]) / beat_interval)

    pos = elapsed if tl.get("unit") == "sec" else beat_pos

    beat_phase = beat_pos % 1.0
    hits = tl.get("hits")
    if hits:
        past = [h for h in hits if h <= elapsed]
        beat_phase = min(1.0, (elapsed - past[-1]) / beat_interval) if past else 1.0

    ctx = {
        "elapsed": elapsed,
        "beat_pos": beat_pos,
        "beat_phase": beat_phase,
        "t": 0.0,
    }

    for start, end, name, params in tl["cues"]:
        if start <= pos < end:
            ctx["t"] = (pos - start) / (end - start)
            frame = EFFECTS[name](frame, bbox, ctx, **params)

    # fade in / out to match audio
    fade_in = tl.get("fade_in", FADE_IN)
    fade_out = tl.get("fade_out", FADE_OUT)
    remaining = template["duration"] - elapsed
    fade = min(1.0, elapsed / fade_in + 0.3, remaining / fade_out)
    if fade < 1.0:
        frame = cv2.convertScaleAbs(frame, alpha=max(0.0, fade))

    if DEBUG:
        cv2.putText(frame, f"t={elapsed:.2f} beat={beat_pos:.1f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame