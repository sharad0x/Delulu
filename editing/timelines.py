# (start_beat, end_beat, effect_name, params) — applied in list order
# offset = seconds from clip start to the first beat

DEFAULT = {
    "offset": 0.0,
    "cues": [
        (0, 99, "color_grade", {}),
        (0, 99, "zoom_pulse", {"amount": 0.15}),
        (0, 99, "rgb_beat",   {"offset": 8}),
    ],
}

TIMELINES = {
    "edit_1": {   # beats, 129.3 BPM
        "offset": 0.30,
        "cues": [
            (0, 99,  "color_grade", {}),
            # build (0-2.16s)
            (0, 4,   "bw",          {}),
            (0, 4,   "vignette",    {"strength": 0.75}),
            (0, 4,   "zoom_ramp",   {"start": 0.0, "end": 0.3}),
            (3, 4,   "strobe",      {}),
            # drop (beat 4)
            (4, 4.6, "flash_beat",  {"intensity": 1.0}),
            (4, 4.6, "glitch",      {"max_shift": 40}),
            (4, 6,   "zoom_pulse",  {"amount": 0.12}),
            (4, 6,   "rgb_beat",    {"offset": 8}),
            # kicks (beat 6-16)
            (6, 16,  "zoom_pulse",  {"amount": 0.22}),
            (6, 16,  "shake_beat",  {"intensity": 9}),
            (6, 16,  "rgb_beat",    {"offset": 12}),
            (10, 12, "glitch",      {}),
            (11, 11.5, "invert_beat", {}),
            (12, 16, "flash_beat",  {"intensity": 0.3}),
            # climax + outro (beat 16-18, then fade)
            (16, 18, "spotlight",   {}),
            (16, 18, "zoom_ramp",   {"start": 0.25, "end": 0.0}),
            (16, 18, "shake_beat",  {"intensity": 14}),
            (18, 99, "vignette",    {"strength": 0.8}),
        ],
    },
    "edit_2": {   # seconds, uses real hit times
        "unit": "sec",
        "offset": 0.0,
        "hits": [0.58, 1.49, 1.72, 2.16, 2.37, 2.79, 3.47, 3.90, 4.57,
                 5.06, 5.69, 6.40, 7.06, 7.48, 8.16, 8.63, 9.28],
        "cues": [
            (0, 99,   "color_grade", {}),
            # build (0-2.3s)
            (0, 2.3,  "spotlight",   {}),
            (0, 2.3,  "vignette",    {"strength": 0.7}),
            (0.5, 2.3, "zoom_ramp",  {"start": 0.0, "end": 0.25}),
            (1.4, 2.3, "zoom_pulse", {"amount": 0.1}),
            # riser (2.3-2.8s)
            (2.3, 2.8, "strobe",     {}),
            (2.3, 2.8, "glitch",     {"max_shift": 25}),
            # drop (2.79s)
            (2.75, 3.2, "flash_beat", {"intensity": 1.0}),
            (2.75, 3.1, "invert_beat", {}),
            # main (2.8-8.5s)
            (2.8, 8.5, "zoom_pulse", {"amount": 0.22}),
            (2.8, 8.5, "rgb_beat",   {"offset": 14}),
            (2.8, 5.0, "shake_beat", {"intensity": 9}),
            (5.0, 5.7, "bw",         {}),
            (5.0, 5.3, "flash_beat", {"intensity": 0.6}),
            (5.7, 8.5, "glitch",     {}),
            (7.0, 8.5, "shake_beat", {"intensity": 12}),
            (8.1, 8.6, "flash_beat", {"intensity": 0.8}),
            # outro
            (8.5, 99,  "vignette",   {"strength": 0.8}),
            (8.5, 10,  "zoom_ramp",  {"start": 0.25, "end": 0.0}),
        ],
    },
    "edit_3": {   # beats, 103 BPM, ~25 beats
        "offset": 0.125,
        "fade_in": 0.2,
        "fade_out": 0.6,
        "cues": [
            # ---- shots: each cut sits 0.15 beat before the downbeat ----
            (0,     1.96, "shot", {"look": "cool",    "zoom": 1.0,  "zoom_end": 1.08}),
            (1.96,  6.14, "shot", {"look": "neutral", "zoom": 1.0,  "zoom_end": 1.06}),
            (6.14,  7.85, "shot", {"look": "warm",    "zoom": 1.0,  "zoom_end": 1.05}),
            (7.85,  8.93, "shot", {"look": "cool",    "zoom": 1.3,  "zoom_end": 1.55}),
            (8.93,  9.85, "shot", {"look": "neutral", "zoom": 1.0}),
            (9.85,  10.85, "shot", {"look": "brown",  "zoom": 1.15, "zoom_end": 1.3}),
            (10.85, 11.85, "shot", {"look": "cool",   "zoom": 1.4,  "zoom_end": 1.7}),
            (11.85, 12.85, "shot", {"look": "cool",   "zoom": 1.7,  "zoom_end": 1.8}),
            (12.85, 13.85, "shot", {"look": "warm",   "zoom": 1.3,  "zoom_end": 1.45}),
            (13.85, 14.85, "shot", {"look": "neutral", "zoom": 1.0}),
            (14.85, 15.3,  "shot", {"look": "brown",  "zoom": 1.45}),
            (15.3,  15.85, "shot", {"look": "brown",  "zoom": 1.1}),
            (15.85, 16.85, "shot", {"look": "brown",  "zoom": 1.25, "zoom_end": 1.35}),
            (16.85, 17.85, "shot", {"look": "neutral", "zoom": 1.0}),
            (17.85, 18.85, "shot", {"look": "brown",  "zoom": 1.2,  "zoom_end": 1.3}),
            (18.85, 19.85, "shot", {"look": "cool",   "zoom": 1.4,  "zoom_end": 1.7}),
            (19.85, 20.85, "shot", {"look": "cool",   "zoom": 1.7,  "zoom_end": 1.8}),
            (20.85, 21.85, "shot", {"look": "warm",   "zoom": 1.3,  "zoom_end": 1.45}),
            (21.85, 22.85, "shot", {"look": "neutral", "zoom": 1.0}),
            (22.85, 23.3,  "shot", {"look": "brown",  "zoom": 1.4}),
            (23.3,  23.85, "shot", {"look": "brown",  "zoom": 1.0}),
            (23.85, 26,    "shot", {"look": "brown",  "zoom": 1.25, "zoom_end": 1.35}),
 
            # ---- eye windows / slabs / boxes ----
            (8.25,  8.72,  "eye_window", {"style": "slab", "content": "neutral"}),
            (9.4,   9.78,  "eye_window", {"style": "slab", "content": "cool"}),
            (12.25, 12.7,  "eye_window", {"style": "box",  "content": "warm"}),
            (13.3,  13.72, "eye_window", {"style": "slab", "content": "neutral"}),
            (17.3,  17.72, "eye_window", {"style": "slab", "content": "cool"}),
            (20.3,  20.65, "eye_window", {"style": "box",  "content": "warm"}),
            (21.3,  21.8,  "eye_window", {"style": "slab", "content": "neutral"}),
 
            # ---- white head silhouettes ----
            (10.68, 10.85, "face_blob", {}),
            (14.95, 15.2,  "face_blob", {}),
            (18.65, 18.85, "face_blob", {}),
            (23.0,  23.3,  "face_blob", {}),
 
            # ---- horizontal white lines ----
            (10.9,  11.7,  "line_sweep", {}),
            (19.0,  19.7,  "line_sweep", {}),
 
            # ---- white flash on the cuts (skipped on blob beats) ----
            (7.5,   10.5,  "flash_cut", {"peak": 0.9}),
            (11.1,  18.5,  "flash_cut", {"peak": 0.9}),
            (19.1,  23.2,  "flash_cut", {"peak": 0.9}),
            (23.5,  24.3,  "flash_cut", {"peak": 0.9}),
 
            # ---- always on ----
            (0, 99, "soft_edge", {"margin": 0.04}),
        ],
    },
}