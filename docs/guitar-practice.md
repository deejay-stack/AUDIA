# AUDIA guitar tuner and lessons

The feature behavior described here is unchanged. Paths below reflect the
feature-based architecture; see [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)
for the migration map and current architecture.

The two features are integrated into the existing Flask application. Sign in and
open **Guitar Tuner** or **Guitar Lessons** from the landing, store, or account
page. The new pages link back to the store, products, account, and each other,
and include the existing AUDIA Assistant.

## Architecture findings

AUDIA creates its Flask app in `app.py`. Existing HTML page routes use Jinja
templates; authentication, catalog, orders, administration, and chatbot APIs
are registered as blueprints. Those APIs use `/api` prefixes. `modules/chatbot/ai/ai.py`
provides the Gemini/RAG service called by `modules/chatbot/chatbot.py`; it is not a
separate page blueprint. The database lifecycle lives in `modules/database/connection.py`,
and SQLAlchemy records live in `modules/database/models.py`. Normal development uses
PostgreSQL; tests use disposable SQLite databases.

Templates extend `templates/shared/base.html`. It loads `assets/css/shared/shared.css`, the
page's stylesheet, and `assets/js/shared/app.js`. Assets are served at `/static/`.
The shared stylesheet contains existing utilities, typography, cards, buttons,
dialogs, chatbot styling, and theme variables. Page controllers use ordinary
JavaScript modules. Repeated client-side components use HTML templates, and
navigation uses normal page URLs. Icons use the existing inline SVG style.

`modules/auth/auth.py` installs app-wide session restoration, CSRF checks, security
headers, and validation handlers. Pages inspect `g.user` and redirect guests
to `/login`; protected APIs use `require_user`. Mutating APIs require
`X-CSRF-Token`. `theme.js` and `app.js` apply the saved `audia-theme` preference
and the `html.dark` class. No new theme or authentication system was introduced.

The new modules use page blueprints to keep them independent, registered by
the same `app.register_blueprint` mechanism as existing modules. They follow
the existing page authentication and `render_template` conventions. Their
routes are read-only. No new database tables, migrations, npm dependencies,
Python dependencies, or audio upload endpoints were added.

## Files created and what each does

| File | Purpose |
| --- | --- |
| `modules/tuner/tuner.py` | Authenticated `/tuner` page blueprint; no audio reaches Python. |
| `modules/lessons/lessons.py` | Authenticated lesson routes and missing-chord 404 handling. |
| `modules/lessons/lessons_data.py` | Static chord shapes, finger instructions, and strumming patterns. |
| `templates/shared/practice_base.html` | Shared header, content area, and existing chatbot for both new features. |
| `templates/shared/practice_links.html` | Reusable links added below existing page headers, visible on mobile too. |
| `templates/tuner/tuner.html` | Live note readout, meter, microphone controls, errors, privacy text, and string reference. |
| `templates/lessons/lessons.html` | Lesson landing page and category links. |
| `templates/lessons/lessons_getting_started.html` | Guitar parts, posture, pick grip, string names, and tuning instructions. |
| `templates/lessons/lessons_chords.html` | Library of eight chords. |
| `templates/lessons/lessons_chord_detail.html` | One chord's diagram and playing instructions. |
| `templates/lessons/lessons_chord_diagram.html` | Reusable Jinja macro that draws an accessible SVG chord diagram. |
| `templates/lessons/lessons_strumming.html` | Down/up strokes, beat counts, patterns, and practice tips. |
| `assets/css/shared/practice.css` | Shared layout for these two features, using AUDIA's existing theme variables. |
| `assets/css/tuner/tuner.css` | Tuner layout, meter, note display, and string highlight. Imports `practice.css`. |
| `assets/css/lessons/lessons.css` | Lesson grids, chord diagrams, and strumming pattern layouts. Imports `practice.css`. |
| `assets/js/tuner/tuner.js` | Start/stop controls, audio resource cleanup, errors, and pitch display. |
| `assets/js/tuner/tuner_pitch.js` | Independent YIN pitch estimator, note/cents conversion, and stabilization. |
| `tests/test_practice.py` | Routes, auth, assets, navigation, chord structure, and session revocation tests. |
| `tests/tuner-pitch.cjs` | Deterministic pitch tests with generated harmonic signals. |
| `tests/practice.cjs` | Browser audio, error/lifecycle, lessons, responsive, and theme checks. |
| `docs/guitar-practice.md` | This architecture and operating guide. |
| `docs/archive/guitar-practice-source.md` | Historical implementation snapshot from before the architecture migration. |

Lessons are static server-rendered pages, so they do not need a `lessons.js`
controller. SVG diagrams and ordinary links work without another frontend
framework or external image service.

## Existing files minimally modified

| File | Change made for this task |
| --- | --- |
| `app.py` | Import and register the `tuner` and `lessons` blueprints: four added lines. |
| `assets/js/shared/app.js` | Include the two new page names in its existing signed-in check; dynamically start the tuner controller on the tuner page only. |
| `templates/landing/landing.html` | Include the practice navigation partial after the existing header. |
| `templates/catalog/catalog.html` | Include the same navigation partial after the existing header. |
| `templates/account/account.html` | Include the same navigation partial after the existing header. |

The working tree already contained many modified/deleted/untracked files before
this task. Those changes were preserved. The table above describes only this
task's additions to existing files, not the entire difference from Git HEAD.
Authentication, CSRF hooks, catalog/order/admin handlers, models, database
behavior, AI/RAG code, and chatbot code were not intentionally changed.

## Routes added

| URL | Content |
| --- | --- |
| `/tuner` | Microphone guitar tuner |
| `/lessons` | Learn Guitar landing page |
| `/lessons/getting-started` | Five linked beginner topics |
| `/lessons/chords` | Eight-chord library |
| `/lessons/chords/<slug>` | Individual chord lesson |
| `/lessons/strumming` | Three strumming patterns |

Chord slugs are `c-major`, `g-major`, `d-major`, `a-major`, `e-major`, `a-minor`,
`e-minor`, and `d-minor`. An unknown slug returns HTTP 404 for signed-in users.
Guests are redirected to login. GET routes also support Flask's normal HEAD
and OPTIONS behavior; they do not accept POST audio or lesson updates.

## How the tuner works

1. The page starts with the microphone inactive. Only **Start Tuner** requests
   microphone permission through `getUserMedia`.
2. An `AudioContext` connects the microphone to an `AnalyserNode`. It never
   connects the microphone to the speakers. Echo cancellation, automatic gain,
   and noise suppression are requested off to preserve sustained guitar tones;
   browsers may decide how to honor those constraints.
3. The analyser supplies a 4,096-sample waveform. Around twelve times per
   second, the pitch estimator examines it locally. No `MediaRecorder`, saved
   audio, microphone network request, or server audio processing is used.
4. Weak input and unreliable periodicity are discarded. Several consistent
   readings are required before a pitch is shown. Median filtering and gentle
   smoothing reduce jitter. Silence clears the readout and displays **Play a
   string**, and playing again restores it.
5. The closest chromatic note and octave appear with frequency and cents.
   Matching E2, A2, D3, G3, B3, or E4 highlights the standard string reference.
6. **Stop Tuner** stops every track, disconnects nodes, cancels the animation
   frame, and closes the audio context. Hiding or leaving the page does the
   same. Stopping during a pending permission request also stops any stream
   that arrives later. Errors allow the player to try again.

The pitch estimator follows [YIN by de Cheveigné and Kawahara](https://pubmed.ncbi.nlm.nih.gov/12002874/).
It compares a waveform with delayed copies, calculates the cumulative mean
normalized difference, selects a reliable period, and refines it with
parabolic interpolation. Frequency is sample rate divided by period. The
working signal is averaged into a lower sample rate to reduce processing.
The range is approximately 65–420 Hz, covering the six standard guitar strings
and nearby chromatic pitches.

With A4 = 440 Hz, note selection uses:

```text
midi = round(69 + 12 × log2(frequency / 440))
targetFrequency = 440 × 2^((midi - 69) / 12)
cents = 1200 × log2(frequency / targetFrequency)
```

Within ±5 cents is **In Tune**. Offsets up to ±15 cents are **Slightly Flat**
or **Slightly Sharp**; larger offsets are **Too Flat** or **Too Sharp**. The
meter centers on zero and spans −50 to +50 cents. The tuner chooses the
nearest musical note automatically, rather than locking to a manually
selected string. If a string is far from its intended note, consult the
standard string reference and check the octave.

## How chord diagrams are generated

Each chord has six `frets` entries, from low E (left) to high E (right).
`None` means muted (X), `0` means open (O), and a positive number places a
finger on that fret. Matching `fingers` entries specify 1 index, 2 middle,
3 ring, or 4 little finger. The macro draws six vertical strings, a thick
nut, four fret spaces, labels, open/muted indicators, and numbered circles.
It includes a title and description for screen readers, uses theme colors,
and preserves its SVG aspect ratio at every screen size.

To add a chord, add a record to `CHORDS` in `modules/lessons/lessons_data.py` with
its name, symbol, frets, fingers, placements, strings played/muted, and tip.
The library, detail route, and diagram will use that record automatically.

Strumming patterns store eight slots representing `1 & 2 & 3 & 4 &`. Empty
strokes remain visible as dashes, so syncopated patterns keep their beat
alignment. In `D D U U D U`, the sounding strokes land on 1, 2, & after 2,
& after 3, 4, and & after 4.

## Run and test

Use the existing configured environment and run:

```powershell
.venv/Scripts/python.exe app.py
```

Sign in normally, then visit `http://localhost:5000/tuner` and
`http://localhost:5000/lessons`. Existing PostgreSQL and Gemini configuration
requirements remain as they were. This task did not change runtime dependency
installation or environment files.

Server and algorithm checks:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py'
node tests/tuner-pitch.cjs
```

Browser checks use the existing disposable test server:

```powershell
# Terminal 1
.venv/Scripts/python.exe tests/serve.py

# Terminal 2: with Playwright available
node tests/practice.cjs
node tests/browser.cjs
node tests/chatbot.cjs
```

`PLAYWRIGHT_MODULE` can point to an existing Playwright installation. This
session used the existing npm cache installation, not a new project dependency:

```powershell
$env:PLAYWRIGHT_MODULE = 'C:\Users\daniel jay bernadas\AppData\Local\npm-cache\_npx\e41f203b7505f1fb\node_modules\playwright'
$env:SCREENSHOT_DIR = 'test-results/practice'
node tests/practice.cjs
```

Do not run fixture browser tests against a real customer database. The default
test URL is `http://127.0.0.1:5056`. Optional screenshots are ignored by Git.

## Verification results and limits

- Existing 20 server tests pass; four added tests pass. Python compilation
  succeeds. Route/asset checks include all new pages and every chord detail.
- Ninety generated harmonic pitch cases pass for six strings, three sample
  rates (44.1, 48, and 96 kHz), and five offsets (−25, −10, 0, +10, +25 cents).
  Silence, weak input, DC, broadband noise, and outlier stabilization pass.
- Chromium uses real Web Audio oscillators, media streams, analysers, and the
  application's pitch detector for all six string readings and meter states.
  It also checks actual `getUserMedia` capture with Chromium's fake device.
- Browser tests cover denial, missing/busy microphones, permission-pending
  cancellation, disconnect, stop/restart, silence recovery, hidden/left-page
  cleanup, unsupported audio APIs, and the insecure-address error. Some error
  and lifecycle conditions are simulated deterministically.
- All thirteen new pages pass both themes at 320, 375, 768, 1024, and 1440 px:
  130 layout cases without horizontal overflow or clipped target components.
  Chord SVGs retain their proportions, and patterns keep eight aligned beats.
  Screenshots were inspected in light and dark mode on desktop and mobile.
- Existing storefront/account/admin browser checks and chatbot browser checks
  pass, including shopping, orders, authorization, session revocation, error
  recovery, responsive layouts, themes, and CSRF retry behavior. No JavaScript
  errors or audio uploads were observed in the new feature browser suite.

Physical guitar/microphone quality and Safari/Firefox behavior have not been
verified with hardware here. AI browser checks use mocked responses; this
task did not call the paid Gemini service or change production PostgreSQL data.

Browsers require a secure context for microphone access: use HTTPS when
deployed or localhost for local development. A phone opening an ordinary
HTTP LAN IP generally needs HTTPS instead. Permissions may also be blocked
by OS settings, enterprise policy, embedding policy, or another app using the
microphone. See [MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).
Audio resource release uses track stops and [AudioContext.close](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/close).

The tuner works best with one open string in a quiet room. Chords, background
music, heavy distortion, very weak sustain, or strong harmonics can confuse
pitch estimation; it does not identify multiple simultaneous notes. Real
guitar tuning remains the final manual check: test all six strings, deny and
restore permission, stop and confirm the browser microphone indicator clears,
then repeat on a phone over HTTPS.

The historical implementation snapshot is preserved in
`archive/guitar-practice-source.md`. Complete current files changed by the
architecture migration are in `components/updated-files.md`, including
whole files rather than isolated snippets.
