"""Input guardrails: check and repair user preferences BEFORE they reach the recommender.

Rules:
  1. Never crash on bad input. Repair it and record a warning instead.
  2. Never silently change what the user meant. Every repair is reported.
  3. Fail loudly (raise) only when the catalog itself is unusable.
"""
from typing import Dict, List, Tuple

# The recommender code in different versions of the starter uses different key names.
# We accept all of them and fill in all of them so score_song works either way.
GENRE_KEYS = ("favorite_genre", "genre")
MOOD_KEYS = ("favorite_mood", "mood")
ENERGY_KEYS = ("target_energy", "energy")


class CatalogError(ValueError):
    """Raised when the song catalog is empty or malformed."""


def _first(prefs: Dict, keys) -> object:
    for key in keys:
        if prefs.get(key) not in (None, ""):
            return prefs[key]
    return None


def validate_catalog(songs: List[Dict]) -> None:
    if not songs:
        raise CatalogError("Song catalog is empty; nothing to recommend.")
    if not all(isinstance(s, dict) for s in songs):
        raise CatalogError("Every song must be a dict.")


def validate_k(k: int, catalog_size: int) -> Tuple[int, List[str]]:
    warnings = []
    if not isinstance(k, int) or k < 1:
        warnings.append(f"k={k!r} is invalid; using k=5.")
        k = 5
    if k > catalog_size:
        warnings.append(f"k={k} is larger than the catalog ({catalog_size}); using k={catalog_size}.")
        k = catalog_size
    return k, warnings


def validate_prefs(prefs: Dict, songs: List[Dict]) -> Tuple[Dict, List[str]]:
    """Return (clean_prefs, warnings). Unknown genres/moods are kept but flagged."""
    warnings: List[str] = []
    prefs = dict(prefs or {})

    genre = _first(prefs, GENRE_KEYS)
    mood = _first(prefs, MOOD_KEYS)
    energy = _first(prefs, ENERGY_KEYS)

    known_genres = {str(s.get("genre", "")).lower() for s in songs}
    known_moods = {str(s.get("mood", "")).lower() for s in songs}

    if genre is None:
        warnings.append("No genre given; genre will not influence results.")
        genre = ""
    else:
        genre = str(genre).strip().lower()
        if genre not in known_genres:
            warnings.append(f"Genre '{genre}' is not in the catalog (known: {sorted(g for g in known_genres if g)}).")

    if mood is None:
        warnings.append("No mood given; mood will not influence results.")
        mood = ""
    else:
        mood = str(mood).strip().lower()
        if mood not in known_moods:
            warnings.append(f"Mood '{mood}' is not in the catalog (known: {sorted(m for m in known_moods if m)}).")

    if energy is None:
        warnings.append("No target energy given; using neutral 0.5.")
        energy = 0.5
    else:
        try:
            energy = float(energy)
        except (TypeError, ValueError):
            warnings.append(f"Energy {energy!r} is not a number; using 0.5.")
            energy = 0.5
    if not 0.0 <= energy <= 1.0:
        clamped = min(1.0, max(0.0, energy))
        warnings.append(f"Energy {energy} is outside 0-1; clamped to {clamped}.")
        energy = clamped

    clean = dict(prefs)
    for key in GENRE_KEYS:
        clean[key] = genre
    for key in MOOD_KEYS:
        clean[key] = mood
    for key in ENERGY_KEYS:
        clean[key] = energy
    return clean, warnings
