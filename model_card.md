# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**TuneScout 1.0**: a tiny music scout that looks through a small song list and picks the five songs that best fit your vibe.

---

## 2. Intended Use  

TuneScout suggests the top 5 songs from a small catalog of songs stored in a spreadsheet-style file (a CSV). You tell it three things: your favorite genre, your favorite mood, and how energetic you want the music to be (from 0, very calm, to 1, very intense). It gives back five songs, each with the reasons it was picked.

It is a classroom project for learning how recommenders work. It assumes a listener's taste can be described with just those three preferences.

### Non-Intended Use

- **Not for real users or real music apps.** It is a learning simulation, not a finished product.
- **Not for judging anyone's taste.** A low score only means a song didn't fit three simple rules, not that the song or the listener is "wrong".
- **Not for large catalogs.** It was built and tested with 10 songs and checks every song one by one, so it was never designed for millions of songs.

---

## 3. How the Model Works  

### Algorithm Summary

TuneScout gives every song in the catalog a score by adding up points:

- **Genre match: +2.0 points** if the song's genre is your favorite genre.
- **Mood match: +1.0 point** if the song's mood is your favorite mood.
- **Energy closeness: up to +1.0 point.** The closer the song's energy is to the energy you want, the more points it gets. A perfect match earns the full point, and a song at the opposite end earns almost nothing.

The highest possible score is 4.0. Once every song has a score, TuneScout sorts them from highest to lowest and shows the top 5. Each pick lists its reasons with their points, like "genre match (+2.0)", so you can see exactly why it was chosen.

Compared with the starter code, I made it explain its reasons. I also made it warn you when your genre or mood isn't in the catalog at all, and label songs that only matched on energy as weak matches.

---

## 4. Data  

The catalog is `data/songs.csv`, which holds 10 songs. Each song has a title, an artist, a genre, a mood, and five number ratings: energy, tempo (beats per minute), valence (how cheerful it sounds), danceability, and acousticness (how acoustic rather than electronic it is). TuneScout only uses genre, mood, and energy. It reads the other numbers but doesn't use them yet.

- **Genres:** pop, lofi, rock, ambient, jazz, synthwave, and indie pop.
- **Moods:** happy, chill, intense, relaxed, moody, and focused.
- **Gaps:** there is only one rock song, there are no "sad" songs, and there is no k-pop.

I did not add or remove any songs.

Real musical taste includes much more than this data captures, for example lyrics, the language a song is sung in, favorite artists, and what someone has listened to before.

---

## 5. Strengths  

- **It gets clear-cut listeners right.** For the Chill Lofi listener, the top pick was Library Rain, a calm lofi song whose energy matches exactly, which is what I expected. For the Deep Intense Rock listener, the top pick was Storm Runner, the one intense rock song, which also matched my intuition.
- **It always shows its work.** Every recommendation lists its reasons and their points, so you never have to guess why a song was picked.
- **It is honest about weak matches.** It warns when your genre or mood isn't in the catalog, and it labels songs that only matched on energy.

---

## 6. Limitations and Bias 

The catalog has only 10 songs, and only one of them is rock, so the "Deep Intense Rock" listener gets 3 weak matches in their top 5, songs that only share an energy level with what they asked for. Genres must match exactly, so a song labeled "indie pop" never counts as "pop", even though a pop fan would probably enjoy it. Because every song earns some points just for being close in energy, the top 5 is always full, even when few songs really fit. To make this honest instead of hidden, I added a warning when a user's genre or mood doesn't exist in the catalog at all (for example, no song has the mood "sad"), and a "Weak match: only energy lined up" label on any song that matched neither the genre nor the mood.

---

## 7. Evaluation  

### Profiles I tested

I ran the recommender for five listener profiles. Each profile has a favorite genre, a favorite mood, and a target energy level from 0 (very calm) to 1 (very intense).

| Profile | Genre | Mood | Energy | Why I picked it |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.9 | A typical upbeat pop fan |
| Chill Lofi | lofi | chill | 0.35 | A calm listener, the opposite of the pop fan |
| Deep Intense Rock | rock | intense | 0.95 | A genre with only one song in the catalog |
| Conflicted (High Energy + Sad) | pop | sad | 0.9 | Tricky: wants high energy but a sad mood, and no song is "sad" |
| Unknown Genre (K-Pop) | k-pop | happy | 0.7 | Tricky: asks for a genre that isn't in the catalog |

### What surprised me

- **Four of the five profiles got the same five songs, just in a different order.** Only five songs in the catalog have high energy (Sunrise City, Gym Hero, Storm Runner, Rooftop Lights, Night Drive Loop). Any profile that wants energetic music ends up choosing from that same small group. Only Chill Lofi got a different list.
- **"Gym Hero" keeps showing up for the happy pop listener.** It ranks #2 for High-Energy Pop even though its mood is "intense", not "happy". It gets 2 points for being pop, the biggest reward in the scoring, and its energy (0.93) is almost exactly the 0.9 the user asked for. Those two things together outweigh the 1 point it misses for mood. Only Sunrise City, which is pop *and* happy, beats it. In plain terms: the recommender cares more about genre than mood, so a pop workout song beats a happy song from another genre.
- **The tricky profiles still got a full top 5 without complaint**, until I added the warnings and weak-match labels described in Limitations and Bias.

### Comparing the profiles, pair by pair

- **High-Energy Pop vs. Chill Lofi:** The two lists share no songs. High-Energy Pop moves toward fast, energetic pop songs, while Chill Lofi moves toward slow, calm lofi songs. That makes sense because they want opposite genres *and* opposite energy levels.
- **High-Energy Pop vs. Deep Intense Rock:** The same five songs, reordered. Storm Runner jumps from #4 to #1 because it is the only rock song and its mood is "intense". Both listeners want high energy, so they draw from the same small group of energetic songs.
- **High-Energy Pop vs. Conflicted:** The same five songs, but Gym Hero moves up to #1 and Sunrise City drops to #2. No song is "sad", so nobody earns mood points, and the closest energy level decides. Gym Hero (0.93) is a little closer to 0.9 than Sunrise City (0.82). This shows the "sad" request was quietly ignored.
- **High-Energy Pop vs. Unknown Genre:** The same five songs, but Rooftop Lights moves up to #1 and Gym Hero falls to #5. No song is "k-pop", so nobody gets genre points. That leaves mood and energy: Rooftop Lights is happy and its energy (0.76) is close to the requested 0.7, while Gym Hero loses the genre points that were holding it up.
- **Chill Lofi vs. Deep Intense Rock:** No shared songs. They sit at opposite ends of the catalog: quiet, gentle lofi tracks versus loud, intense ones.
- **Chill Lofi vs. Conflicted:** No shared songs. Conflicted still asks for pop at 0.9 energy, so it pulls the same energetic songs as the pop listener, far from the calm lofi tracks.
- **Chill Lofi vs. Unknown Genre:** No shared songs. Unknown Genre wants happy songs at medium-high energy (0.7). The lofi songs are calm (energy around 0.35 to 0.42) and none of them is happy, so they score low.
- **Deep Intense Rock vs. Conflicted:** The same five songs. Storm Runner is #1 for the rock fan but only #3 for Conflicted, because it is rock, not pop. Gym Hero is #2 for the rock fan only because it is "intense" (a mood match), not because it is rock.
- **Deep Intense Rock vs. Unknown Genre:** The same five songs, ordered by different moods. The rock fan's "intense" mood lifts Gym Hero to #2, while the k-pop fan's "happy" mood puts Rooftop Lights and Sunrise City at the top.
- **Conflicted vs. Unknown Genre:** The same five songs. Each profile has one preference the catalog can't satisfy, so each falls back on its other two. Conflicted ranks by "is it pop?" plus energy, so the pop songs lead. Unknown Genre ranks by "is it happy?" plus energy, so the happy songs lead.

### Terminal output for each profile

These are the results of running `python -m src.main`.

**High-Energy Pop**

```
=== High-Energy Pop ===
Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9}

Top recommendations:

1. Sunrise City
   Score: 3.92
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness (+0.92)

2. Gym Hero
   Score: 2.97
   Reasons:
     - genre match (+2.0)
     - energy closeness (+0.97)

3. Rooftop Lights
   Score: 1.86
   Reasons:
     - mood match (+1.0)
     - energy closeness (+0.86)

4. Storm Runner
   Score: 0.99
   Reasons:
     - energy closeness (+0.99)
   Weak match: only energy lined up

5. Night Drive Loop
   Score: 0.85
   Reasons:
     - energy closeness (+0.85)
   Weak match: only energy lined up
```

**Chill Lofi**

```
=== Chill Lofi ===
Preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35}

Top recommendations:

1. Library Rain
   Score: 4.00
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness (+1.00)

2. Midnight Coding
   Score: 3.93
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness (+0.93)

3. Focus Flow
   Score: 2.95
   Reasons:
     - genre match (+2.0)
     - energy closeness (+0.95)

4. Spacewalk Thoughts
   Score: 1.93
   Reasons:
     - mood match (+1.0)
     - energy closeness (+0.93)

5. Coffee Shop Stories
   Score: 0.98
   Reasons:
     - energy closeness (+0.98)
   Weak match: only energy lined up
```

**Deep Intense Rock**

```
=== Deep Intense Rock ===
Preferences: {'genre': 'rock', 'mood': 'intense', 'energy': 0.95}

Top recommendations:

1. Storm Runner
   Score: 3.96
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness (+0.96)

2. Gym Hero
   Score: 1.98
   Reasons:
     - mood match (+1.0)
     - energy closeness (+0.98)

3. Sunrise City
   Score: 0.87
   Reasons:
     - energy closeness (+0.87)
   Weak match: only energy lined up

4. Rooftop Lights
   Score: 0.81
   Reasons:
     - energy closeness (+0.81)
   Weak match: only energy lined up

5. Night Drive Loop
   Score: 0.80
   Reasons:
     - energy closeness (+0.80)
   Weak match: only energy lined up
```

**Conflicted (High Energy + Sad)**

```
=== Conflicted (High Energy + Sad) ===
Preferences: {'genre': 'pop', 'mood': 'sad', 'energy': 0.9}
Warning: no songs in the catalog have mood "sad".

Top recommendations:

1. Gym Hero
   Score: 2.97
   Reasons:
     - genre match (+2.0)
     - energy closeness (+0.97)

2. Sunrise City
   Score: 2.92
   Reasons:
     - genre match (+2.0)
     - energy closeness (+0.92)

3. Storm Runner
   Score: 0.99
   Reasons:
     - energy closeness (+0.99)
   Weak match: only energy lined up

4. Rooftop Lights
   Score: 0.86
   Reasons:
     - energy closeness (+0.86)
   Weak match: only energy lined up

5. Night Drive Loop
   Score: 0.85
   Reasons:
     - energy closeness (+0.85)
   Weak match: only energy lined up
```

**Unknown Genre (K-Pop)**

```
=== Unknown Genre (K-Pop) ===
Preferences: {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.7}
Warning: no songs in the catalog have genre "k-pop".

Top recommendations:

1. Rooftop Lights
   Score: 1.94
   Reasons:
     - mood match (+1.0)
     - energy closeness (+0.94)

2. Sunrise City
   Score: 1.88
   Reasons:
     - mood match (+1.0)
     - energy closeness (+0.88)

3. Night Drive Loop
   Score: 0.95
   Reasons:
     - energy closeness (+0.95)
   Weak match: only energy lined up

4. Storm Runner
   Score: 0.79
   Reasons:
     - energy closeness (+0.79)
   Weak match: only energy lined up

5. Gym Hero
   Score: 0.77
   Reasons:
     - energy closeness (+0.77)
   Weak match: only energy lined up
```

### Experiment: changing the weights

I tried a weight-shift experiment: I doubled the importance of energy (up to 2 points instead of 1) and halved the importance of genre (1 point instead of 2), leaving mood at 1 point. Then I ran all five profiles again.

**Result:** the top 5 stayed exactly the same, in the same order, for all five profiles. Only the scores changed, and the gaps between songs got smaller. For example, for Chill Lofi, Focus Flow had been ahead of Spacewalk Thoughts by about 1 point, and that lead shrank to just 0.04.

**Why:** in this small catalog, genre and energy line up. Pop songs here tend to be energetic and lofi songs tend to be calm, so rewarding energy more mostly rewards the same songs that genre was already favoring. With a bigger, more varied catalog, the change would likely start pushing songs from the wrong genre into the top 5.

**Decision:** I kept the original weights (genre +2.0, mood +1.0, energy up to +1.0). The experiment didn't improve any recommendation, and it made weak matches look closer to good ones.

---

## 8. Future Work  

1. **Use more of the song data.** Tempo, valence (cheerfulness), and danceability are already in the file. Using them would help tell apart songs that have the same genre and energy.
2. **Treat similar genres as close matches.** "Indie pop" should earn some points for a pop fan instead of zero, for example half the genre points.
3. **Add variety to the top 5.** Right now the five most energetic songs keep showing up for many different listeners. TuneScout could make sure the list doesn't repeat one artist or one kind of song too often.

---


## 9. Personal Reflection

My biggest learning moment was seeing that a song's score is just three simple parts added together: genre points, mood points, and how close its energy is to what the user wants. Once the reasons list showed where each point came from, I understood exactly why a song ranked where it did.

AI helped me a lot. It wrote the scoring and ranking code, fixed my crash, and ran all five test profiles. But I couldn't just trust it. When I ran the first code, I got a KeyError because the key names didn't match my files (favorite_genre instead of genre). I pasted the error back, and Claude Code read my real files and fixed it. I also read the output myself to make sure the results made sense, like Chill Lofi giving calm lofi songs.

I was surprised that just three rules (genre, mood, and energy) could produce results that really felt like recommendations. Chill Lofi gave calm lofi songs, and the pop fan got upbeat pop. I was also surprised that Gym Hero kept showing up for happy pop fans even though its mood is "intense," because the genre match and high energy outweighed the mood. And when I doubled the energy weight, nothing changed at all, because genre and energy line up in a tiny catalog.

Next, I would add more songs so the catalog isn't so small, and use features like tempo, valence, and danceability. I would also treat "indie pop" as close to "pop" instead of a totally different genre, and add variety to the top 5 so it isn't the same kind of song five times.---

# Applied AI System: Model Card Additions

## System overview

**Name:** Trustworthy Music Recommender (extension of the Module 3 Music Recommender Simulation)
**Type:** Rule-based recommender with guardrails, retrieval (RAG), confidence scoring, self-critique and a
human-review flag.
**Intended use:** Suggest songs from a small catalog and say how much the suggestion can be trusted.
**Not intended for:** Real music services, large catalogs, or any decision that affects people's livelihoods.

## Limitations and biases

- **Filter bubble.** An exact genre match is worth the most points, so songs in the requested genre crowd out
  good songs from neighboring genres. The self-critique flags this but does not change the ranking.
- **Tiny catalog.** With about ten songs, some genres have one track, so "top 5" often includes poor matches.
  Confidence drops when this happens, which is intended.
- **Narrow knowledge base.** Retrieval only covers a handful of genres and moods. For any other genre the system
  has no opinion and says nothing, so unusual or non-Western genres get weaker checks.
- **Keyword retrieval.** Matching is by word overlap, not meaning, so unusual phrasing can miss.
- **Confidence is a heuristic, not a probability.** A score of 0.72 does not mean 72% likely to be liked.
- **Cultural bias.** The genre and mood labels, energy ranges and descriptions reflect mainstream Western
  categories, and a person's taste may not fit them.

## Could the AI be misused, and how is that prevented?

- **Misuse risk:** Low stakes overall. The main risks are treating a confident-sounding score as proof of
  quality, and using a narrow catalog to push certain artists or genres to users.
- **Prevention built in:** every repair to user input is reported, never silent; low-trust answers are flagged
  for a human instead of being presented as confident; retrieved notes are shown as evidence so users can
  check them; every run is logged so a reviewer can audit what happened.
- **Prevention still needed in a real product:** diversity re-ranking so one genre or artist cannot dominate,
  and disclosure of how ranking works.

## What surprised me while testing reliability

Before retrieval drove a decision, a contradictory request (ambient music at maximum energy) scored a
confidence of 0.87 and was trusted automatically. The score formula only measured how well a song matched, not
whether the request made sense. Adding retrieved energy ranges lowered that case to 0.77 and triggered human
review.

## Testing results

18 of 18 automated tests pass; the 8-profile experiment passes 8 of 8.

| Test input | Evaluation criteria | Confidence | Result |
|---|---|---|---|
| Pop, happy, energy 0.8 | Pop song first, no review | 1.00 | Pass |
| Lofi, chill, energy 0.35 | Lofi song first, no review | 0.72 | Pass |
| Classical, happy (not in catalog) | Warn and request review | 0.22 | Pass |
| Energy 1.7 | Clamp with warning, still return results | 0.88 | Pass |
| Energy "very loud" (text) | Fall back to 0.5 with warning, no crash | 0.74 | Pass |
| Empty preferences | Three warnings, no crash | 0.00 | Pass |
| Ambient at energy 1.0 | Retrieval flags atypical energy, request review | 0.77 | Pass |
| k = 500 | Reduce to catalog size with warning | 0.90 | Pass |

Reproduce with `python -m src.evaluate` and `python -m pytest`.

## AI collaboration

**How I used AI.** I used an AI assistant to help brainstorm the pipeline design (guardrails, retrieval,
confidence, self-critique, human review), draft code and tests, and review my approach. I decided which
extension to build and checked the results by running the tests and the evaluation script myself.

**A suggestion I accepted.** The assistant suggested repairing bad input (for example clamping an energy of
1.7 to 1.0) and reporting a warning, instead of rejecting the request. I accepted it because the user still
gets an answer and every change is visible, and I confirmed it with tests that check each warning appears.

**A suggestion I changed.** The first design only printed the retrieved notes next to each recommendation.
Because the project requires the AI feature to change how the system behaves, I changed it so the retrieved
energy range for the requested genre drives a decision: a mismatch lowers confidence and triggers human review.
I verified the change with a before/after test (same genre, calm versus loud energy, different review result).

**What I checked myself.** I ran the full test suite, read the outputs for each demo profile, and confirmed
that confidence ordering made sense (bad input scored lower than good input).
