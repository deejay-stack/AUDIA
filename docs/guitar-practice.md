# Guitar tuner and lessons

The existing signed-in tuner and learning module are extended in place. Use the
shared navigation to move between Shop, My Orders, Tuner, Lessons and Account.

## Live tuner

`audia/routes/tuner/tuner.py` renders `templates/tuner/tuner.html`.
`assets/js/tuner/tuner.js` requests real microphone input only after Start,
creates a local Web Audio filter/analyser chain and repeatedly passes samples to
`detectPitch()` in `tuner_pitch.js`. No application code generates fake pitches,
records audio or uploads recordings. YIN and median/smoothed pitch handling remain.

Both acoustic and electric use A4=440 standard targets: E2 82.41 Hz, A2 110 Hz,
D3 146.83 Hz, G3 196 Hz, B3 246.94 Hz and E4 329.63 Hz. Electric mode lowers the
signal gate and changes filtering, rather than changing tuning. Select Automatic
or choose the intended string; the meter measures cents against that target.
Within ?5 cents is in tune. Use a clean amplifier near the microphone for a quiet
electric guitar. Pluck one open string and mute the others.

HTTPS or localhost and a browser with Web Audio/getUserMedia are required.
Permission denial, missing devices and interruptions have explicit feedback.
Stop, hidden pages and navigation release tracks, nodes and the AudioContext.
Physical microphone/room/instrument performance needs a real hardware check.

## Lessons and saved progress

`audia/routes/lessons/lessons_data.py` holds the original eight chord shapes and
additional shapes, curriculum, strumming and original song exercises. The chord
library has 20 shapes with family/difficulty filters. First-position barre
indicators and finger labels are drawn by the existing SVG macro.

Nine courses are grouped into beginner, intermediate and advanced levels, with
chord, rhythm, technique and harmony categories. Course pages have clear steps,
a practice exercise, chord links, previous/next navigation and saved completion.
Six strumming patterns include the original three. Three original eight-bar song
studies provide chord progressions and original lyrics; no copyrighted arrangement
was reproduced.

`assets/js/lessons/lessons.js` reads and updates only the signed-in user's progress
through `/api/lessons/progress` and `/api/lessons/progress/<slug>`. Mutations use
existing session authentication and CSRF protection. Content stays server-rendered;
progress failures do not remove the lesson material.

## Editing and checks

- Content/routes: `audia/routes/lessons/lessons_data.py` and `lessons.py`.
- Markup: `templates/lessons/`; appearance: `assets/css/lessons/lessons.css` and its existing component sheets.
- Tuner UI/audio lifecycle: `tuner.js`; pure frequency/note/target math: `tuner_pitch.js`; presentation: `assets/css/tuner/`.
- New progress storage: `LessonProgress` in `audia/database/models.py`; existing databases use `flask --app app upgrade-db`.

[UPGRADE_NOTES.md](UPGRADE_NOTES.md) records the passing API, chord pitch-class and
synthetic pitch checks and the limits of verification. Browser UI inspection was
stopped by the computer-use URL check; desktop/mobile behavior and physical audio
remain unverified. Temporary tests and generated reports were removed after
verification as requested.
