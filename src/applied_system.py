"""Applied AI system: orchestrates guardrails -> recommender -> retrieval -> confidence -> self-critique.

Pipeline (orchestration):
    1. GUARDRAILS   validate/repair the user's preferences (src/guardrails.py)
    2. RECOMMENDER  the original rule-based ranker from the earlier project
    3. RAG          retrieve trusted notes explaining why each genre/mood fits (src/rag.py)
    4. CONFIDENCE   score how much to trust this answer (0-1)
    5. SELF-CRITIQUE look for filter bubbles, weak matches, ties, repeated artists
    6. HUMAN-IN-THE-LOOP  flag the answer for review when confidence is low
    7. LOGGING      append every run to logs/system.log

Run:  python -m src.applied_system
"""
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List

from src.guardrails import CatalogError, validate_catalog, validate_k, validate_prefs
from src.rag import check_energy_fit, retrieve
from src.recommender import load_songs, recommend_songs

# Highest score score_song can award (genre + mood + perfect energy). Adjust to your weights.
MAX_SCORE = 4.0
REVIEW_THRESHOLD = 0.5

logger = logging.getLogger("applied_system")


def _setup_logging(log_path: str = "logs/system.log") -> None:
    if logger.handlers:
        return
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass
class Report:
    recommendations: List[Dict] = field(default_factory=list)
    confidence: float = 0.0
    flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    needs_human_review: bool = False


def _normalize(results) -> List[Dict]:
    """Accept the starter's (song, score, explanation) tuples and turn them into dicts."""
    rows = []
    for item in results:
        song, score, why = item[0], float(item[1]), (item[2] if len(item) > 2 else "")
        reasons = why if isinstance(why, list) else [r.strip() for r in str(why).split(";") if r.strip()]
        rows.append({
            "title": song.get("title", "?"),
            "artist": song.get("artist", "?"),
            "genre": str(song.get("genre", "")).lower(),
            "mood": str(song.get("mood", "")).lower(),
            "score": score,
            "reasons": reasons,
        })
    return rows


def compute_confidence(rows: List[Dict], n_warnings: int, max_score: float = MAX_SCORE) -> float:
    """0-1 trust score: how strong the top match is, how clearly it beats #2, minus input problems."""
    if not rows:
        return 0.0
    top = rows[0]["score"]
    strength = min(1.0, top / max_score)
    if len(rows) > 1:
        separation = min(1.0, (top - rows[1]["score"]) / (0.25 * max_score))
    else:
        separation = 1.0
    penalty = min(0.3, 0.1 * n_warnings)
    return round(max(0.0, min(1.0, 0.7 * strength + 0.3 * separation - penalty)), 2)


def self_critique(rows: List[Dict], warnings: List[str], max_score: float = MAX_SCORE) -> List[str]:
    """Look at our own answer and name its weaknesses."""
    flags = []
    if not rows:
        return ["no_results"]
    if len(rows) >= 3:
        genres = [r["genre"] for r in rows]
        if max(genres.count(g) for g in set(genres)) / len(genres) >= 0.8:
            flags.append("filter_bubble: nearly all results share one genre")
    if rows[0]["score"] < 0.5 * max_score:
        flags.append("weak_match: best score is under half of the maximum")
    if len(rows) > 1 and rows[0]["score"] == rows[1]["score"]:
        flags.append("tie: top two songs have identical scores")
    artists = [r["artist"] for r in rows]
    if len(set(artists)) < len(artists):
        flags.append("artist_repeat: the same artist appears more than once")
    if any("not in the catalog" in w for w in warnings):
        flags.append("input_outside_catalog: requested genre/mood does not exist in the data")
    if any("is unusual for" in w for w in warnings):
        flags.append("implausible_request: retrieved knowledge says this energy is atypical for the genre")
    return flags


def run(user_prefs: Dict, songs: List[Dict], k: int = 5, log_path: str = "logs/system.log") -> Report:
    _setup_logging(log_path)
    validate_catalog(songs)
    clean, warnings = validate_prefs(user_prefs, songs)
    k, k_warnings = validate_k(k, len(songs))
    warnings += k_warnings

    # RAG decision step: retrieved knowledge about the requested genre checks the requested energy.
    implausible = check_energy_fit(clean["favorite_genre"], clean["target_energy"])
    if implausible:
        warnings.append(implausible)

    rows = _normalize(recommend_songs(clean, songs, k))
    for row in rows:
        row["evidence"] = [d["text"] for d in retrieve(f"{row['genre']} {row['mood']}", k=2)]

    confidence = compute_confidence(rows, len(warnings))
    flags = self_critique(rows, warnings)
    needs_review = confidence < REVIEW_THRESHOLD or any(
        f.startswith(("weak_match", "input_outside_catalog", "implausible_request", "no_results")) for f in flags
    )

    level = logging.WARNING if needs_review else logging.INFO
    logger.log(level, "prefs=%s top=%s confidence=%.2f flags=%s warnings=%s review=%s",
               user_prefs, rows[0]["title"] if rows else None, confidence, flags, warnings, needs_review)
    return Report(rows, confidence, flags, warnings, needs_review)


def format_report(report: Report) -> str:
    lines = []
    for i, r in enumerate(report.recommendations, 1):
        lines.append(f"{i}. {r['title']} by {r['artist']}  [{r['genre']}/{r['mood']}]  score {r['score']:.2f}")
        for reason in r["reasons"]:
            lines.append(f"     - {reason}")
        if r["evidence"]:
            lines.append(f"     > {r['evidence'][0]}")
    lines.append(f"\nConfidence: {report.confidence:.2f}")
    if report.warnings:
        lines.append("Input warnings: " + " | ".join(report.warnings))
    if report.flags:
        lines.append("Self-critique flags: " + " | ".join(report.flags))
    if report.needs_human_review:
        lines.append("HUMAN REVIEW REQUESTED: confidence or input quality is too low to trust automatically.")
    return "\n".join(lines)


DEMO_PROFILES = {
    "Pop fan": {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8},
    "Lofi studier": {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.35},
    "Genre not in catalog": {"favorite_genre": "classical", "favorite_mood": "sad", "target_energy": 1.7},
    "Conflicting taste": {"favorite_genre": "ambient", "favorite_mood": "chill", "target_energy": 1.0},
}


def main() -> None:
    try:
        songs = load_songs("data/songs.csv")
    except (FileNotFoundError, CatalogError) as err:
        print(f"Cannot start: {err}")
        return
    for name, prefs in DEMO_PROFILES.items():
        print(f"\n=== {name} ===")
        print(format_report(run(prefs, songs, k=5)))


if __name__ == "__main__":
    main()
