"""Read-only beginner lesson pages using static content and Jinja diagrams."""
from flask import Blueprint, abort, g, redirect, render_template, url_for

from .lessons_data import CHORDS, STRUMMING_PATTERNS

lessons = Blueprint("lessons", __name__, url_prefix="/lessons")


@lessons.before_request
def require_signed_in_player():
    if not g.user:
        return redirect(url_for("login_page"))


def lesson_page(template, title, **content):
    return render_template(
        "lessons/" + template, title=title, page_name="lessons",
        stylesheet="lessons/lessons", practice_area="lessons", **content,
    )


@lessons.get("")
def index():
    return lesson_page("lessons.html", "Learn Guitar")


@lessons.get("/getting-started")
def getting_started():
    return lesson_page("lessons_getting_started.html", "Getting Started")


@lessons.get("/chords")
def chords():
    return lesson_page("lessons_chords.html", "Basic Chords", chords=CHORDS)


@lessons.get("/chords/<slug>")
def chord_detail(slug):
    chord = CHORDS.get(slug)
    if chord is None:
        abort(404)
    return lesson_page("lessons_chord_detail.html", chord["name"], chord=chord, slug=slug)


@lessons.get("/strumming")
def strumming():
    return lesson_page("lessons_strumming.html", "Strumming", patterns=STRUMMING_PATTERNS)
