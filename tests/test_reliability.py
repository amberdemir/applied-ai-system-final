"""Reliability tests for the applied system. Run with:  python -m pytest"""
import pytest

from src.applied_system import compute_confidence, run, self_critique
from src.guardrails import CatalogError, validate_catalog, validate_k, validate_prefs
from src.rag import retrieve

SONGS = [
    {"title": "Sunrise City", "artist": "Neon Echo", "genre": "pop", "mood": "happy", "energy": 0.82},
    {"title": "Midnight Coding", "artist": "LoRoom", "genre": "lofi", "mood": "chill", "energy": 0.42},
    {"title": "Storm Runner", "artist": "Voltline", "genre": "rock", "mood": "intense", "energy": 0.91},
    {"title": "Library Rain", "artist": "Paper Lanterns", "genre": "lofi", "mood": "chill", "energy": 0.35},
    {"title": "Spacewalk Thoughts", "artist": "Orbit Bloom", "genre": "ambient", "mood": "chill", "energy": 0.28},
]


# ---------- guardrails ----------
def test_energy_out_of_range_is_clamped_and_warned():
    clean, warnings = validate_prefs({"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 1.7}, SONGS)
    assert clean["target_energy"] == 1.0
    assert any("clamped" in w for w in warnings)


def test_non_numeric_energy_falls_back():
    clean, warnings = validate_prefs({"favorite_genre": "pop", "target_energy": "loud"}, SONGS)
    assert clean["target_energy"] == 0.5 and warnings


def test_unknown_genre_is_flagged_not_crashed():
    _, warnings = validate_prefs({"favorite_genre": "classical", "favorite_mood": "happy", "target_energy": 0.5}, SONGS)
    assert any("not in the catalog" in w for w in warnings)


def test_both_key_styles_are_filled():
    clean, _ = validate_prefs({"genre": "Pop", "mood": "HAPPY", "energy": 0.8}, SONGS)
    assert clean["favorite_genre"] == clean["genre"] == "pop"
    assert clean["favorite_mood"] == clean["mood"] == "happy"


def test_empty_catalog_raises():
    with pytest.raises(CatalogError):
        validate_catalog([])


def test_k_is_bounded():
    assert validate_k(0, 5)[0] == 5
    assert validate_k(99, 5)[0] == 5


# ---------- retrieval ----------
def test_retrieval_finds_relevant_genre():
    assert retrieve("lofi chill")[0]["id"] in {"genre-lofi", "mood-chill"}


def test_retrieval_returns_nothing_for_gibberish():
    assert retrieve("zzzz qqqq") == []


def test_energy_fit_uses_retrieved_range():
    from src.rag import check_energy_fit
    assert check_energy_fit("ambient", 1.0) is not None   # atypical: ambient is low energy
    assert check_energy_fit("ambient", 0.2) is None       # typical
    assert check_energy_fit("classical", 0.5) is None     # not in knowledge base: no opinion


def test_retrieval_changes_the_decision(tmp_path):
    """Same catalog, same genre: only the retrieved energy range differs between these two runs."""
    calm = run({"favorite_genre": "ambient", "favorite_mood": "chill", "target_energy": 0.2}, SONGS, k=3,
               log_path=str(tmp_path / "log.txt"))
    loud = run({"favorite_genre": "ambient", "favorite_mood": "chill", "target_energy": 1.0}, SONGS, k=3,
               log_path=str(tmp_path / "log.txt"))
    assert not calm.needs_human_review
    assert loud.needs_human_review
    assert any(f.startswith("implausible_request") for f in loud.flags)


# ---------- confidence + critique ----------
def _row(title, artist, genre, score):
    return {"title": title, "artist": artist, "genre": genre, "mood": "x", "score": score, "reasons": []}


def test_confidence_is_between_0_and_1():
    rows = [_row("a", "A", "pop", 4.0), _row("b", "B", "rock", 1.0)]
    assert 0.0 <= compute_confidence(rows, 0) <= 1.0


def test_strong_clear_match_beats_weak_tied_match():
    strong = compute_confidence([_row("a", "A", "pop", 3.9), _row("b", "B", "rock", 1.5)], 0)
    weak = compute_confidence([_row("a", "A", "pop", 1.0), _row("b", "B", "rock", 1.0)], 0)
    assert strong > weak


def test_warnings_lower_confidence():
    rows = [_row("a", "A", "pop", 3.0), _row("b", "B", "rock", 1.0)]
    assert compute_confidence(rows, 2) < compute_confidence(rows, 0)


def test_filter_bubble_detected():
    rows = [_row(str(i), f"A{i}", "lofi", 3.0 - i * 0.1) for i in range(4)]
    assert any(f.startswith("filter_bubble") for f in self_critique(rows, []))


def test_tie_and_artist_repeat_detected():
    rows = [_row("a", "Same", "pop", 2.0), _row("b", "Same", "rock", 2.0)]
    flags = self_critique(rows, [])
    assert any(f.startswith("tie") for f in flags)
    assert any(f.startswith("artist_repeat") for f in flags)


# ---------- end-to-end ----------
def test_good_profile_is_trusted(tmp_path):
    report = run({"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}, SONGS, k=3,
                 log_path=str(tmp_path / "log.txt"))
    assert report.recommendations[0]["title"] == "Sunrise City"
    assert not report.needs_human_review


def test_out_of_catalog_profile_triggers_human_review(tmp_path):
    report = run({"favorite_genre": "classical", "favorite_mood": "sad", "target_energy": 1.7}, SONGS, k=3,
                 log_path=str(tmp_path / "log.txt"))
    assert report.needs_human_review
    assert report.warnings


def test_results_are_sorted_best_first(tmp_path):
    report = run({"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.35}, SONGS, k=5,
                 log_path=str(tmp_path / "log.txt"))
    scores = [r["score"] for r in report.recommendations]
    assert scores == sorted(scores, reverse=True)
