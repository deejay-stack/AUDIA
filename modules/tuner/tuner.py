"""The signed-in guitar tuner page; microphone audio stays in the browser."""
from flask import Blueprint, g, redirect, render_template, url_for

tuner = Blueprint("tuner", __name__, url_prefix="/tuner")


@tuner.before_request
def require_signed_in_player():
    if not g.user:
        return redirect(url_for("login_page"))


@tuner.get("")
def index():
    return render_template(
        "tuner/tuner.html", title="Guitar Tuner", page_name="tuner",
        stylesheet="tuner/tuner", practice_area="tuner",
    )
