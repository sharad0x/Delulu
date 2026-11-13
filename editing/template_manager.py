
import random
from pathlib import Path


# ==========================================
# TEMPLATE CONFIGURATION
# ==========================================

EDIT_DURATION = 10

SONG_BPM = {
    "edit_1": 130,
    "edit_2": 134,
}


def get_templates(project_root):

    songs_dir = project_root / "assets" / "songs"

    songs = sorted(
        songs_dir.glob("*.mp3")
    )

    templates = []

    for song in songs:

        name = song.stem

        templates.append({
            "name": name,
            "song": str(song),
            "bpm": SONG_BPM.get(name, 120),
            "duration": EDIT_DURATION
        })

    return templates


def select_random_template(templates):

    if not templates:
        raise RuntimeError("No editing templates available")

    return random.choice(templates)
