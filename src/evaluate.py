"""Reliability evaluation: run the system on a fixed set of test profiles and print a pass/fail table.

Run:  python -m src.evaluate
Each case states what a RELIABLE system should do. The table (and the summary line)
go straight into the README / model card as evidence.
"""
from src.applied_system import run
from src.recommender import load_songs

# (name, prefs, expectation, check(report) -> bool)
CASES = [
    ("Typical pop fan",
     {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8},
     "pop/happy song ranked first, no human review",
     lambda r: r.recommendations[0]["genre"] == "pop" and not r.needs_human_review),
    ("Typical lofi studier",
     {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.35},
     "lofi song ranked first, no human review",
     lambda r: r.recommendations[0]["genre"] == "lofi" and not r.needs_human_review),
    ("Genre missing from catalog",
     {"favorite_genre": "classical", "favorite_mood": "happy", "target_energy": 0.5},
     "warning raised and human review requested",
     lambda r: bool(r.warnings) and r.needs_human_review),
    ("Energy out of range (1.7)",
     {"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 1.7},
     "energy clamped with a warning, system still returns results",
     lambda r: any("clamped" in w for w in r.warnings) and len(r.recommendations) > 0),
    ("Energy is text",
     {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": "very loud"},
     "falls back to 0.5 with a warning, no crash",
     lambda r: any("not a number" in w for w in r.warnings) and len(r.recommendations) > 0),
    ("Empty preferences",
     {},
     "three warnings, lower confidence, no crash",
     lambda r: len(r.warnings) >= 3 and len(r.recommendations) > 0),
    ("Conflicting taste (calm genre, max energy)",
     {"favorite_genre": "ambient", "favorite_mood": "chill", "target_energy": 1.0},
     "retrieval flags the energy as atypical for ambient and requests human review",
     lambda r: any("is unusual for ambient" in w for w in r.warnings) and r.needs_human_review
     and [x["score"] for x in r.recommendations] == sorted((x["score"] for x in r.recommendations), reverse=True)),
    ("Oversized k (500)",
     {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8},
     "k reduced to catalog size with a warning",
     lambda r: any("larger than the catalog" in w for w in r.warnings)),
]


def main() -> None:
    songs = load_songs("data/songs.csv")
    passed = 0
    print(f"{'Case':44} {'Result':6} {'Conf':>5}  Expectation")
    print("-" * 110)
    for name, prefs, expectation, check in CASES:
        k = 500 if "k (500)" in name else 5
        report = run(prefs, songs, k=k, log_path="logs/eval.log")
        ok = bool(check(report))
        passed += ok
        print(f"{name:44} {'PASS' if ok else 'FAIL':6} {report.confidence:5.2f}  {expectation}")
    print("-" * 110)
    print(f"{passed}/{len(CASES)} reliability checks passed.")


if __name__ == "__main__":
    main()
