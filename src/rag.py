"""Retrieval step (RAG): look up short, trusted notes about a genre or mood.

Retrieval is used in two ways, and BOTH change what the system does:
  1. Evidence: each recommendation carries the retrieved note explaining why that genre/mood fits.
  2. Decision: the retrieved note for the user's requested genre carries a typical energy range.
     `check_energy_fit` compares the user's target energy to that range. A mismatch (for example a
     user who asks for ambient music at maximum energy) lowers confidence and triggers human review.

The knowledge base is small and human-written so every claim can be audited. The system never
invents facts: if nothing relevant is retrieved, it says nothing rather than guessing.
"""
import re
from typing import Dict, List, Optional

# "energy" is the typical (low, high) energy range on the same 0-1 scale as songs.csv.
KNOWLEDGE_BASE: List[Dict] = [
    {"id": "genre-pop", "genre": "pop", "energy": (0.55, 1.0),
     "text": "Pop music favors catchy hooks, polished production and upbeat, danceable energy. Suits listeners who want familiar, high-energy, feel-good tracks."},
    {"id": "genre-lofi", "genre": "lofi", "energy": (0.15, 0.6),
     "text": "Lofi uses mellow beats, warm textures and low tempo. Popular for studying, focus and relaxing because it is calm and unobtrusive with low energy."},
    {"id": "genre-rock", "genre": "rock", "energy": (0.6, 1.0),
     "text": "Rock centers on guitars, drums and driving rhythm. Typically high energy and intense, suited to workouts and loud, energetic moods."},
    {"id": "genre-ambient", "genre": "ambient", "energy": (0.0, 0.4),
     "text": "Ambient music is slow, atmospheric and mostly beatless. Very low energy, used for relaxing, sleep and deep calm."},
    {"id": "genre-jazz", "genre": "jazz", "energy": (0.2, 0.65),
     "text": "Jazz features improvisation, swing and rich harmony. Usually relaxed to moderate energy, suited to chill evenings and a sophisticated, relaxed mood."},
    {"id": "genre-synthwave", "genre": "synthwave", "energy": (0.45, 0.9),
     "text": "Synthwave blends retro synthesizers with steady driving beats. Moderate to high energy with a nostalgic, moody or focused feel, good for night drives."},
    {"id": "genre-indie", "genre": "indie pop", "energy": (0.4, 0.85),
     "text": "Indie pop mixes melodic pop writing with a softer, more personal sound. Moderate energy, often happy or reflective."},
    {"id": "mood-happy", "text": "A happy mood pairs with upbeat tempo, major-key melodies and higher energy."},
    {"id": "mood-chill", "text": "A chill mood pairs with low energy, slow tempo and soft, relaxed instrumentation."},
    {"id": "mood-relaxed", "text": "A relaxed mood pairs with low to moderate energy and smooth, unhurried sound."},
    {"id": "mood-intense", "text": "An intense mood pairs with high energy, fast tempo and heavy, driving sound."},
    {"id": "mood-moody", "text": "A moody mood pairs with atmospheric, darker or nostalgic tones at moderate energy."},
    {"id": "mood-focused", "text": "A focused mood pairs with steady, low-distraction music at low to moderate energy."},
    {"id": "limits-bias", "text": "Rule-based recommenders over-reward exact genre matches, which can create a filter bubble that hides good songs from other genres. Small catalogs also under-represent many genres."},
]


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z]+", text.lower()))


def retrieve(query: str, k: int = 2, min_overlap: int = 1) -> List[Dict]:
    """Return up to k knowledge-base entries ranked by word overlap with query.

    Entries whose id words (e.g. 'genre', 'pop') appear in the query count double,
    so a query of "pop happy" finds genre-pop and mood-happy first.
    """
    q = _tokens(query)
    scored = []
    for doc in KNOWLEDGE_BASE:
        id_words = _tokens(doc["id"])
        overlap = len(q & _tokens(doc["text"])) + 2 * len(q & id_words - {"genre", "mood"})
        if overlap >= min_overlap:
            scored.append((overlap, doc))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:k]]


def check_energy_fit(genre: str, energy: float) -> Optional[str]:
    """Use retrieved knowledge to test whether a requested energy is typical for the requested genre.

    Returns a human-readable explanation when the request looks implausible, otherwise None.
    Returns None (no opinion) when the genre is not in the knowledge base.
    """
    if not genre:
        return None
    for doc in retrieve(genre, k=3):
        if doc.get("genre") == genre and "energy" in doc:
            low, high = doc["energy"]
            if not low <= energy <= high:
                return (f"Target energy {energy:.2f} is unusual for {genre} "
                        f"(typical range {low:.2f}-{high:.2f}). Source: {doc['id']}")
            return None
    return None
