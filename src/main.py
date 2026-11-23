"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.applied_system import format_report, run
from src.recommender import load_songs


PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.95},
    # Edge case: high energy but a sad mood, which pull in opposite directions
    "Conflicted (High Energy + Sad)": {"genre": "pop", "mood": "sad", "energy": 0.9},
    # Edge case: a genre that doesn't exist in songs.csv
    "Unknown Genre (K-Pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for profile_name, user_prefs in PROFILES.items():
        print(f"\n=== {profile_name} ===")
        print(f"Preferences: {user_prefs}\n")
        report = run(user_prefs, songs, k=5)
        print(format_report(report))

if __name__ == "__main__":
    main()
