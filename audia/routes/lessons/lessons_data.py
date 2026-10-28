"""Module: audia.routes.lessons.lessons_data.

Purpose: Store existing chord shapes, finger instructions, and strumming content.
Main components: CHORDS, STRUMMING_PATTERNS.
Related: routes.lessons.lessons and templates/lessons chord/strumming views.
Debugging: Match chord slugs and diagram data to templates; this module performs no I/O.
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


def _chord(name, symbol, frets, fingers, family, difficulty='Beginner', barre=None):
    """Build consistent descriptions from low-E-to-high-E fret/finger arrays."""
    strings = ['low E (6th)', 'A (5th)', 'D (4th)', 'G (3rd)', 'B (2nd)', 'high E (1st)']
    names = {1: 'Index', 2: 'Middle', 3: 'Ring', 4: 'Little'}
    placements = [f'{names[finger]}: fret {fret}, {strings[index]} string.'
                  for index, (fret, finger) in enumerate(zip(frets, fingers)) if finger]
    if barre:
        placements.insert(0, f'Barre fret {barre[0]} with your index from string {6-barre[1]} to string {6-barre[2]}.')
    muted = ', '.join(strings[index] for index, fret in enumerate(frets) if fret is None)
    return dict(name=name, symbol=symbol, frets=frets, fingers=fingers, family=family,
                difficulty=difficulty, barre=barre, placement=placements,
                played='Play the fretted strings and all strings marked O. Read from low E to high E.',
                muted=f'Do not play: {muted}.' if muted else 'No strings are muted in this shape.',
                tip='Pick one string at a time, keep your wrist relaxed, and use only enough pressure for a clear note.')


# Existing chord shapes and URLs remain intact; these are additional first-position shapes.
CHORDS.update({
    'f-major': _chord('F Major', 'F', [1,3,3,2,1,1], [1,3,4,2,1,1], 'Major', 'Intermediate', [1,0,5]),
    'b-minor': _chord('B Minor', 'Bm', [None,2,4,4,3,2], [None,1,3,4,2,1], 'Minor', 'Intermediate', [2,1,5]),
    'a-seventh': _chord('A Seventh', 'A7', [None,0,2,0,2,0], [None,None,2,None,3,None], 'Seventh'),
    'b-seventh': _chord('B Seventh', 'B7', [None,2,1,2,0,2], [None,2,1,3,None,4], 'Seventh'),
    'd-seventh': _chord('D Seventh', 'D7', [None,None,0,2,1,2], [None,None,None,2,1,3], 'Seventh'),
    'e-seventh': _chord('E Seventh', 'E7', [0,2,0,1,0,0], [None,2,None,1,None,None], 'Seventh'),
    'g-seventh': _chord('G Seventh', 'G7', [3,2,0,0,0,1], [3,2,None,None,None,1], 'Seventh'),
    'c-major-seventh': _chord('C Major Seventh', 'Cmaj7', [None,3,2,0,0,0], [None,3,2,None,None,None], 'Seventh'),
    'a-minor-seventh': _chord('A Minor Seventh', 'Am7', [None,0,2,0,1,0], [None,None,2,None,1,None], 'Seventh'),
    'a-suspended-second': _chord('A Suspended Second', 'Asus2', [None,0,2,2,0,0], [None,None,1,2,None,None], 'Suspended'),
    'd-suspended-second': _chord('D Suspended Second', 'Dsus2', [None,None,0,2,3,0], [None,None,None,1,3,None], 'Suspended'),
    'd-suspended-fourth': _chord('D Suspended Fourth', 'Dsus4', [None,None,0,2,3,3], [None,None,None,1,3,4], 'Suspended'),
})
for chord in CHORDS.values():
    chord.setdefault('difficulty', 'Beginner')
    chord.setdefault('family', 'Minor' if chord['symbol'].endswith('m') else 'Major')

STRUMMING_PATTERNS.extend([
    {'name': 'Offbeat accents', 'strokes': ['D','U','D','U','D','U','D','U'],
     'description': 'Intermediate: play lightly on the numbers and accent each upstroke on &. Start at 60 BPM.'},
    {'name': 'Muted backbeat', 'strokes': ['D','–','X','U','D','–','X','U'],
     'description': 'Intermediate: X is a gentle muted downstroke on beats 2 and 4. Keep an even eighth-note motion.'},
    {'name': 'Syncopated control', 'strokes': ['D','–','–','U','–','U','D','–'],
     'description': 'Advanced: count every subdivision aloud. Sustain through the skipped strokes without speeding up.'},
])

# Original curriculum and song exercises, written for AUDIA; no copied arrangements.
COURSES = {
    'clean-first-chords': dict(title='Clean first chords', difficulty='Beginner', category='Chords', minutes=10,
        chords=['e-minor','a-minor','c-major'],
        steps=['Tune to E–A–D–G–B–E, then form Em with a relaxed wrist.', 'Pick each string separately; move a fingertip just behind its fret if it buzzes.', 'Repeat with Am and C. Leave muted strings out of your strum.'],
        exercise='Play each chord for four slow downstrokes at 50 BPM. Repeat the sequence four times.'),
    'first-chord-switches': dict(title='Your first chord changes', difficulty='Beginner', category='Technique', minutes=8,
        chords=['e-minor','a-minor','g-major','d-major'],
        steps=['Alternate Em and Am, moving the fingers together rather than one at a time.', 'Try G to D. Look for the destination before lifting your hand.', 'Count clean changes for one minute. Keep a personal record without sacrificing clarity.'],
        exercise='Two minutes each: Em–Am, G–D, then Em–G. Rest between rounds; stop if your hand hurts.'),
    'steady-eighth-notes': dict(title='Steady eighth-note rhythm', difficulty='Beginner', category='Rhythm', minutes=10,
        chords=['e-minor','g-major'],
        steps=['Count 1 & 2 & 3 & 4 & with your foot tapping on the numbers.', 'Use downstrokes on numbers and upstrokes on & with a small wrist motion.', 'Change Em to G after each full bar without pausing your strumming hand.'],
        exercise='At 55 BPM, play eight bars of alternating down/up strokes. Repeat with the common beginner pattern.'),
    'barre-foundations': dict(title='A comfortable barre foundation', difficulty='Intermediate', category='Chords', minutes=12,
        chords=['f-major','b-minor','c-major'],
        steps=['Use the side of your index close to the fret for the F barre.', 'Add middle, ring and little fingers. Pick each note and adjust the index angle gently.', 'Practice the Bm shape at fret 2, muting low E. Relax your grip between attempts.'],
        exercise='Hold F for two beats, release for two, then switch C–F slowly. Use short rounds rather than squeezing harder.'),
    'seventh-colors': dict(title='Seventh-chord colors', difficulty='Intermediate', category='Chords', minutes=12,
        chords=['a-seventh','d-seventh','e-seventh','g-seventh'],
        steps=['Compare A to A7 and listen for the added seventh.', 'Pick D7 carefully from the D string, leaving low E and A muted.', 'Alternate A7, D7 and E7 using four beats per chord.'],
        exercise='Play a 12-bar study: A7 A7 A7 A7 / D7 D7 A7 A7 / E7 D7 A7 E7. Start at 60 BPM.'),
    'muted-groove': dict(title='Muted groove and accents', difficulty='Intermediate', category='Rhythm', minutes=10,
        chords=['a-minor','e-minor'],
        steps=['Rest your fretting fingers lightly on the strings for a muted X stroke.', 'Place the muted stroke on beats 2 and 4 without a hard strike.', 'Alternate one bar of Am with one bar of Em. Keep your motion small and even.'],
        exercise='Use D – X U D – X U for eight bars at 65 BPM. Record a short practice clip yourself if helpful.'),
    'voice-leading': dict(title='Voice leading with color chords', difficulty='Advanced', category='Harmony', minutes=15,
        chords=['c-major-seventh','a-minor-seventh','d-suspended-second','d-suspended-fourth','d-major'],
        steps=['Compare Cmaj7 and Am7 and identify which fingers can stay close to the strings.', 'Alternate Dsus2, D and Dsus4 while holding common notes.', 'Pick strings separately to hear how one moving voice changes the harmony.'],
        exercise='Play Cmaj7–Am7–Dsus2–D–Dsus4–D at 60 BPM. Aim for connected notes and minimal finger travel.'),
    'fingerstyle-independence': dict(title='Fingerstyle independence', difficulty='Advanced', category='Technique', minutes=15,
        chords=['c-major','a-minor','e-minor','g-major'],
        steps=['Use the thumb on an appropriate bass note: A for C/Am, low E for Em/G.', 'Use index on G, middle on B and ring on high E.', 'Keep the thumb steady while the upper fingers play lightly. Avoid pulling the strings outward.'],
        exercise='Count 1 & 2 & 3 & 4 &: bass–G–B–e–bass–G–B–e. Play two bars per chord at 50 BPM.'),
    'syncopation-study': dict(title='Syncopation without losing the beat', difficulty='Advanced', category='Rhythm', minutes=12,
        chords=['a-minor-seventh','c-major-seventh'],
        steps=['Count eighth notes aloud and keep the strumming hand moving through rests.', 'Play D – – U – U D – with a gentle accent on the upstroke after beat 2.', 'Alternate Am7 and Cmaj7 only after the rhythm stays steady on one chord.'],
        exercise='Play four bars, rest one bar while counting, then re-enter on beat 1. Repeat four rounds at 65 BPM.'),
}

SONGS = [
    dict(title='First Light', difficulty='Beginner', meter='4/4', bpm=55,
         progression=['Em','Em','C','C','G','G','D','D'],
         lyrics=['Morning opens, strings awake; one small sound is mine to make.', 'Step by step, I find my way; let this chord begin the day.'],
         practice='Original eight-bar song study. Four downstrokes per bar; sing each lyric line across four bars.'),
    dict(title='Small Steps Home', difficulty='Beginner', meter='4/4', bpm=60,
         progression=['Am','C','G','G','Am','C','Em','Em'],
         lyrics=['Little steps along the street, steady hands and steady feet.', 'Every note can lead me home; I can play and make it my own.'],
         practice='Original eight-bar song study. One chord per bar. Start with quarter notes, then try D D U U D U.'),
    dict(title='Evening Colors', difficulty='Intermediate', meter='4/4', bpm=65,
         progression=['Cmaj7','Am7','Dsus2','D','Cmaj7','Am7','G','G'],
         lyrics=['Evening colors fill the air; quiet chords are waiting there.', 'Hold the rhythm, let it flow; hear the places we can go.'],
         practice='Original eight-bar song study. Keep common fingers near their strings; try the fingerstyle pattern from the course.'),
]
