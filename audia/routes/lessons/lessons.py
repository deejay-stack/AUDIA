"""Module: audia.routes.lessons.lessons.

Purpose: Render authenticated lesson pages and chord detail lookups.
Main components: lessons/lessons_api, page handlers, original curriculum, songs, progress and update_progress.
Related: lessons_data, templates/lessons, app-wide session restoration.
Debugging: Check chord slugs and lesson_page() template context for missing content.
"""
from flask import Blueprint, abort, g, jsonify, redirect, render_template, request, url_for

from .lessons_data import CHORDS, COURSES, SONGS, STRUMMING_PATTERNS
from audia.database import db
from audia.database.models import LessonProgress
from ..auth import payload, require_user
from sqlalchemy import select

lessons = Blueprint("lessons", __name__, url_prefix="/lessons")
lessons_api = Blueprint("lessons_api", __name__, url_prefix="/api/lessons")


@lessons.before_request
def require_signed_in_player():
    if not g.user:
        return redirect(url_for("login_page"))


def lesson_page(template, title, **content):
    """Render template with title and content using the shared lesson context.

    Returns HTML for lesson handlers; Jinja errors propagate for debugging.
    """
    return render_template(
        "lessons/" + template, title=title, page_name="lessons",
        stylesheet="lessons/lessons", practice_area="lessons", **content,
    )


@lessons.get("")
def index():
    return lesson_page("lessons.html", "Learn Guitar", courses=COURSES)


@lessons.get("/getting-started")
def getting_started():
    return lesson_page("lessons_getting_started.html", "Getting Started")


@lessons.get("/chords")
def chords():
    family, difficulty = request.args.get('family', ''), request.args.get('difficulty', '')
    filtered = {slug: chord for slug, chord in CHORDS.items()
                if (not family or chord['family'] == family) and (not difficulty or chord['difficulty'] == difficulty)}
    return lesson_page("lessons_chords.html", "Chord Library", chords=filtered, family=family, difficulty=difficulty)


@lessons.get("/chords/<slug>")
def chord_detail(slug):
    chord = CHORDS.get(slug)
    if chord is None:
        abort(404)
    return lesson_page("lessons_chord_detail.html", chord["name"], chord=chord, slug=slug)


@lessons.get("/strumming")
def strumming():
    return lesson_page("lessons_strumming.html", "Strumming", patterns=STRUMMING_PATTERNS)


@lessons.get('/practice/<slug>')
def practice(slug):
    """Render an original curriculum lesson and adjacent navigation; unknown slugs return 404."""
    course = COURSES.get(slug)
    if course is None:
        abort(404)
    slugs = list(COURSES)
    index = slugs.index(slug)
    return lesson_page('lessons_practice.html', course['title'], course=course, slug=slug,
                       chords=CHORDS, previous=slugs[index-1] if index else None,
                       following=slugs[index+1] if index+1 < len(slugs) else None)


@lessons.get('/songs')
def songs():
    return lesson_page('lessons_songs.html', 'Original Song Practice', songs=SONGS)


@lessons_api.get('/progress')
@require_user()
def progress():
    """Return only the signed-in player's completed curriculum slugs."""
    return jsonify(completed=list(db().scalars(select(LessonProgress.lesson_slug).where(LessonProgress.user_id == g.user.id))))


@lessons_api.put('/progress/<slug>')
@require_user()
def update_progress(slug):
    """Persist a validated completion flag; ownership comes from the server session."""
    if slug not in COURSES:
        abort(404)
    completed = payload().get('completed')
    if type(completed) is not bool:
        raise ValueError('Choose a valid lesson completion value.')
    key = (g.user.id, slug)
    record = db().get(LessonProgress, key)
    if completed and record is None:
        db().add(LessonProgress(user_id=g.user.id, lesson_slug=slug))
    elif not completed and record is not None:
        db().delete(record)
    db().commit()
    return jsonify(slug=slug, completed=completed)
