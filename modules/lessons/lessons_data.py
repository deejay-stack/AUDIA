"""Beginner shapes ordered from string 6 (low E) to string 1 (high E).

A fret of None means mute; zero means open. Finger numbers: 1 index,
2 middle, 3 ring, 4 little. Add another entry to extend the chord library.
"""
CHORDS = {
    "c-major": {
        "name": "C Major", "symbol": "C",
        "frets": [None, 3, 2, 0, 1, 0], "fingers": [None, 3, 2, None, 1, None],
        "placement": ["Index: 1st fret, B string (2nd).", "Middle: 2nd fret, D string (4th).", "Ring: 3rd fret, A string (5th)."],
        "played": "Strum strings 5 to 1, starting on A. Leave G and high E open.",
        "muted": "Do not play the low E string (6th).",
        "tip": "Curve your fingers so the open G and high E strings can ring. Keep your thumb behind the neck.",
    },
    "g-major": {
        "name": "G Major", "symbol": "G",
        "frets": [3, 2, 0, 0, 0, 3], "fingers": [2, 1, None, None, None, 3],
        "placement": ["Index: 2nd fret, A string (5th).", "Middle: 3rd fret, low E string (6th).", "Ring: 3rd fret, high E string (1st)."],
        "played": "Strum all six strings. Leave D, G and B open.",
        "muted": "No strings are muted in this shape.",
        "tip": "Keep your middle finger from touching the A string and let the open middle strings ring.",
    },
    "d-major": {
        "name": "D Major", "symbol": "D",
        "frets": [None, None, 0, 2, 3, 2], "fingers": [None, None, None, 1, 3, 2],
        "placement": ["Index: 2nd fret, G string (3rd).", "Middle: 2nd fret, high E string (1st).", "Ring: 3rd fret, B string (2nd)."],
        "played": "Strum strings 4 to 1, starting on the open D string.",
        "muted": "Do not play low E (6th) or A (5th).",
        "tip": "Make a small triangle with your fingertips. Keep the ring finger clear of high E.",
    },
    "a-major": {
        "name": "A Major", "symbol": "A",
        "frets": [None, 0, 2, 2, 2, 0], "fingers": [None, None, 1, 2, 3, None],
        "placement": ["Index: 2nd fret, D string (4th).", "Middle: 2nd fret, G string (3rd).", "Ring: 2nd fret, B string (2nd)."],
        "played": "Strum strings 5 to 1. Leave A and high E open.",
        "muted": "Do not play low E (6th).",
        "tip": "Fit your fingertips into the second fret without resting the ring finger on high E.",
    },
    "e-major": {
        "name": "E Major", "symbol": "E",
        "frets": [0, 2, 2, 1, 0, 0], "fingers": [None, 2, 3, 1, None, None],
        "placement": ["Index: 1st fret, G string (3rd).", "Middle: 2nd fret, A string (5th).", "Ring: 2nd fret, D string (4th)."],
        "played": "Strum all six strings. Leave low E, B and high E open.",
        "muted": "No strings are muted in this shape.",
        "tip": "Use the tips of your fingers so your index does not mute the open B string.",
    },
    "a-minor": {
        "name": "A Minor", "symbol": "Am",
        "frets": [None, 0, 2, 2, 1, 0], "fingers": [None, None, 2, 3, 1, None],
        "placement": ["Index: 1st fret, B string (2nd).", "Middle: 2nd fret, D string (4th).", "Ring: 2nd fret, G string (3rd)."],
        "played": "Strum strings 5 to 1. Leave A and high E open.",
        "muted": "Do not play low E (6th).",
        "tip": "Keep the index finger curved to let high E ring. This shape has a darker sound than A major.",
    },
    "e-minor": {
        "name": "E Minor", "symbol": "Em",
        "frets": [0, 2, 2, 0, 0, 0], "fingers": [None, 2, 3, None, None, None],
        "placement": ["Middle: 2nd fret, A string (5th).", "Ring: 2nd fret, D string (4th)."],
        "played": "Strum all six strings. Leave low E, G, B and high E open.",
        "muted": "No strings are muted in this shape.",
        "tip": "A useful first chord: play each string separately and check that all six ring clearly.",
    },
    "d-minor": {
        "name": "D Minor", "symbol": "Dm",
        "frets": [None, None, 0, 2, 3, 1], "fingers": [None, None, None, 2, 3, 1],
        "placement": ["Index: 1st fret, high E string (1st).", "Middle: 2nd fret, G string (3rd).", "Ring: 3rd fret, B string (2nd)."],
        "played": "Strum strings 4 to 1, starting on the open D string.",
        "muted": "Do not play low E (6th) or A (5th).",
        "tip": "Reach with your ring finger gently. Press just behind each fret, rather than on the metal.",
    },
}

STRUMMING_PATTERNS = [
    {"name": "Quarter-note downstrokes", "strokes": ["D", "–", "D", "–", "D", "–", "D", "–"],
     "description": "Play D D D D: one downstroke on each numbered beat. On each &, keep moving your hand upward without touching the strings."},
    {"name": "Eighth-note alternating", "strokes": ["D", "U", "D", "U", "D", "U", "D", "U"],
     "description": "Play D U D U D U D U. Downstrokes land on numbers; upstrokes land on &. Keep both strokes even and light."},
    {"name": "Common beginner pattern", "strokes": ["D", "–", "D", "U", "–", "U", "D", "U"],
     "description": "Play D D U U D U. Skip the upstroke after 1 and the downstroke on 3, but keep your hand moving through those gaps."},
]
