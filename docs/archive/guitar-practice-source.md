# AUDIA guitar practice: complete updated files

This snapshot includes every file added or edited for this task, except this generated snapshot itself. Existing integration files are included in full, preserving the changes already present before this task. See guitar-practice.md for the architecture, file purposes, routes, run instructions, and verification.

## app.py

```python
import os
import secrets
from datetime import timedelta
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import (
    Flask,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import URL, text
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash


# ---------------------------------------------------------
# 1. Load environment variables FIRST
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parent

load_dotenv(ROOT / ".env")


# ---------------------------------------------------------
# 2. Import AUDIA modules AFTER .env has been loaded
# ---------------------------------------------------------

from modules.admin import admin
from modules.auth import (
    auth,
    install_security,
    validate_email,
    validate_password,
)
from modules.catalog import catalog
from modules.chatbot import chatbot
from modules.database import db, init_database, initialize
from modules.models import User
from modules.orders import orders
from modules.tuner import tuner
from modules.lessons import lessons


# ---------------------------------------------------------
# 3. Create Flask application
# ---------------------------------------------------------

app = Flask(
    __name__,
    static_folder="assets",
    static_url_path="/static",
    template_folder="templates",
    instance_path=str(ROOT / "instance"),
)


# ---------------------------------------------------------
# 4. Build PostgreSQL database URL
# ---------------------------------------------------------

def build_database_url():
    """
    Build the PostgreSQL URL from the separate
    credentials stored in .env.

    Falls back to DATABASE_URL if the separate
    credentials are not available.
    """

    required_variables = (
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    )

    if not all(
        os.getenv(name)
        for name in required_variables
    ):
        return os.getenv(
            "DATABASE_URL",
            "",
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),
        port=int(
            os.getenv(
                "DB_PORT",
                "5432",
            )
        ),
        database=os.getenv("DB_NAME"),
    )


# ---------------------------------------------------------
# 5. Application configuration
# ---------------------------------------------------------

app.config.update(
    DATABASE_URL=build_database_url(),

    SECRET_KEY=os.getenv(
        "SECRET_KEY"
    ),

    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",

    SESSION_COOKIE_SECURE=(
        os.getenv(
            "COOKIE_SECURE",
            "false",
        ).lower()
        == "true"
    ),

    PERMANENT_SESSION_LIFETIME=timedelta(
        days=30
    ),

    MAX_CONTENT_LENGTH=64 * 1024,

    MAIL_BACKEND=os.getenv(
        "MAIL_BACKEND",
        "disabled",
    ),

    SMTP_HOST=os.getenv(
        "SMTP_HOST",
        "",
    ),

    SMTP_PORT=int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    ),

    SMTP_USER=os.getenv(
        "SMTP_USER",
        "",
    ),

    SMTP_PASSWORD=os.getenv(
        "SMTP_PASSWORD",
        "",
    ),

    SMTP_FROM=os.getenv(
        "SMTP_FROM",
        "noreply@audia.local",
    ),

    APP_URL=os.getenv(
        "APP_URL",
        "http://localhost:5000",
    ).rstrip("/"),
)


# ---------------------------------------------------------
# 6. Secret key fallback
# ---------------------------------------------------------

if not app.config["SECRET_KEY"]:

    Path(
        app.instance_path
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    key_file = (
        Path(app.instance_path)
        / ".secret-key"
    )

    try:
        with key_file.open(
            "x",
            encoding="utf-8",
        ) as file:

            file.write(
                secrets.token_hex(32)
            )

    except FileExistsError:
        pass

    app.config["SECRET_KEY"] = (
        key_file.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------
# 7. Initialize PostgreSQL
# ---------------------------------------------------------

init_database(app)


# ---------------------------------------------------------
# 8. Register blueprints
# ---------------------------------------------------------

app.register_blueprint(auth)
app.register_blueprint(catalog)
app.register_blueprint(orders)
app.register_blueprint(admin)

# Gemini chatbot
app.register_blueprint(chatbot)
app.register_blueprint(tuner)
app.register_blueprint(lessons)


# Install authentication/security hooks
install_security(app)


# ---------------------------------------------------------
# 9. Pages
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template(
        "landing.html",
        title="Find your sound",
        page_name="landing",
        stylesheet="landing",
    )


@app.route("/login")
def login_page():

    if g.user:
        return redirect(
            url_for(
                "dashboard"
                if g.user.role == "admin"
                else "shop"
            )
        )

    mode = (
        "admin"
        if request.args.get("role") == "admin"
        else "login"
    )

    return render_template(
        "auth.html",
        title="Sign in",
        page_name="auth",
        stylesheet="auth",
        auth_mode=mode,
    )


@app.route("/register")
def register_page():

    if g.user:
        return redirect(
            url_for("shop")
        )

    return render_template(
        "auth.html",
        title="Create an account",
        page_name="auth",
        stylesheet="auth",
        auth_mode="register",
    )


@app.route("/reset-password")
def reset_password_page():

    return render_template(
        "auth.html",
        title="Reset your password",
        page_name="auth",
        stylesheet="auth",
        auth_mode="reset",
        reset_token=request.args.get(
            "token",
            "",
        ),
    )


@app.route("/shop")
def shop():

    if not g.user:
        return redirect(
            url_for("login_page")
        )

    return render_template(
        "storefront.html",
        title="Guitar shop",
        page_name="storefront",
        stylesheet="storefront",
    )


@app.route("/account")
def account_page():

    if not g.user:
        return redirect(
            url_for("login_page")
        )

    return render_template(
        "account.html",
        title="My account",
        page_name="account",
        stylesheet="account",
    )


@app.route("/admin")
def dashboard():

    if not g.user:
        return redirect(
            url_for(
                "login_page",
                role="admin",
            )
        )

    if g.user.role != "admin":
        return redirect(
            url_for("shop")
        )

    return render_template(
        "admin.html",
        title="Administration",
        page_name="dashboard",
        stylesheet="admin",
    )


# ---------------------------------------------------------
# 10. Health endpoint
# ---------------------------------------------------------

@app.route("/api/health")
def health():

    if "engine" not in current_app.extensions:

        return jsonify(
            status="setup_required",
            database="not_configured",
        ), 503

    db().execute(
        text("SELECT 1")
    )

    return jsonify(
        status="ok",
        service="AUDIA",
        database="connected",
    )

# ---------------------------------------------------------
# 11. Error handlers
# ---------------------------------------------------------

@app.errorhandler(
    OperationalError
)
def database_unavailable(error):

    if g.get("db"):
        g.db.rollback()

    return jsonify(
        error=(
            "The database is unavailable. "
            "Please try again shortly."
        )
    ), 503


@app.errorhandler(503)
def service_unavailable(error):

    return jsonify(
        error=(
            "Account and order services "
            "are not available yet. "
            "Please try again later."
        )
    ), 503


@app.errorhandler(413)
def request_too_large(error):

    return jsonify(
        error="This request is too large."
    ), 413


# ---------------------------------------------------------
# 12. CLI: initialize database
# ---------------------------------------------------------

@app.cli.command(
    "init-db"
)
def init_db():
    """
    Create missing tables and seed an empty
    catalog without deleting existing data.
    """

    initialize(
        current_app
    )

    click.echo(
        "Database ready. "
        "Catalog seed applied where needed."
    )


# ---------------------------------------------------------
# 13. CLI: create administrator
# ---------------------------------------------------------

@app.cli.command(
    "create-admin"
)
@click.option(
    "--email",
    prompt=True,
)
@click.option(
    "--name",
    default="AUDIA Admin",
    prompt=True,
)
@click.password_option()
def create_admin(
    email,
    name,
    password,
):

    try:

        email = validate_email(
            email
        )

        validate_password(
            password
        )

    except ValueError as error:

        raise click.ClickException(
            str(error)
        ) from error

    existing_user = (
        db()
        .query(User)
        .filter_by(
            email=email
        )
        .first()
    )

    if existing_user:

        raise click.ClickException(
            "That email already exists; "
            "no account was changed."
        )

    admin_user = User(
        name=name.strip(),
        email=email,
        password_hash=generate_password_hash(
            password
        ),
        role="admin",
    )

    db().add(
        admin_user
    )

    db().commit()

    click.echo(
        "Administrator created."
    )

@app.cli.command("sync-rag")
def sync_rag():
    """
    Synchronize AUDIA product knowledge
    with the RAG database.
    """

    from modules.rag_sync import (
        sync_products_to_rag,
    )

    try:

        result = sync_products_to_rag()

        click.echo(
            f"RAG synchronization complete. "
            f"{result['indexed']} products indexed, "
            f"{result['removed']} stale documents removed."
        )

    except Exception:

        db().rollback()

        current_app.logger.exception(
            "RAG synchronization failed."
        )

        raise click.ClickException(
            "RAG synchronization failed. "
            "Check the error above."
        )
# ---------------------------------------------------------
# 14. Run development server
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",

        port=int(
            os.getenv(
                "PORT",
                "5000",
            )
        ),

        debug=(
            os.getenv(
                "FLASK_DEBUG",
                "0",
            )
            == "1"
        ),
    )
```

## assets/js/app.js

```javascript
// Flask chooses the page. This file starts that page's interactive features.
import { initChatbot } from "./chatbot/chatbot.js";
import { mountStore } from "./storefront.js";
import { mountAuth } from "./auth.js";
import { mountAdmin } from "./admin.js";
import { mountAccount } from "./account.js";
import { $$, icon, animate, api, notice, writeCart } from "./shared.js";

const root = document.getElementById("root");
const page = root.firstElementChild;
const pageName = document.body.dataset.page;
let user = null;
let theme = localStorage.getItem("audia-theme") || "dark";

// Keep only small navigation preferences across normal page loads.
const app = {
  get user() {
    return user;
  },
  set user(value) {
    user = value;
  },
  get catalogCategory() {
    return sessionStorage.getItem("audia-category") || "";
  },
  set catalogCategory(value) {
    sessionStorage.setItem("audia-category", value);
  },
  get searchProduct() {
    return sessionStorage.getItem("audia-search") || "";
  },
  set searchProduct(value) {
    sessionStorage.setItem("audia-search", value);
  },
  get openFinder() {
    return sessionStorage.getItem("audia-finder") === "true";
  },
  set openFinder(value) {
    sessionStorage.setItem("audia-finder", String(value));
  },
  resetToken: document.body.dataset.resetToken || "",
  navigate(screen, role = "customer") {
    const pages = {
      landing: "/",
      storefront: "/shop",
      account: "/account",
      dashboard: "/admin",
    };
    let url = pages[screen] || "/login";
    if (screen === "auth" && role === "register") url = "/register";
    if (screen === "auth" && role === "admin") url = "/login?role=admin";
    window.location.assign(url);
  },
  login(account) {
    user = account;
    app.navigate(account.role === "admin" ? "dashboard" : "storefront");
  },
  async logout() {
    try {
      await api("/auth/logout", { method: "POST" });
      user = null;
      writeCart([]);
      app.navigate("landing");
    } catch (error) {
      notice(error.message);
    }
  },
};

function updateTheme() {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem("audia-theme", theme);
  $$(root, '[data-action="theme"]').forEach((button) => {
    const label = `Switch to ${theme === "dark" ? "light" : "dark"} mode`;
    button.setAttribute("aria-label", label);
    button.title = label;
    button.replaceChildren(icon(theme === "dark" ? "sun" : "moon", 17));
  });
}
root.addEventListener("click", (event) => {
  if (event.target.closest('[data-action="theme"]')) {
    theme = theme === "dark" ? "light" : "dark";
    updateTheme();
  }
});
window.addEventListener("audia:unauthorized", () => {
  if (!user) return;
  user = null;
  writeCart([]);
  app.navigate("auth");
});

// Old bookmarks and emailed reset links remain usable after the route change.
function followOldBookmark() {
  const legacy = {
    "#storefront": "/shop",
    "#auth": "/login",
    "#account": "/account",
    "#dashboard": "/admin",
    "#landing": "/",
  };
  if (legacy[location.hash]) {
    location.replace(legacy[location.hash]);
    return true;
  }
  if (location.hash.startsWith("#reset/")) {
    location.replace(
      "/reset-password?token=" + encodeURIComponent(location.hash.slice(7)),
    );
    return true;
  }
  return false;
}
window.addEventListener("hashchange", followOldBookmark);

if (!followOldBookmark()) {
  try {
    user = (await api("/auth/session")).user;
  } catch (error) {
    notice(error.message);
  }

  if (["storefront", "account", "dashboard", "tuner", "lessons"].includes(pageName) && !user) {
    app.navigate("auth");
  } else {
    if (pageName === "storefront") mountStore(page, app);
    if (pageName === "auth")
      mountAuth(page, app, document.body.dataset.authMode);
    if (pageName === "account") mountAccount(page, app);
    if (pageName === "dashboard") mountAdmin(page, app);
    if (pageName === "tuner") (await import("./tuner.js")).mountTuner(page);
    if (pageName === "landing") {
      page.querySelectorAll("[data-auth-entry]").forEach((node) => {
        node.hidden = Boolean(user);
      });
      page.querySelectorAll("[data-member-entry]").forEach((node) => {
        node.hidden = !user;
      });
      page.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action]");
        if (!button) return;
        const action = button.dataset.action;
        if (action === "register") app.navigate("auth", "register");
        if (action === "sign-in") app.navigate("auth");
        if (action === "browse") {
          app.catalogCategory = button.dataset.category || "";
          app.navigate(user ? "storefront" : "auth");
        }
      });
    }
    initChatbot(page);
    updateTheme();
    animate(page);
    // Enable controls after their handlers and session have loaded.
    root.inert = false;
    root.removeAttribute("aria-busy");
  }
}
```

## templates/landing.html

```html
{% extends "base.html" %} {% block content %}
<div class="landing-page">
  <header class="landing-header">
    <div class="shell landing-nav">
      <a class="audia-mark" href="#welcome" aria-label="AUDIA home"
        ><span class="mark-a">A</span>UDI<span class="mark-a">A</span></a
      >
      <nav aria-label="About AUDIA">
        <a href="#about-audia">About</a>
        <a href="#guitar-families">Guitar families</a>
        <a href="#how-it-works">How it works</a>
      </nav>
      <div class="landing-nav-actions">
        <button
          class="landing-theme"
          data-action="theme"
          aria-label="Switch to light mode"
        ></button>
        <button class="secondary-btn" data-action="sign-in" data-auth-entry>
          Sign in
        </button>
        <button
          class="secondary-btn"
          data-action="browse"
          data-member-entry
          hidden
        >
          Browse guitars
        </button>
      </div>
    </div>
  </header>
  {% include 'practice/feature_links.html' %}
  <main>
    <section id="welcome" class="shell landing-hero">
      <div class="landing-hero-copy">
        <p class="section-label">Meet AUDIA</p>
        <h1>
          Your sound.<br /><span class="hero-gradient"
            >Your starting point.</span
          >
        </h1>
        <p>
          A place to discover guitars and find what fits your music. AUDIA
          brings instrument details, guided recommendations, and a simple
          shopping experience together in one account.
        </p>
        <div class="landing-actions">
          <button class="primary-btn" data-action="register" data-auth-entry>
            Create an account <span aria-hidden="true">↗</span>
          </button>
          <button
            class="primary-btn"
            data-action="browse"
            data-member-entry
            hidden
          >
            Explore the catalog <span aria-hidden="true">↗</span>
          </button>
          <a class="landing-text-link" href="#about-audia"
            >Take a quick look <span aria-hidden="true">↓</span></a
          >
        </div>
        <p class="landing-access-note">
          Sign in to browse all instruments, save favorites, and shop.
        </p>
        <div class="landing-hero-details">
          <span>Four guitar families</span
          ><span>One place to find your sound</span>
        </div>
      </div>
      <figure class="landing-hero-photo">
        <img
          src="{{ url_for('static', filename='images/guitar_front.jpg') }}"
          alt="Acoustic guitar in a studio with instruments and amplifiers"
          fetchpriority="high"
        />
        <figcaption>
          <span>A little inspiration</span
          ><strong>Every player starts somewhere.</strong>
        </figcaption>
      </figure>
    </section>
    <section id="about-audia" class="landing-about">
      <div class="shell">
        <div class="landing-section-heading">
          <div>
            <p class="section-label">The system at a glance</p>
            <h2 class="section-title">
              Less guesswork.<br />More making music.
            </h2>
          </div>
          <p>
            Whether you are picking up your first guitar or exploring a
            different style, AUDIA helps you compare your options and keep your
            choices in one place.
          </p>
        </div>
        <div class="landing-features">
          <article>
            <span class="landing-step">01 / DISCOVER</span>
            <h3>Know what you are choosing.</h3>
            <p>
              See each instrument's photo, description, price, and availability.
              Browse by guitar family or search for a specific catalog code.
            </p>
          </article>
          <article>
            <span class="landing-step">02 / FIND YOUR FIT</span>
            <h3>A little guidance goes a long way.</h3>
            <p>
              Guitar Finder uses your budget, experience, and preferred guitar
              type to suggest instruments. Save the ones you want to revisit.
            </p>
          </article>
          <article>
            <span class="landing-step">03 / KEEP IT TOGETHER</span>
            <h3>From your shortlist to your doorstep.</h3>
            <p>
              Add instruments to your cart, check out with your delivery
              details, and follow your order status from your account.
            </p>
          </article>
        </div>
      </div>
    </section>
    <section id="guitar-families" class="shell landing-collections">
      <div class="landing-section-heading">
        <div>
          <p class="section-label">A quick introduction</p>
          <h2 class="section-title">Choose your voice.</h2>
        </div>
        <p>
          Get to know the four guitar families. Sign in when you are ready to
          explore individual instruments.
        </p>
      </div>
      <div class="landing-collection-grid">
        {% for category, caption, description in [ ('Electric', 'Plug into
        possibility.', 'Explore amplified sounds, effects, and styles from clean
        pop to rock.'), ('Acoustic', 'Let the song lead.', 'A familiar starting
        point for unplugged strumming and fingerpicking.'), ('Classical', 'Make
        room for the details.', 'Discover traditional shapes suited to classical
        and fingerstyle study.'), ('Bass', 'Give the music its pulse.', 'Build
        the low-end foundation and connect melody with rhythm.') ] %}
        <button
          class="landing-collection"
          data-action="browse"
          data-category="{{ category }}"
          aria-label="Explore {{ category|lower }} guitars"
        >
          <span class="landing-collection-photo">
            <img
              src="{{ url_for('static', filename='images/' ~ category|lower ~ '_studio.jpg') }}"
              alt="{{ category }} guitar in a studio"
              loading="lazy"
              decoding="async"
            />
            <span class="landing-collection-label"
              ><strong>{{ category }}</strong
              ><span aria-hidden="true">↗</span></span
            >
          </span>
          <span class="landing-collection-copy"
            ><strong>{{ caption }}</strong><span>{{ description }}</span></span
          >
        </button>
        {% endfor %}
      </div>
    </section>
    <section id="how-it-works" class="shell landing-how">
      <div>
        <p class="section-label">Your next step</p>
        <h2 class="section-title">A simple path<br />to your next guitar.</h2>
        <p class="landing-how-intro">
          Your account opens the full AUDIA experience.
        </p>
      </div>
      <ol class="landing-steps">
        <li>
          <span>01</span>
          <div>
            <h3>Create your account.</h3>
            <p>
              Sign up or sign in to unlock the catalog and your personal
              workspace.
            </p>
          </div>
        </li>
        <li>
          <span>02</span>
          <div>
            <h3>Explore and compare.</h3>
            <p>
              Browse guitar families, try Guitar Finder, and save your
              favorites.
            </p>
          </div>
        </li>
        <li>
          <span>03</span>
          <div>
            <h3>Shop when you are ready.</h3>
            <p>
              Add your selections to the cart, check out, and track your order.
            </p>
          </div>
        </li>
      </ol>
    </section>
    <section class="shell landing-join">
      <div>
        <p class="section-label">Find your sound</p>
        <h2 class="section-title">Ready to take a closer look?</h2>
        <p>The full collection is waiting inside.</p>
      </div>
      <button class="primary-btn" data-action="browse">
        Explore the catalog <span aria-hidden="true">↗</span>
      </button>
    </section>
  </main>
  <footer class="shell landing-footer">
    <a class="audia-mark" href="#welcome">AUDIA</a>
    <p>Discover. Compare. Find your sound.</p>
    <span>School project · Demo catalog</span>
  </footer>
  {% include 'chatbot.html' %}
</div>
{% endblock %}
```

## templates/storefront.html

```html
{% extends "base.html" %} {% block content %}
<div class="storefront min-h-screen overflow-x-clip">
  <div
    class="announcement px-5 py-2.5 text-center font-semibold uppercase tracking-[.18em]"
  >
    Free nationwide delivery over ₱15,000
    <span class="mx-2 opacity-40">•</span> Professional setup included
  </div>
  <header
    class="store-header sticky top-0 z-40 border-b border-zinc-200/80 bg-stone-50/90 backdrop-blur-xl dark:border-white/10 dark:bg-ink/90"
  >
    <div class="shell flex h-[76px] items-center justify-between">
      <button
        class="audia-mark flex items-center text-left text-lg"
        aria-label="Go to AUDIA home"
        data-action="home"
      >
        <span class="mark-a">A</span>UDI<span class="mark-a">A</span>
      </button>
      <nav
        class="hidden items-center gap-8 text-sm font-medium text-zinc-600 dark:text-zinc-400 lg:flex"
      >
        <a class="nav-link" href="#shop">Shop</a>
        <a class="nav-link" href="#categories">Guitars</a>
        <button class="nav-link flex items-center gap-2" data-action="finder">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-compass"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <path
              d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
            ></path>
          </svg>
          Guitar finder
        </button>
        <a class="nav-link" href="#bundles">Bundles</a>
        <a class="nav-link" href="#track">Track order</a>
      </nav>
      <div class="flex items-center gap-1.5">
        <button
          class="theme-toggle relative flex items-center rounded-full border border-zinc-200 bg-white text-zinc-700 shadow-sm transition hover:border-zinc-300 dark:border-white/10 dark:bg-white/[.05] dark:text-zinc-200 h-10 w-10 justify-center"
          aria-label="Switch to light mode"
          title="Switch to light mode"
          data-action="theme"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-sun"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 2v2"></path>
            <path d="M12 20v2"></path>
            <path d="m4.93 4.93 1.41 1.41"></path>
            <path d="m17.66 17.66 1.41 1.41"></path>
            <path d="M2 12h2"></path>
            <path d="M20 12h2"></path>
            <path d="m6.34 17.66-1.41 1.41"></path>
            <path d="m19.07 4.93-1.41 1.41"></path>
          </svg>
        </button>
        <button class="icon-btn" aria-label="Search" data-action="search">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-search"
            aria-hidden="true"
          >
            <path d="m21 21-4.34-4.34"></path>
            <circle cx="11" cy="11" r="8"></circle>
          </svg>
        </button>
        <button
          class="icon-btn hidden sm:grid"
          aria-label="Sign in"
          data-action="account"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-circle-user-round"
            aria-hidden="true"
          >
            <path d="M17.925 20.056a6 6 0 0 0-11.851.001"></path>
            <circle cx="12" cy="11" r="4"></circle>
            <circle cx="12" cy="12" r="10"></circle>
          </svg>
        </button>
        <button
          class="icon-btn relative"
          aria-label="Open cart"
          data-action="cart"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-shopping-bag"
            aria-hidden="true"
          >
            <path d="M16 10a4 4 0 0 1-8 0"></path>
            <path d="M3.103 6.034h17.794"></path>
            <path
              d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"
            ></path>
          </svg>
        </button>
        <button
          class="icon-btn lg:hidden"
          aria-label="Open menu"
          data-action="menu"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-menu"
            aria-hidden="true"
          >
            <path d="M4 5h16"></path>
            <path d="M4 12h16"></path>
            <path d="M4 19h16"></path>
          </svg>
        </button>
      </div>
    </div>
  </header>
  {% include 'practice/feature_links.html' %}
  <main>
    <section
      id="top"
      class="hero-section relative overflow-hidden border-b border-zinc-200 dark:border-white/10"
    >
      <div aria-hidden="true" class="hero-mesh absolute inset-0"></div>
      <div
        class="shell hero-layout relative grid items-center gap-12 py-16 lg:grid-cols-[1.05fr_1fr] lg:py-10"
      >
        <div
          class="hero-copy relative z-10 max-w-xl"
          data-motion='{"initial":{"opacity":0,"y":32},"animate":{"opacity":1,"y":0},"transition":{"duration":0.8,"ease":[0.22,1,0.36,1]},"viewport":false}'
        >
          <p class="section-label hero-eyebrow">
            <span class="status-dot" aria-hidden="true"></span> The 2026
            electric edit
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-arrow-up-right"
              aria-hidden="true"
            >
              <path d="M7 7h10v10"></path>
              <path d="M7 17 17 7"></path>
            </svg>
          </p>
          <h1
            class="mt-5 font-display text-[clamp(3.4rem,7.5vw,7rem)] font-semibold leading-[.88] tracking-[-.065em]"
          >
            Make some<br /><span class="hero-gradient">noise.</span>
          </h1>
          <p
            class="mt-7 max-w-lg text-base leading-7 text-zinc-600 dark:text-zinc-400 sm:text-lg"
          >
            Discover guitars chosen for feel, tone, and lasting value. Compare
            the details, listen to a preview, and find an instrument you’ll keep
            reaching for.
          </p>
          <div class="mt-9 flex flex-col gap-3 sm:flex-row">
            <a href="#shop" class="primary-btn"
              >Shop guitars
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-arrow-right"
                aria-hidden="true"
              >
                <path d="M5 12h14"></path>
                <path d="m12 5 7 7-7 7"></path></svg
            ></a>
            <button class="secondary-btn" data-action="finder">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-compass"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <path
                  d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
                ></path>
              </svg>
              Find my guitar
            </button>
          </div>
          <div
            class="hero-stats mt-12 grid grid-cols-3 border-t border-zinc-200 pt-6 dark:border-white/10"
          >
            <div>
              <div class="font-display text-xl font-semibold sm:text-2xl">
                120+
              </div>
              <div
                class="mt-1 text-[9px] uppercase tracking-[.16em] text-zinc-500 sm:text-[10px]"
              >
                instruments
              </div>
            </div>
            <div>
              <div class="font-display text-xl font-semibold sm:text-2xl">
                4.9
              </div>
              <div
                class="mt-1 text-[9px] uppercase tracking-[.16em] text-zinc-500 sm:text-[10px]"
              >
                buyer rating
              </div>
            </div>
            <div>
              <div class="font-display text-xl font-semibold sm:text-2xl">
                2-year
              </div>
              <div
                class="mt-1 text-[9px] uppercase tracking-[.16em] text-zinc-500 sm:text-[10px]"
              >
                warranty
              </div>
            </div>
          </div>
        </div>
        <div
          class="hero-visual relative"
          data-motion='{"initial":{"opacity":0,"scale":0.96},"animate":{"opacity":1,"scale":1},"transition":{"duration":1,"delay":0.12,"ease":[0.22,1,0.36,1]},"viewport":false}'
        >
          <div class="sound-orbit orbit-one" aria-hidden="true"></div>
          <div class="sound-orbit orbit-two" aria-hidden="true"></div>
          <div class="hero-photo absolute overflow-hidden bg-zinc-900">
            <img
              class="h-full w-full object-cover object-center transition duration-1000 hover:scale-[1.025]"
              src="{{ url_for('static', filename='images/guitar_front.jpg') }}"
              alt="Guitars and amplifiers in a studio"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/75 via-transparent to-black/5"
            ></div>
            <div
              class="hero-photo-caption absolute bottom-6 left-6 right-6 flex items-end justify-between gap-3 text-white sm:left-8 sm:right-8"
            >
              <div>
                <p
                  class="text-[10px] font-semibold uppercase tracking-[.18em] text-white/60"
                >
                  Featured sound
                </p>
                <h2 class="mt-2 font-display text-2xl font-semibold">
                  Midnight Drive
                </h2>
                <p class="mt-1 text-xs text-white/60">
                  Warm humbuckers · crisp overdrive
                </p>
              </div>
              <button
                class="h-11 gap-2 px-4 inline-flex items-center justify-center rounded-full bg-white text-zinc-950 shadow-lg transition hover:scale-105"
                aria-label="Play guitar tone"
                data-action="sound"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-play"
                  aria-hidden="true"
                >
                  <path
                    d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"
                  ></path>
                </svg>
                <span class="text-xs font-semibold">Hear the tone</span>
              </button>
            </div>
          </div>
          <div
            class="setup-note absolute right-0 top-3 rounded-2xl border border-zinc-200 bg-white p-4 shadow-xl dark:border-white/10 dark:bg-zinc-900 sm:right-1 sm:top-12"
          >
            <div class="flex items-center gap-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-guitar"
                aria-hidden="true"
              >
                <path d="m11.9 12.1 4.514-4.514"></path>
                <path
                  d="M20.1 2.3a1 1 0 0 0-1.4 0l-1.114 1.114A2 2 0 0 0 17 4.828v1.344a2 2 0 0 1-.586 1.414A2 2 0 0 1 17.828 7h1.344a2 2 0 0 0 1.414-.586L21.7 5.3a1 1 0 0 0 0-1.4z"
                ></path>
                <path d="m6 16 2 2"></path>
                <path
                  d="M8.23 9.85A3 3 0 0 1 11 8a5 5 0 0 1 5 5 3 3 0 0 1-1.85 2.77l-.92.38A2 2 0 0 0 12 18a4 4 0 0 1-4 4 6 6 0 0 1-6-6 4 4 0 0 1 4-4 2 2 0 0 0 1.85-1.23z"
                ></path>
              </svg>
              <div>
                <p class="text-xs font-semibold">Free setup</p>
                <p class="mt-0.5 text-[10px] text-zinc-500">
                  Ready to play on arrival
                </p>
              </div>
            </div>
          </div>
          <div class="sound-signature" aria-hidden="true">
            <span class="sound-signature-icon">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-volume2 lucide-volume-2"
                aria-hidden="true"
              >
                <path
                  d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"
                ></path>
                <path d="M16 9a5 5 0 0 1 0 6"></path>
                <path d="M19.364 18.364a9 9 0 0 0 0-12.728"></path>
              </svg>
            </span>
            <div>
              <span class="sound-signature-label">Find your frequency</span>
              <div class="sound-wave">
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
                <i></i>
              </div>
            </div>
            <span class="sound-signature-type">100% YOU</span>
          </div>
        </div>
      </div>
      <div class="hero-bottom">
        <div class="shell flex flex-wrap items-center justify-between gap-4">
          <span>GOOD GEAR. GREAT POSSIBILITIES.</span>
          <span class="flex items-center gap-2"
            ><span class="status-dot" aria-hidden="true"></span> Your sound
            starts here
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-arrow-right"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="m12 5 7 7-7 7"></path></svg
          ></span>
        </div>
      </div>
    </section>
    <section id="categories" class="shell py-24 sm:py-28">
      <div
        class="mb-10 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div>
          <p class="section-label">Browse the collection</p>
          <h2 class="section-title">Choose your voice.</h2>
        </div>
        <p class="max-w-sm text-sm leading-6 text-zinc-500">
          Start with the instrument family that fits the sound in your head.
        </p>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Electric"
          >
            <img
              src="{{ url_for('static', filename='images/electric_studio.jpg') }}"
              alt="Electric guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  01 · <span data-category-count="Electric">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">
                  Electric
                </h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0.07,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Acoustic"
          >
            <img
              src="{{ url_for('static', filename='images/acoustic_studio.jpg') }}"
              alt="Acoustic guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  02 · <span data-category-count="Acoustic">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">
                  Acoustic
                </h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0.14,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Classical"
          >
            <img
              src="{{ url_for('static', filename='images/classical_studio.jpg') }}"
              alt="Classical guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  03 · <span data-category-count="Classical">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">
                  Classical
                </h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
        <div
          class=""
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0.21000000000000002,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <button
            class="category-card group relative h-[390px] w-full overflow-hidden rounded-2xl bg-zinc-900 text-left shadow-sm"
            data-hover='{"y":-7}'
            data-action="category"
            data-category="Bass"
          >
            <img
              src="{{ url_for('static', filename='images/bass_studio.jpg') }}"
              alt="Bass guitar"
              class="h-full w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent"
            ></div>
            <div
              class="absolute inset-x-0 bottom-0 flex items-end justify-between p-6 text-white"
            >
              <div>
                <p class="text-[10px] uppercase tracking-[.16em] text-white/55">
                  04 · <span data-category-count="Bass">10</span> models
                </p>
                <h3 class="mt-2 font-display text-2xl font-semibold">Bass</h3>
              </div>
              <span
                class="grid h-10 w-10 place-items-center rounded-full border border-white/30 bg-white/10 backdrop-blur transition group-hover:bg-white group-hover:text-zinc-950"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-up-right"
                  aria-hidden="true"
                >
                  <path d="M7 7h10v10"></path>
                  <path d="M7 17 17 7"></path>
                </svg>
              </span>
            </div>
          </button>
        </div>
      </div>
    </section>
    <section
      id="shop"
      class="border-y border-zinc-200 bg-white py-24 dark:border-white/10 dark:bg-[#0c0c0f] sm:py-28"
    >
      <div class="shell">
        <div
          class="flex flex-col justify-between gap-7 lg:flex-row lg:items-end"
          data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
        >
          <div>
            <p class="section-label">Curated instruments</p>
            <h2 class="section-title">Guitars worth playing.</h2>
            <p class="form-hint mt-3">
              School project catalog: illustrative brands, prices and stock.
            </p>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row">
            <label class="input-shell min-w-[270px]">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-search"
                aria-hidden="true"
              >
                <path d="m21 21-4.34-4.34"></path>
                <circle cx="11" cy="11" r="8"></circle>
              </svg>
              <input
                class="w-full bg-transparent py-3 text-sm outline-none"
                placeholder="Search guitars or brands"
                aria-label="Search guitars or brands"
                value=""
                data-field="search"
              />
            </label>
            <label class="input-shell">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-sliders-horizontal"
                aria-hidden="true"
              >
                <path d="M10 5H3"></path>
                <path d="M12 19H3"></path>
                <path d="M14 3v4"></path>
                <path d="M16 17v4"></path>
                <path d="M21 12h-9"></path>
                <path d="M21 19h-5"></path>
                <path d="M21 5h-7"></path>
                <path d="M8 10v4"></path>
                <path d="M8 12H3"></path>
              </svg>
              <select
                class="appearance-none bg-transparent py-3 pr-4 text-sm outline-none"
                data-field="sort"
                aria-label="Sort instruments"
              >
                <option selected="">Featured</option>
                <option>Price: low</option>
                <option>Price: high</option>
                <option>Rating</option>
              </select>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-chevron-down"
                aria-hidden="true"
              >
                <path d="m6 9 6 6 6-6"></path>
              </svg>
            </label>
          </div>
        </div>
        <div class="mt-8 flex gap-2 overflow-x-auto pb-2">
          <button
            class="filter-chip filter-chip-active"
            data-action="filter"
            data-category="All"
          >
            All
          </button>
          <button
            class="filter-chip"
            data-action="filter"
            data-category="Electric"
          >
            Electric
          </button>
          <button
            class="filter-chip"
            data-action="filter"
            data-category="Acoustic"
          >
            Acoustic
          </button>
          <button
            class="filter-chip"
            data-action="filter"
            data-category="Classical"
          >
            Classical
          </button>
          <button class="filter-chip" data-action="filter" data-category="Bass">
            Bass
          </button>
        </div>
        <div
          class="mt-9 grid gap-x-5 gap-y-12 sm:grid-cols-2 lg:grid-cols-3"
          data-field="products"
        ></div>
        <div
          class="mt-9 rounded-2xl border border-dashed border-zinc-300 py-20 text-center text-sm text-zinc-500 dark:border-white/15"
          hidden=""
          data-field="no-products"
        >
          No guitar matches that search.
        </div>
      </div>
    </section>
    <section class="shell py-24 sm:py-28">
      <div
        class=""
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div
          class="finder-banner relative overflow-hidden rounded-[2rem] bg-zinc-950 px-7 py-16 text-white dark:bg-gradient-to-br dark:from-[#1c1330] dark:via-zinc-950 dark:to-zinc-950 sm:px-12 lg:px-20 lg:py-20"
        >
          <div
            class="absolute -right-28 -top-28 h-80 w-80 rounded-full bg-violet-500/25 blur-[100px]"
          ></div>
          <div
            class="relative grid items-center gap-12 lg:grid-cols-[1fr_.72fr]"
          >
            <div>
              <p
                class="text-[10px] font-semibold uppercase tracking-[.2em] text-acid"
              >
                Guitar finder
              </p>
              <h2
                class="mt-4 font-display text-4xl font-semibold leading-tight tracking-tight sm:text-6xl"
              >
                Four questions.<br />A much better shortlist.
              </h2>
              <p class="mt-5 max-w-xl leading-7 text-zinc-400">
                Choose your budget, experience, preferred style, and guitar
                type. AUDIA will narrow the catalog to practical matches.
              </p>
              <button class="primary-btn mt-8" data-action="finder">
                Start guitar finder
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-compass"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <path
                    d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
                  ></path>
                </svg>
              </button>
            </div>
            <div
              class="finder-profile rounded-3xl border border-white/10 bg-white/[.055] p-6 backdrop-blur"
            >
              <p
                class="text-xs font-semibold uppercase tracking-[.16em] text-zinc-500"
              >
                Example profile
              </p>
              <div class="mt-6 divide-y divide-white/10">
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Budget</span>
                  <span class="font-medium">₱10k – ₱20k</span>
                </div>
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Experience</span>
                  <span class="font-medium">Beginner</span>
                </div>
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Genre</span>
                  <span class="font-medium">Rock</span>
                </div>
                <div class="flex items-center justify-between py-4 text-sm">
                  <span class="text-zinc-500">Type</span>
                  <span class="font-medium">Electric</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    <section id="bundles" class="shell pb-24 sm:pb-28">
      <div
        class="grid overflow-hidden rounded-[2rem] border border-zinc-200 bg-white shadow-sm dark:border-white/10 dark:bg-panel lg:grid-cols-2"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div class="relative min-h-[430px] overflow-hidden">
          <img
            src="{{ url_for('static', filename='images/electric_studio.jpg') }}"
            alt="Electric guitar beside a practice amplifier"
            class="absolute inset-0 h-full w-full object-cover transition duration-1000 hover:scale-105"
          />
          <span
            class="absolute left-6 top-6 rounded-full bg-white px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-zinc-950"
            >Save ₱3,500</span
          >
        </div>
        <div class="flex flex-col justify-center p-8 sm:p-12 lg:p-16">
          <p class="section-label">Complete starter rig</p>
          <h2 class="mt-3 font-display text-4xl font-semibold">
            Everything after the guitar.
          </h2>
          <p class="mt-4 leading-7 text-zinc-500">
            A matched practice amp, padded bag, cable, tuner, strap, picks, and
            a professional setup—ready from day one.
          </p>
          <div class="mt-7 grid grid-cols-2 gap-3 text-sm">
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              15W practice amp
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Padded gig bag
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Clip-on tuner
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Cable + strap
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Assorted picks
            </div>
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-check text-emerald-500"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5"></path>
              </svg>
              Free setup
            </div>
          </div>
          <div class="mt-8 flex items-end gap-3">
            <span class="font-display text-3xl font-semibold">₱19,990</span>
            <span class="pb-1 text-sm text-zinc-500 line-through">₱23,490</span>
          </div>
          <button class="primary-btn mt-7 self-start" data-action="bundle">
            View the bundle
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="17"
              height="17"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-arrow-right"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="m12 5 7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </section>
    <section
      id="track"
      class="border-y border-zinc-200 bg-zinc-100 py-24 dark:border-white/10 dark:bg-white/[.02]"
    >
      <div
        class="shell grid gap-12 lg:grid-cols-[.72fr_1.28fr] lg:items-center"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <div>
          <p class="section-label">Delivery updates</p>
          <h2 class="section-title">Know where it is.</h2>
          <p class="mt-4 leading-7 text-zinc-500">
            Enter your order number to see its current status and estimated
            delivery.
          </p>
          <div class="input-shell mt-7 max-w-md p-1.5 pl-5">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-search"
              aria-hidden="true"
            >
              <path d="m21 21-4.34-4.34"></path>
              <circle cx="11" cy="11" r="8"></circle>
            </svg>
            <input
              placeholder="Enter your order number"
              aria-label="Order number"
              class="min-w-0 flex-1 bg-transparent py-2 text-sm outline-none"
              value=""
              data-field="order"
            />
            <button
              class="rounded-full bg-zinc-950 px-5 py-2.5 text-xs font-bold text-white dark:bg-white dark:text-zinc-950"
              data-action="track"
            >
              Track
            </button>
          </div>
        </div>
        <div class="surface-card p-6 sm:p-8">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-zinc-500">Order</p>
              <p class="mt-1 font-semibold">Example delivery journey</p>
            </div>
            <span
              class="rounded-full bg-blue-100 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-blue-700 dark:bg-blue-400/10 dark:text-blue-300"
              >In transit</span
            >
          </div>
          <div class="mt-10 grid grid-cols-4">
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid dark:text-ink"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-package-check"
                  aria-hidden="true"
                >
                  <path d="M12 22V12"></path>
                  <path d="m16 17 2 2 4-4"></path>
                  <path
                    d="M21 11.127V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.729l7 4a2 2 0 0 0 2 .001l1.32-.753"
                  ></path>
                  <path d="M3.29 7 12 12l8.71-5"></path>
                  <path d="m7.5 4.27 8.997 5.148"></path>
                </svg>
              </div>
              <div
                class="absolute left-1/2 top-5 h-px w-full bg-zinc-950 dark:bg-acid"
              ></div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Processing
              </p>
            </div>
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid dark:text-ink"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-truck"
                  aria-hidden="true"
                >
                  <path
                    d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"
                  ></path>
                  <path d="M15 18H9"></path>
                  <path
                    d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"
                  ></path>
                  <circle cx="17" cy="18" r="2"></circle>
                  <circle cx="7" cy="18" r="2"></circle>
                </svg>
              </div>
              <div
                class="absolute left-1/2 top-5 h-px w-full bg-zinc-950 dark:bg-acid"
              ></div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Shipped
              </p>
            </div>
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-200 bg-white text-zinc-400 dark:border-white/10 dark:bg-panel"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-arrow-right"
                  aria-hidden="true"
                >
                  <path d="M5 12h14"></path>
                  <path d="m12 5 7 7-7 7"></path>
                </svg>
              </div>
              <div
                class="absolute left-1/2 top-5 h-px w-full bg-zinc-200 dark:bg-white/10"
              ></div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Out for delivery
              </p>
            </div>
            <div class="relative text-center">
              <div
                class="relative z-10 mx-auto grid h-10 w-10 place-items-center rounded-full border border-zinc-200 bg-white text-zinc-400 dark:border-white/10 dark:bg-panel"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-check"
                  aria-hidden="true"
                >
                  <path d="M20 6 9 17l-5-5"></path>
                </svg>
              </div>
              <p class="mt-3 text-[9px] text-zinc-500 sm:text-[11px]">
                Delivered
              </p>
            </div>
          </div>
          <div
            class="mt-7 flex justify-between border-t border-zinc-200 pt-5 text-xs dark:border-white/10"
          >
            <span class="text-zinc-500">Estimated arrival</span>
            <span class="font-semibold">Thursday, Sep 10</span>
          </div>
        </div>
      </div>
    </section>
    <div class="shell grid gap-4 py-14 sm:grid-cols-3">
      <div
        class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-5 dark:border-white/10"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-shield-check"
          aria-hidden="true"
        >
          <path
            d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"
          ></path>
          <path d="m9 12 2 2 4-4"></path>
        </svg>
        <div>
          <p class="text-sm font-semibold">Authentic gear</p>
          <p class="mt-1 text-xs text-zinc-500">
            Official products with warranty
          </p>
        </div>
      </div>
      <div
        class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-5 dark:border-white/10"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-volume2 lucide-volume-2"
          aria-hidden="true"
        >
          <path
            d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"
          ></path>
          <path d="M16 9a5 5 0 0 1 0 6"></path>
          <path d="M19.364 18.364a9 9 0 0 0 0-12.728"></path>
        </svg>
        <div>
          <p class="text-sm font-semibold">Hear before buying</p>
          <p class="mt-1 text-xs text-zinc-500">Tone previews on key models</p>
        </div>
      </div>
      <div
        class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-5 dark:border-white/10"
        data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-headphones"
          aria-hidden="true"
        >
          <path
            d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"
          ></path>
        </svg>
        <div>
          <p class="text-sm font-semibold">Player-first support</p>
          <p class="mt-1 text-xs text-zinc-500">Help choosing and setting up</p>
        </div>
      </div>
    </div>
  </main>
  <footer
    class="border-t border-zinc-200 bg-white pt-16 dark:border-white/10 dark:bg-ink"
  >
    <div
      class="shell grid gap-12 pb-14 sm:grid-cols-2 lg:grid-cols-[1.4fr_repeat(3,1fr)]"
    >
      <div>
        <button
          class="audia-mark flex items-center text-left text-lg"
          aria-label="Go to AUDIA home"
          data-action="home"
        >
          <span class="mark-a">A</span>UDI<span class="mark-a">A</span>
        </button>
        <p class="mt-6 max-w-xs text-sm leading-6 text-zinc-500">
          A guitar-only marketplace helping players find, hear, compare, and
          purchase the right instrument.
        </p>
      </div>
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-[.18em]">Shop</h3>
        <div class="mt-5 flex flex-col gap-3">
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Electric"
            >Electric guitars</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Acoustic"
            >Acoustic guitars</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Bass"
            >Bass guitars</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="category"
            data-category="Accessories"
            >Accessories</a
          >
        </div>
      </div>
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-[.18em]">
          Services
        </h3>
        <div class="mt-5 flex flex-col gap-3">
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="finder"
            >Guitar finder</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            >Sound previews</a
          >
          <a
            href="#bundles"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            >Bundles</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="setup"
            >Professional setup</a
          >
        </div>
      </div>
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-[.18em]">
          Support
        </h3>
        <div class="mt-5 flex flex-col gap-3">
          <a
            href="#track"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            >Order tracking</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="delivery"
            >Delivery &amp; returns</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="warranty"
            >Warranty</a
          >
          <a
            href="#shop"
            class="text-sm text-zinc-500 transition hover:text-zinc-950 dark:hover:text-white"
            data-action="support-info"
            data-topic="contact"
            >Contact us</a
          >
        </div>
      </div>
    </div>
    <div class="border-t border-zinc-200 dark:border-white/10">
      <div
        class="shell flex flex-col justify-between gap-3 py-6 text-[11px] text-zinc-500 sm:flex-row"
      >
        <span>© 2026 AUDIA Guitar Marketplace</span>
        <button
          class="hover:text-zinc-950 dark:hover:text-white"
          data-action="admin-login"
        >
          Admin portal
        </button>
      </div>
    </div>
  </footer>
  {% include 'chatbot.html' %}
</div>
{% endblock %} {% block components %}
<!-- Related cards and dialogs live here with the page that uses them. -->

<!-- Product Card -->
<template id="product-card-template">
  <div
    class=""
    data-motion='{"initial":{"opacity":0,"y":28},"animate":{"opacity":1,"y":0},"transition":{"duration":0.7,"delay":0,"ease":[0.22,1,0.36,1]},"viewport":true}'
  >
    <article class="product-card group">
      <div
        class="product-image relative aspect-[4/4.5] overflow-hidden rounded-[1.15rem] bg-zinc-100 dark:bg-zinc-900"
      >
        <img
          loading="lazy"
          decoding="async"
          src="{{ url_for('static', filename='images/electric/Amber_Flame.png') }}"
          alt="ELECTRIC_001"
          class="h-full w-full object-cover transition duration-700 group-hover:scale-[1.04]"
          data-field="image"
        />
        <span
          class="absolute left-3 top-3 rounded-full bg-white/90 px-3 py-1.5 text-[9px] font-bold uppercase tracking-[.12em] text-zinc-950 backdrop-blur"
          data-field="badge"
          >Amber Flame</span
        >
        <button
          class="absolute right-3 top-3 grid h-9 w-9 place-items-center rounded-full bg-white/90 text-zinc-950 shadow-sm"
          aria-label="Save guitar"
          data-action="like"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-heart"
            aria-hidden="true"
          >
            <path
              d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"
            ></path>
          </svg>
        </button>
        <div class="absolute bottom-3 right-3">
          <button
            class="h-10 w-10 inline-flex items-center justify-center rounded-full bg-white text-zinc-950 shadow-lg transition hover:scale-105"
            aria-label="Play guitar tone"
            data-action="sound"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="currentColor"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-play"
              aria-hidden="true"
            >
              <path
                d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"
              ></path>
            </svg>
          </button>
        </div>
      </div>
      <div class="product-details px-1 pb-2 pt-5">
        <div
          class="flex items-center justify-between text-[10px] uppercase tracking-[.14em] text-zinc-500"
        >
          <span data-field="category">AUDIA Demo · Electric</span>
          <span class="flex items-center gap-1 normal-case tracking-normal">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="11"
              height="11"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-star fill-amber-400 text-amber-400"
              aria-hidden="true"
            >
              <path
                d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"
              ></path>
            </svg>
            <span data-field="rating">0 (0)</span>
          </span>
        </div>
        <h3 class="mt-2 font-display text-lg font-semibold" data-field="name">
          ELECTRIC_001
        </h3>
        <p
          class="mt-2 min-h-[40px] text-xs leading-5 text-zinc-500"
          data-field="description"
        >
          Amber Flame single-cut electric with an amber figured finish and two
          covered pickups.
        </p>
        <div class="mt-5 flex items-center justify-between">
          <div>
            <p class="text-lg font-semibold" data-field="price">₱12,990</p>
            <p class="mt-0.5 text-[10px] text-zinc-500" data-field="stock">
              8 available
            </p>
          </div>
          <button
            class="grid h-11 w-11 place-items-center rounded-full bg-zinc-950 text-white transition hover:scale-105 dark:bg-acid dark:text-ink"
            aria-label="Add ELECTRIC_001 to cart"
            data-action="add"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="17"
              height="17"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-plus"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="M12 5v14"></path>
            </svg>
          </button>
        </div>
      </div>
    </article>
  </div>
</template>

<!-- Mobile Nav -->
<template id="mobile-nav-template">
  <nav
    class="shell overflow-hidden border-t border-zinc-200 dark:border-white/10 lg:hidden"
    data-motion='{"initial":{"height":0,"opacity":0},"animate":{"height":"auto","opacity":1},"viewport":false}'
  >
    <div class="flex flex-col gap-1 py-4 text-sm">
      <a
        href="#shop"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Shop</a
      >
      <a
        href="#categories"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Guitars</a
      >
      <a
        href="#bundles"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Bundles</a
      >
      <a
        href="#track"
        class="rounded-xl px-3 py-3 hover:bg-zinc-100 dark:hover:bg-white/5"
        data-action="mobile-link"
        >Track order</a
      >
      <button
        class="flex items-center gap-2 rounded-xl px-3 py-3 text-left"
        data-action="finder"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-compass"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10"></circle>
          <path
            d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
          ></path>
        </svg>
        Guitar finder
      </button>
      <button
        class="flex items-center gap-2 rounded-xl px-3 py-3 text-left"
        data-action="account"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-circle-user-round"
          aria-hidden="true"
        >
          <path d="M17.925 20.056a6 6 0 0 0-11.851.001"></path>
          <circle cx="12" cy="11" r="4"></circle>
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
        Sign in
      </button>
    </div>
  </nav>
</template>

<!-- Bundle Detail -->
<template id="bundle-detail-template">
  <div class="bundle-detail">
    <img class="bundle-image" data-field="image" alt="" />
    <p class="form-hint mt-5" data-field="description"></p>
    <div class="order-total mt-5">
      <span>Complete bundle</span><strong data-field="price"></strong>
    </div>
    <button class="primary-btn w-full" data-field="bundle-add">
      Add bundle to cart
    </button>
  </div>
</template>

<!-- Support Info -->
<template id="support-info-template">
  <div>
    <p class="form-hint" data-field="support-copy"></p>
    <p class="form-hint mt-5">
      Keep your order confirmation for reference. The store can help confirm the
      terms for your instrument.
    </p>
    <a
      class="secondary-btn mt-5"
      data-field="support-email"
      href="mailto:support@audia.ph"
      >Contact the store</a
    >
  </div>
</template>

<!-- Cart -->
<template id="cart-template">
  <div class="fixed inset-0 z-50">
    <button
      class="absolute inset-0 bg-black/55 backdrop-blur-sm"
      aria-label="Close cart"
      data-motion='{"initial":{"opacity":0},"animate":{"opacity":1},"viewport":false}'
      data-action="close-cart"
    ></button>
    <aside
      class="cart-panel absolute right-0 top-0 flex h-full w-full max-w-md flex-col bg-white shadow-2xl dark:bg-[#101014]"
      data-motion='{"initial":{"x":"100%"},"animate":{"x":0},"transition":{"type":"spring","stiffness":300,"damping":32},"viewport":false}'
    >
      <div
        class="flex items-center justify-between border-b border-zinc-200 px-6 py-5 dark:border-white/10"
      >
        <div class="flex items-center gap-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-shopping-bag"
            aria-hidden="true"
          >
            <path d="M16 10a4 4 0 0 1-8 0"></path>
            <path d="M3.103 6.034h17.794"></path>
            <path
              d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"
            ></path>
          </svg>
          <h2 class="font-display text-xl font-semibold">Your cart</h2>
          <span class="text-xs text-zinc-500" data-field="cart-count"
            >1 items</span
          >
        </div>
        <button class="icon-btn" data-action="close-cart">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-x"
            aria-hidden="true"
          >
            <path d="M18 6 6 18"></path>
            <path d="m6 6 12 12"></path>
          </svg>
        </button>
      </div>
      <div class="flex-1 overflow-y-auto p-6" data-field="cart-body"></div>
      <div
        class="border-t border-zinc-200 p-6 dark:border-white/10"
        data-field="cart-footer"
      >
        <div class="flex justify-between">
          <span class="text-sm text-zinc-500">Subtotal</span>
          <span class="font-display text-xl font-semibold" data-field="subtotal"
            >₱12,990</span
          >
        </div>
        <button class="primary-btn mt-5 w-full" data-action="checkout">
          Proceed to checkout
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-shield-check"
            aria-hidden="true"
          >
            <path
              d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"
            ></path>
            <path d="m9 12 2 2 4-4"></path>
          </svg>
        </button>
      </div>
    </aside>
  </div>
</template>

<!-- Cart Badge -->
<template id="cart-badge-template">
  <span
    class="absolute -right-0.5 -top-0.5 grid h-5 w-5 place-items-center rounded-full bg-zinc-950 text-[10px] font-bold text-white dark:bg-acid dark:text-ink"
  ></span>
</template>

<!-- Cart Empty -->
<template id="cart-empty-template">
  <div class="grid h-full place-items-center text-center">
    <div>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="36"
        height="36"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="lucide lucide-shopping-bag mx-auto text-zinc-300 dark:text-zinc-700"
        aria-hidden="true"
      >
        <path d="M16 10a4 4 0 0 1-8 0"></path>
        <path d="M3.103 6.034h17.794"></path>
        <path
          d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z"
        ></path>
      </svg>
      <p class="mt-4 text-sm text-zinc-500">Your cart is empty.</p>
    </div>
  </div>
</template>

<!-- Cart Item -->
<template id="cart-item-template">
  <div class="flex gap-4">
    <img
      src="{{ url_for('static', filename='images/electric/Amber_Flame.png') }}"
      alt=""
      class="h-24 w-20 rounded-xl object-cover"
      data-field="image"
    />
    <div class="flex min-w-0 flex-1 flex-col">
      <p
        class="text-[10px] uppercase tracking-widest text-zinc-500"
        data-field="brand"
      >
        AUDIA Demo
      </p>
      <p class="mt-1 truncate text-sm font-semibold" data-field="name">
        ELECTRIC_001
      </p>
      <div class="mt-auto flex items-center justify-between">
        <span class="text-sm font-semibold" data-field="price">₱12,990</span>
        <div
          class="flex items-center gap-3 rounded-full border border-zinc-200 px-2 py-1 dark:border-white/10"
        >
          <button data-action="decrease">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-minus"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
            </svg>
          </button>
          <span class="text-xs" data-field="quantity">1</span>
          <button data-action="increase">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-plus"
              aria-hidden="true"
            >
              <path d="M5 12h14"></path>
              <path d="M12 5v14"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<!-- Cart Items -->
<template id="cart-items-template">
  <div class="space-y-5"></div>
</template>

<!-- Checkout -->
<template id="checkout-template">
  <form method="post" class="stack-form" data-form="checkout">
    <p class="form-hint">
      Your instruments are reserved when you place your order. Pay with cash on
      delivery.
    </p>
    <label
      >Delivery address<textarea
        name="address"
        required
        minlength="10"
        maxlength="500"
        autocomplete="street-address"
        placeholder="House number, street, barangay, city, province, postal code"
      ></textarea></label
    ><label
      >Phone number<input
        name="phone"
        type="tel"
        required
        minlength="7"
        maxlength="30"
        autocomplete="tel"
    /></label>
    <div class="order-total">
      <span>Order total</span><strong data-field="checkout-total"></strong>
    </div>
    <p class="form-hint">
      Payment: cash on delivery. No online payment is collected.
    </p>
    <p class="form-error" role="alert" data-field="form-error" hidden></p>
    <button type="submit" class="primary-btn">Place order</button>
  </form>
</template>

<!-- Finder -->
<template id="finder-template">
  <div class="fixed inset-0 z-[60] grid place-items-center p-4">
    <button
      class="absolute inset-0 bg-black/65 backdrop-blur-md"
      aria-label="Close finder"
      data-motion='{"initial":{"opacity":0},"animate":{"opacity":1},"viewport":false}'
      data-action="close-finder"
    ></button>
    <div
      class="finder-modal relative w-full max-w-2xl overflow-hidden rounded-[2rem] bg-white shadow-2xl dark:bg-panel"
      data-motion='{"initial":{"opacity":0,"y":28,"scale":0.98},"animate":{"opacity":1,"y":0,"scale":1},"viewport":false}'
    >
      <div
        class="flex items-center justify-between border-b border-zinc-200 p-6 dark:border-white/10"
      >
        <div class="flex items-center gap-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-compass"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <path
              d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
            ></path>
          </svg>
          <div>
            <p class="font-display font-semibold">AUDIA Guitar Finder</p>
            <p class="text-[10px] text-zinc-500">Four quick questions</p>
          </div>
        </div>
        <button class="icon-btn" data-action="close-finder">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-x"
            aria-hidden="true"
          >
            <path d="M18 6 6 18"></path>
            <path d="m6 6 12 12"></path>
          </svg>
        </button>
      </div>
      <div class="p-7 sm:p-10" data-field="finder-body">
        <div class="mb-8 flex gap-2" data-field="progress">
          <span class="h-1 flex-1 rounded-full bg-zinc-950 dark:bg-acid"></span>
          <span
            class="h-1 flex-1 rounded-full bg-zinc-200 dark:bg-white/10"
          ></span>
          <span
            class="h-1 flex-1 rounded-full bg-zinc-200 dark:bg-white/10"
          ></span>
          <span
            class="h-1 flex-1 rounded-full bg-zinc-200 dark:bg-white/10"
          ></span>
        </div>
        <p class="section-label" data-field="question-number">
          Question 1 of 4
        </p>
        <h2
          class="mt-3 font-display text-3xl font-semibold"
          data-field="question-title"
        >
          What is your budget?
        </h2>
        <div class="mt-10" data-field="budget">
          <div
            class="mb-7 text-center font-display text-4xl font-semibold"
            data-field="budget-value"
          >
            ₱20,000
          </div>
          <input
            type="range"
            min="8000"
            max="60000"
            step="1000"
            class="range-acid w-full"
            value="20000"
            data-field="budget-input"
          />
          <div class="mt-3 flex justify-between text-xs text-zinc-500">
            <span>₱8,000</span>
            <span>₱60,000</span>
          </div>
        </div>
        <div
          class="mt-9 grid gap-3 sm:grid-cols-2"
          data-field="options"
          hidden=""
        ></div>
        <button class="primary-btn mt-10 w-full" data-action="finder-next">
          Continue
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="lucide lucide-arrow-right"
            aria-hidden="true"
          >
            <path d="M5 12h14"></path>
            <path d="m12 5 7 7-7 7"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<!-- Finder Results -->
<template id="finder-results-template">
  <div class="p-7 sm:p-10" data-field="finder-results">
    <p class="section-label">Recommended for you</p>
    <h2 class="mt-3 font-display text-3xl font-semibold">
      Your closest matches.
    </h2>
    <div class="mt-7 space-y-3" data-field="matches"></div>
    <button class="secondary-btn mt-6 w-full" data-action="finder-restart">
      Start again
    </button>
  </div>
</template>

<!-- Finder Match -->
<template id="finder-match-template">
  <div
    class="flex items-center gap-4 rounded-2xl border border-zinc-200 p-3 dark:border-white/10"
  >
    <div class="relative">
      <img
        src="{{ url_for('static', filename='images/electric/Amber_Flame.png') }}"
        alt=""
        class="h-20 w-16 rounded-xl object-cover"
        data-field="image"
      />
      <span
        class="absolute -left-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-zinc-950 text-[10px] font-bold text-white dark:bg-acid dark:text-ink"
        data-field="rank"
        >1</span
      >
    </div>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-semibold" data-field="name">
        ELECTRIC_001
      </p>
      <p class="mt-1 text-xs text-zinc-500" data-field="category">
        Electric · Beginner
      </p>
      <p class="mt-2 text-sm font-semibold" data-field="price">₱12,990</p>
    </div>
    <button
      class="grid h-10 w-10 place-items-center rounded-full bg-zinc-950 text-white dark:bg-acid dark:text-ink"
      data-action="add-match"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="lucide lucide-plus"
        aria-hidden="true"
      >
        <path d="M5 12h14"></path>
        <path d="M12 5v14"></path>
      </svg>
    </button>
  </div>
</template>

<!-- Finder Option -->
<template id="finder-option-template">
  <button
    class="rounded-2xl border p-5 text-left text-sm transition border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid/10 dark:text-acid"
    data-action="finder-option"
  ></button>
</template>

<!-- Check -->
<template id="check-template">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="15"
    height="15"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide lucide-check float-right"
    aria-hidden="true"
  >
    <path d="M20 6 9 17l-5-5"></path>
  </svg>
</template>

{% endblock %}
```

## templates/account.html

```html
{% extends "base.html" %} {% block content %}
<div class="account-page min-h-screen">
  <header class="account-header shell">
    <button class="audia-mark" data-action="store">AUDIA</button>
    <div class="flex items-center gap-3">
      <button class="secondary-btn" data-action="store">Back to store</button
      ><button
        class="icon-btn"
        data-action="theme"
        aria-label="Change theme"
      ></button
      ><button class="secondary-btn" data-action="logout">Sign out</button>
    </div>
  </header>
  {% include 'practice/feature_links.html' %}
  <main class="shell account-main">
    <p class="section-label">Your AUDIA</p>
    <h1
      class="font-display text-4xl font-semibold mt-3"
      data-field="greeting"
    ></h1>
    <p class="mt-3 text-sm text-zinc-500">
      Your instruments, orders, and account details, together.
    </p>
    <div class="account-grid">
      <section class="surface-card account-section">
        <h2 class="font-display text-xl font-semibold">
          Profile &amp; delivery
        </h2>
        <form method="post" class="stack-form mt-6" data-form="profile">
          <label
            >Full name<input
              name="name"
              required
              minlength="2"
              maxlength="100"
              autocomplete="name" /></label
          ><label
            >Email address<input name="email" type="email" disabled /></label
          ><label
            >Phone number<input
              name="phone"
              maxlength="30"
              autocomplete="tel" /></label
          ><label
            >Delivery address<textarea
              name="address"
              maxlength="500"
              autocomplete="street-address"
            ></textarea>
          </label>
          <p class="form-error" role="alert" data-field="form-error" hidden></p>
          <button class="primary-btn" type="submit">Save profile</button>
        </form>
      </section>
      <section class="surface-card account-section">
        <h2 class="font-display text-xl font-semibold">Account security</h2>
        <p class="form-hint mt-3">
          Changing your password signs out your other sessions.
        </p>
        <form method="post" class="stack-form mt-6" data-form="password">
          <label
            >Current password<input
              name="current_password"
              type="password"
              required
              autocomplete="current-password"
              maxlength="128" /></label
          ><label
            >New password<input
              name="password"
              type="password"
              required
              minlength="10"
              maxlength="128"
              autocomplete="new-password" /></label
          ><label
            >Confirm new password<input
              name="confirm"
              type="password"
              required
              minlength="10"
              maxlength="128"
              autocomplete="new-password"
          /></label>
          <p class="form-error" role="alert" data-field="form-error" hidden></p>
          <button class="primary-btn" type="submit">Update password</button>
        </form>
      </section>
    </div>
    <section class="surface-card account-section mt-7">
      <div class="flex items-center justify-between gap-4">
        <h2 class="font-display text-xl font-semibold">Your orders</h2>
        <button class="secondary-btn" data-action="refresh-orders">
          Refresh
        </button>
      </div>
      <div class="account-orders" data-field="orders">
        <p class="empty-state">Loading your orders…</p>
      </div>
    </section>
    <section class="surface-card account-section mt-7">
      <h2 class="font-display text-xl font-semibold">Saved instruments</h2>
      <div class="saved-grid" data-field="saved">
        <p class="empty-state">Loading your saved instruments…</p>
      </div>
      <div class="finder-profile-summary">
        <p class="form-hint" data-field="finder-profile"></p>
        <button class="secondary-btn" data-action="find-guitar">
          Open Guitar Finder
        </button>
      </div>
    </section>
  </main>
</div>
{% endblock %} {% block components %}
<!-- Related cards and dialogs live here with the page that uses them. -->

<!-- Order Card -->
<template id="order-card-template">
  <article class="account-order">
    <div>
      <h3 class="font-semibold text-sm" data-field="id"></h3>
      <p class="form-hint" data-field="date"></p>
      <p class="text-xs mt-2" data-field="product"></p>
    </div>
    <div class="account-order-actions">
      <span class="order-status" data-field="status"></span
      ><strong data-field="amount"></strong
      ><button class="secondary-btn" data-action="view-order">
        View order
      </button>
    </div>
  </article>
</template>

<!-- Saved Item -->
<template id="saved-item-template">
  <article class="saved-item">
    <img data-field="image" alt="" />
    <div>
      <h3 class="font-semibold text-sm" data-field="name"></h3>
      <p class="form-hint" data-field="price"></p>
      <div class="form-actions">
        <button class="secondary-btn" data-action="saved-shop">
          Shop instrument</button
        ><button class="danger-btn" data-action="unsave">Remove</button>
      </div>
    </div>
  </article>
</template>
{% endblock %}
```

## modules/tuner.py

```python
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
        stylesheet="tuner", practice_area="tuner",
    )
```

## modules/lessons.py

```python
"""Read-only beginner lesson pages using static content and Jinja diagrams."""
from flask import Blueprint, abort, g, redirect, render_template, url_for

from .lessons_content import CHORDS, STRUMMING_PATTERNS

lessons = Blueprint("lessons", __name__, url_prefix="/lessons")


@lessons.before_request
def require_signed_in_player():
    if not g.user:
        return redirect(url_for("login_page"))


def lesson_page(template, title, **content):
    return render_template(
        "lessons/" + template, title=title, page_name="lessons",
        stylesheet="lessons", practice_area="lessons", **content,
    )


@lessons.get("")
def index():
    return lesson_page("index.html", "Learn Guitar")


@lessons.get("/getting-started")
def getting_started():
    return lesson_page("getting_started.html", "Getting Started")


@lessons.get("/chords")
def chords():
    return lesson_page("chords.html", "Basic Chords", chords=CHORDS)


@lessons.get("/chords/<slug>")
def chord_detail(slug):
    chord = CHORDS.get(slug)
    if chord is None:
        abort(404)
    return lesson_page("chord_detail.html", chord["name"], chord=chord, slug=slug)


@lessons.get("/strumming")
def strumming():
    return lesson_page("strumming.html", "Strumming", patterns=STRUMMING_PATTERNS)
```

## modules/lessons_content.py

```python
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
```

## templates/practice/base.html

```html
{% extends "base.html" %}
{% block content %}
<div class="practice-page">
  <header class="practice-header shell">
    <a class="audia-mark" href="{{ url_for('index') }}" aria-label="AUDIA home"><span class="mark-a">A</span>UDI<span class="mark-a">A</span></a>
    <nav class="practice-nav" aria-label="Main navigation">
      <a href="{{ url_for('shop') }}">Store</a>
      <a href="{{ url_for('shop') }}#shop">Products</a>
      <a href="{{ url_for('tuner.index') }}" {% if practice_area == 'tuner' %}aria-current="page"{% endif %}>Guitar Tuner</a>
      <a href="{{ url_for('lessons.index') }}" {% if practice_area == 'lessons' %}aria-current="page"{% endif %}>Guitar Lessons</a>
      <a href="{{ url_for('account_page') }}">Account</a>
    </nav>
    <button class="icon-btn" data-action="theme" aria-label="Change theme"></button>
  </header>
  <main class="shell practice-main">
    {% block practice_content %}{% endblock %}
  </main>
  {% include 'chatbot.html' %}
</div>
{% endblock %}
```

## templates/practice/feature_links.html

```html
<nav class="shell flex flex-wrap items-center gap-3 py-3 text-sm border-b border-zinc-200 dark:border-white/10" aria-label="Guitar practice">
  <a class="flex items-center gap-2" href="{{ url_for('tuner.index') }}">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 10v4m4-8v12m4-15v18m4-15v12m4-8v4"/></svg>
    Guitar Tuner
  </a>
  <a class="flex items-center gap-2" href="{{ url_for('lessons.index') }}">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M12 5C9 3 5 3 2 4v15c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 1Zm0 0v15"/></svg>
    Guitar Lessons
  </a>
</nav>
```

## templates/tuner/tuner.html

```html
{% extends "practice/base.html" %}
{% block practice_content %}
<div class="practice-heading">
  <p class="section-label">AUDIA practice studio</p>
  <h1 class="section-title">Guitar Tuner</h1>
  <p>Six strings. One clear sound. Pluck a single open string and let it ring.</p>
</div>
<div class="tuner-layout">
  <section class="surface-card tuner-container" aria-label="Live guitar tuner">
    <p id="tuner-microphone" class="tuner-microphone" role="status">Microphone inactive</p>
    <div class="tuner-readout" aria-label="Detected pitch">
      <p class="tuner-note"><span id="tuner-note">—</span><span id="tuner-octave" class="tuner-octave"></span></p>
      <p id="tuner-frequency" class="tuner-frequency">— Hz</p>
      <p id="tuner-cents" class="tuner-cents">— cents</p>
    </div>
    <p id="tuner-status" class="tuner-status" role="status">Play a string</p>
    <div id="tuner-meter" class="tuner-meter" role="meter" aria-label="Tuning deviation in cents" aria-valuemin="-50" aria-valuemax="50" aria-valuenow="0" aria-valuetext="No reliable pitch">
      <div class="tuner-meter-track"><span class="tuner-meter-center" aria-hidden="true"></span><span id="tuner-indicator" class="tuner-indicator" hidden></span></div>
      <div class="tuner-meter-labels" aria-hidden="true"><span>Flat −50</span><span>In tune</span><span>+50 Sharp</span></div>
    </div>
    <div class="practice-actions tuner-controls">
      <button id="tuner-start" type="button" class="primary-btn">Start Tuner</button>
      <button id="tuner-stop" type="button" class="secondary-btn" disabled>Stop Tuner</button>
    </div>
    <p id="tuner-error" class="form-error" role="alert" hidden></p>
    <p class="tuner-privacy">Audio is processed locally in your browser and is not recorded.</p>
  </section>
  <aside class="tuner-guide">
    <section class="surface-card practice-card">
      <p class="section-label">Standard tuning · A4 = 440 Hz</p>
      <h2>Meet your six strings</h2>
      <p>From the thickest string to the thinnest. The matching string lights up automatically.</p>
      <ol class="tuner-strings" reversed>
        {% for note, frequency in [('E2', '82.41'), ('A2', '110.00'), ('D3', '146.83'), ('G3', '196.00'), ('B3', '246.94'), ('E4', '329.63')] %}
        <li data-tuning-note="{{ note }}"><span>String {{ 7 - loop.index }}</span><strong>{{ note }}</strong><span>{{ frequency }} Hz</span></li>
        {% endfor %}
      </ol>
    </section>
    <section class="practice-card tuner-tips">
      <h2>A little preparation</h2>
      <p>Use a quiet room and keep your microphone near the guitar. Mute the other strings and pluck gently. Adjust the tuning peg a little at a time, then pluck again.</p>
      <p>Within ±5 cents is in tune. The note follows the nearest musical pitch; check the string reference to make sure you reach the intended open string.</p>
      <a class="practice-link" href="{{ url_for('lessons.getting_started') }}#tuning">Learn standard tuning →</a>
    </section>
  </aside>
</div>
{% endblock %}
```

## templates/lessons/index.html

```html
{% extends "practice/base.html" %}
{% block practice_content %}
<div class="practice-heading">
  <p class="section-label">AUDIA practice studio</p>
  <h1 class="section-title">Learn Guitar</h1>
  <p>Start small, build good habits, and make your first chords ring.</p>
</div>
<div class="lesson-hero surface-card">
  <div class="practice-card">
    <p class="section-label">Your first practice</p>
    <h2>Pick up your guitar.<br>Find your rhythm.</h2>
    <p>A few focused minutes each day can help you get comfortable. Learn the strings, tune up, try a chord, then add a steady strum.</p>
    <div class="practice-actions"><a class="primary-btn" href="{{ url_for('lessons.getting_started') }}">Start learning</a><a class="secondary-btn" href="{{ url_for('tuner.index') }}">Tune your guitar</a></div>
  </div>
  <img src="{{ url_for('static', filename='images/acoustic_studio.jpg') }}" alt="Acoustic guitar ready for practice" width="640" height="480">
</div>
<div class="lesson-grid">
  <a class="surface-card practice-card lesson-card" href="{{ url_for('lessons.getting_started') }}"><span class="section-label">01 · Getting Started</span><h2>Get to know your guitar</h2><p>Parts, posture, pick grip, string names, and standard tuning.</p><span class="practice-link">Explore the basics →</span></a>
  <a class="surface-card practice-card lesson-card" href="{{ url_for('lessons.chords') }}"><span class="section-label">02 · Basic Chords</span><h2>Your first eight chords</h2><p>Clear diagrams and finger placements for C, G, D, A, E, Am, Em, and Dm.</p><span class="practice-link">Open the chord library →</span></a>
  <a class="surface-card practice-card lesson-card" href="{{ url_for('lessons.strumming') }}"><span class="section-label">03 · Strumming</span><h2>Bring chords to life</h2><p>Downstrokes, upstrokes, counting beats, and three beginner patterns.</p><span class="practice-link">Find your rhythm →</span></a>
</div>
{% endblock %}
```

## templates/lessons/getting_started.html

```html
{% extends "practice/base.html" %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.index') }}">← All lessons</a>
<div class="practice-heading"><p class="section-label">01 · Getting Started</p><h1 class="section-title">Get to know your guitar</h1><p>Get comfortable before you start playing. These instructions describe right-handed playing; mirror the hands for left-handed playing.</p></div>
<nav class="lesson-topics" aria-label="Getting started topics"><a href="#parts">Guitar parts</a><a href="#holding">Holding your guitar</a><a href="#pick">Holding a pick</a><a href="#strings">String names</a><a href="#tuning">Standard tuning</a></nav>
<div class="lesson-basics-grid">
  <section id="parts" class="surface-card practice-card"><h2>Parts of a guitar</h2><dl class="lesson-definitions"><dt>Headstock &amp; tuning pegs</dt><dd>The headstock holds the pegs. Turn them to change string tension and pitch.</dd><dt>Nut, neck &amp; frets</dt><dd>The nut guides strings into the neck. Press just behind a metal fret to shorten a string and change its note.</dd><dt>Body &amp; sound</dt><dd>An acoustic guitar uses a sound hole and hollow body. An electric guitar uses pickups to send sound to an amplifier.</dd><dt>Bridge &amp; saddle</dt><dd>These support the strings at the body end and help transfer their vibrations.</dd></dl></section>
  <section id="holding" class="surface-card practice-card"><h2>How to hold a guitar</h2><ol class="lesson-steps"><li>Sit upright with both feet supported and your shoulders relaxed.</li><li>Rest the guitar body on your right thigh. Classical players may prefer the left thigh with a foot support.</li><li>Keep the neck angled slightly upward. Rest your right forearm lightly over the body.</li><li>Place your left thumb behind the neck and curve your fingers. Avoid squeezing or bending your wrist sharply.</li></ol><p>A strap can support the guitar while standing. Adjust it so both hands can move comfortably.</p></section>
  <section id="pick" class="surface-card practice-card"><h2>How to hold a guitar pick</h2><ol class="lesson-steps"><li>Curl your index finger gently.</li><li>Lay the pick on the side of the index finger, with the point facing the strings.</li><li>Place your thumb over it, leaving a small part of the point exposed.</li><li>Hold it securely, relax your wrist, and let the pick glide over the strings.</li></ol><p>A light or medium pick is a comfortable starting point. Use small motions instead of gripping tightly.</p></section>
  <section id="strings" class="surface-card practice-card"><h2>Guitar string names</h2><p>String 6 is the thickest and lowest. String 1 is the thinnest and highest.</p><ol class="lesson-string-list" reversed><li>6 · E — low E</li><li>5 · A</li><li>4 · D</li><li>3 · G</li><li>2 · B</li><li>1 · E — high E</li></ol><p>Remember: <strong>E A D G B E</strong>, from thick to thin.</p></section>
  <section id="tuning" class="surface-card practice-card lesson-wide"><h2>Standard guitar tuning</h2><p>The open-string pitches are E2 (82.41 Hz), A2 (110.00 Hz), D3 (146.83 Hz), G3 (196.00 Hz), B3 (246.94 Hz), and E4 (329.63 Hz). The octave number distinguishes low E from high E.</p><ol class="lesson-steps"><li>Open the tuner and press Start Tuner. Allow microphone access.</li><li>Mute the other strings and pluck one open string. Match its note and octave to the reference.</li><li>If the reading is flat, carefully increase tension. If sharp, reduce tension. Make small adjustments; avoid overtightening.</li><li>Repeat for all six strings and check them once more.</li></ol><a class="primary-btn" href="{{ url_for('tuner.index') }}">Open Guitar Tuner</a></section>
</div>
<div class="practice-actions"><a class="secondary-btn" href="{{ url_for('lessons.chords') }}">Next: basic chords →</a></div>
{% endblock %}
```

## templates/lessons/chords.html

```html
{% extends "practice/base.html" %}
{% from "lessons/_chord_diagram.html" import chord_diagram %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.index') }}">← All lessons</a>
<div class="practice-heading"><p class="section-label">02 · Basic Chords</p><h1 class="section-title">Your first eight chords</h1><p>Choose a chord to see finger placements and playing tips. Try E minor first if you are just starting.</p></div>
<p class="chord-legend">O = open string · X = muted string · numbered circle = finger. 1 index, 2 middle, 3 ring, 4 little. Read from low E on the left to high E on the right.</p>
<div class="chord-grid">
  {% for slug, chord in chords.items() %}
  <a class="surface-card practice-card chord-card" href="{{ url_for('lessons.chord_detail', slug=slug) }}"><h2>{{ chord.name }} <span>{{ chord.symbol }}</span></h2>{{ chord_diagram(chord, slug) }}<span class="practice-link">Learn this chord →</span></a>
  {% endfor %}
</div>
{% endblock %}
```

## templates/lessons/chord_detail.html

```html
{% extends "practice/base.html" %}
{% from "lessons/_chord_diagram.html" import chord_diagram %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.chords') }}">← Chord library</a>
<div class="practice-heading"><p class="section-label">02 · Basic Chords</p><h1 class="section-title">{{ chord.name }}</h1><p>Make each string ring clearly before trying a full strum.</p></div>
<div class="chord-detail-layout">
  <section class="surface-card practice-card chord-detail-diagram" aria-label="Chord shape"><h2>{{ chord.symbol }}</h2>{{ chord_diagram(chord, slug) }}<p class="chord-legend">O = open · X = muted<br>1 index · 2 middle · 3 ring · 4 little</p></section>
  <section class="surface-card practice-card"><h2>Finger placement</h2><ul class="lesson-steps">{% for placement in chord.placement %}<li>{{ placement }}</li>{% endfor %}</ul><h3>Strings to play</h3><p>{{ chord.played }}</p><h3>Strings to leave out</h3><p>{{ chord.muted }}</p><h3>Make it sound clear</h3><p>{{ chord.tip }}</p><p>Place your fingers just behind the frets. Pick each played string separately, adjust any buzzing notes, and then strum slowly.</p></section>
</div>
<div class="practice-actions"><a class="secondary-btn" href="{{ url_for('lessons.chords') }}">Try another chord</a><a class="primary-btn" href="{{ url_for('lessons.strumming') }}">Add a strumming pattern →</a></div>
{% endblock %}
```

## templates/lessons/_chord_diagram.html

```html
{% macro chord_diagram(chord, diagram_id) %}
<svg class="chord-diagram" viewBox="0 0 220 245" role="img" aria-labelledby="{{ diagram_id }}-title {{ diagram_id }}-description">
  <title id="{{ diagram_id }}-title">{{ chord.name }} chord diagram</title>
  <desc id="{{ diagram_id }}-description">Strings run from low E on the left to high E on the right. O means open, X means muted. {{ chord.placement|join(' ') }} {{ chord.played }} {{ chord.muted }}</desc>
  {% for fret in range(5) %}<line class="chord-fret{% if fret == 0 %} chord-nut{% endif %}" x1="35" y1="{{ 55 + fret * 36 }}" x2="185" y2="{{ 55 + fret * 36 }}"/>{% endfor %}
  {% for label in ['E', 'A', 'D', 'G', 'B', 'e'] %}
    {% set position = loop.index0 %}{% set x = 35 + position * 30 %}{% set fret = chord.frets[position] %}
    <line class="chord-string" x1="{{ x }}" y1="55" x2="{{ x }}" y2="199"/>
    <text class="chord-string-label" x="{{ x }}" y="226" text-anchor="middle">{{ label }}</text>
    {% if fret is none or fret == 0 %}<text class="chord-open-muted" x="{{ x }}" y="35" text-anchor="middle">{{ 'X' if fret is none else 'O' }}</text>
    {% else %}<circle class="chord-finger" cx="{{ x }}" cy="{{ 55 + (fret - 0.5) * 36 }}" r="11"/><text class="chord-finger-number" x="{{ x }}" y="{{ 59 + (fret - 0.5) * 36 }}" text-anchor="middle">{{ chord.fingers[position] }}</text>{% endif %}
  {% endfor %}
  {% for fret in range(1, 5) %}<text class="chord-fret-label" x="14" y="{{ 59 + (fret - 0.5) * 36 }}" text-anchor="middle">{{ fret }}</text>{% endfor %}
</svg>
{% endmacro %}
```

## templates/lessons/strumming.html

```html
{% extends "practice/base.html" %}
{% block practice_content %}
<a class="practice-link" href="{{ url_for('lessons.index') }}">← All lessons</a>
<div class="practice-heading"><p class="section-label">03 · Strumming</p><h1 class="section-title">Find your rhythm</h1><p>Choose a comfortable chord, such as E minor. Count out loud and keep your hand moving evenly.</p></div>
<section class="surface-card practice-card"><h2>Learn the strokes</h2><p><strong>D ↓ = Downstroke:</strong> move from thick strings toward thin strings. <strong>U ↑ = Upstroke:</strong> move back toward the thick strings, brushing lightly.</p><p>In 4/4 time, count <strong>1 &amp; 2 &amp; 3 &amp; 4 &amp;</strong>. Each number is a beat (a quarter note). The &amp; halfway between beats makes eighth notes. A dash means pass over the strings without striking them.</p></section>
<div class="strumming-lessons">
{% for pattern in patterns %}
<section class="surface-card practice-card"><h2>{{ pattern.name }}</h2><div class="strumming-pattern" role="group" aria-label="{{ pattern.name }} with beat counts">
{% for stroke in pattern.strokes %}<div class="strumming-beat"><span class="strumming-stroke{% if stroke == '–' %} strumming-rest{% endif %}">{{ stroke }}<span aria-hidden="true">{{ '↓' if stroke == 'D' else '↑' if stroke == 'U' else '·' }}</span></span><span class="strumming-count">{{ (loop.index0 // 2) + 1 if loop.index0 % 2 == 0 else '&' }}</span></div>{% endfor %}
</div><p>{{ pattern.description }}</p></section>
{% endfor %}
</div>
<section class="practice-card"><h2>Keep it comfortable</h2><ul class="lesson-steps"><li>Hold your pick with a relaxed grip and keep your wrist loose.</li><li>Start slowly, around 60 beats per minute on a metronome. Play one downstroke per click first.</li><li>Keep the same motion through silent gaps. Listen for even spacing between strokes.</li><li>Practice on one chord before changing chords. Increase the tempo only when the pattern feels steady.</li></ul><div class="practice-actions"><a class="secondary-btn" href="{{ url_for('lessons.chords') }}">Choose a practice chord</a><a class="practice-link" href="{{ url_for('tuner.index') }}">Tune up before practice →</a></div></section>
{% endblock %}
```

## assets/css/practice.css

```css
/* Shared only by the new tuner and lessons pages. Reuses AUDIA's theme. */
.practice-page {
  min-height: 100vh;
  background: var(--page);
  color: var(--text);
}
.practice-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  padding-block: 20px;
  border-bottom: 1px solid var(--line);
}
.practice-header .audia-mark { font-size: 22px; }
.practice-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
  margin-left: auto;
  font-size: 13px;
  color: var(--muted);
}
.practice-nav a { padding-block: 6px; }
.practice-nav a:hover, .practice-nav a[aria-current] { color: var(--accent); }
.practice-main { max-width: 1200px; padding-block: 40px 80px; }
.practice-heading { margin-bottom: 32px; }
.practice-heading > p:last-child {
  max-width: 660px;
  margin-top: 16px;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.8;
}
.practice-card { padding: 28px; min-width: 0; }
.practice-card h2 {
  font-family: "Space Grotesk", Inter, ui-sans-serif, system-ui;
  font-size: 22px;
  font-weight: 600;
  line-height: 1.4;
}
.practice-card h3 { font-size: 15px; font-weight: 600; margin-top: 24px; }
.practice-card p:not(.section-label) { margin-top: 12px; color: var(--muted); font-size: 14px; line-height: 1.8; }
.practice-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 24px; }
.practice-link { color: var(--accent); font-size: 14px; font-weight: 600; }
.practice-link:hover { text-decoration: underline; }
@media (max-width: 767px) {
  .practice-header { gap: 12px; }
  .practice-header > .icon-btn { margin-left: auto; }
  .practice-nav { order: 3; width: 100%; margin-left: 0; gap: 8px 20px; }
  .practice-main { padding-block: 28px 64px; }
  .practice-card { padding: 20px; }
}
```

## assets/css/tuner.css

```css
@import url("./practice.css");

.tuner-layout { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); gap: 24px; }
.tuner-container { padding: 32px; text-align: center; min-width: 0; align-self: start; }
.tuner-microphone { color: var(--muted); font-size: 13px; min-height: 24px; }
.tuner-note { font-family: "Space Grotesk", Inter, system-ui; font-size: clamp(72px, 12vw, 116px); font-weight: 600; line-height: 1.2; margin-top: 24px; }
.tuner-octave { font-size: 0.45em; color: var(--muted); margin-left: 4px; }
.tuner-frequency { color: var(--muted); font-size: 18px; font-variant-numeric: tabular-nums; }
.tuner-cents { margin-top: 8px; color: var(--accent); font-size: 16px; font-variant-numeric: tabular-nums; }
.tuner-status { font-weight: 600; margin-top: 24px; color: var(--muted); }
.tuner-container[data-tuning="in-tune"] .tuner-status { color: var(--mint); }
.tuner-container[data-tuning="flat"] .tuner-status,
.tuner-container[data-tuning="sharp"] .tuner-status { color: var(--accent); }
.tuner-meter { margin-top: 24px; }
.tuner-meter-track { position: relative; height: 36px; margin-inline: 8px; border-bottom: 2px solid var(--line); background: repeating-linear-gradient(90deg, var(--line) 0 1px, transparent 1px 10%); }
.tuner-meter-center { position: absolute; left: 45%; width: 10%; height: 100%; background: var(--mint); opacity: 0.18; border-radius: 4px; }
.tuner-meter-center::after { content: ""; position: absolute; left: 50%; height: 100%; width: 2px; background: var(--text); }
.tuner-indicator { position: absolute; left: 50%; top: -5px; width: 4px; height: 45px; background: var(--accent); border-radius: 4px; transform: translateX(-50%); transition: left 100ms linear; }
.tuner-container[data-tuning="in-tune"] .tuner-indicator { background: var(--mint); }
.tuner-meter-labels { display: flex; justify-content: space-between; gap: 4px; margin-top: 12px; color: var(--muted); font-size: 11px; }
.tuner-controls { justify-content: center; margin-top: 32px; }
.tuner-privacy { margin-top: 24px; color: var(--muted); font-size: 12px; line-height: 1.7; }
.tuner-container .form-error { margin-top: 20px; }
.tuner-strings { list-style: none; margin-top: 24px; }
.tuner-strings li { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 12px; border-bottom: 1px solid var(--line); padding: 12px 8px; font-size: 12px; color: var(--muted); }
.tuner-strings li > :last-child { text-align: right; font-variant-numeric: tabular-nums; }
.tuner-strings strong { color: var(--text); font-size: 20px; }
.tuner-strings li[data-active] { background: var(--soft); border-radius: 8px; }
.tuner-strings li[data-active] strong { color: var(--accent); }
.tuner-tips .practice-link { display: inline-block; margin-top: 16px; }
@media (max-width: 767px) {
  .tuner-layout { grid-template-columns: minmax(0, 1fr); }
  .tuner-container { padding: 24px 20px; }
}
@media (prefers-reduced-motion: reduce) { .tuner-indicator { transition: none; } }
```

## assets/css/lessons.css

```css
@import url("./practice.css");

.lesson-hero { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); overflow: hidden; margin-bottom: 24px; }
.lesson-hero .practice-card { align-self: center; padding: 36px; }
.lesson-hero h2 { margin-top: 16px; font-size: clamp(26px, 4vw, 40px); letter-spacing: -0.04em; }
.lesson-hero img { height: 100%; min-height: 320px; max-height: 430px; width: 100%; object-fit: cover; }
.lesson-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; }
.lesson-card { display: flex; flex-direction: column; gap: 12px; }
.lesson-card p { margin-top: 0; }
.lesson-card .practice-link { margin-top: auto; padding-top: 12px; }
.lesson-card:hover, .chord-card:hover { border-color: var(--accent); }
.lesson-topics { display: flex; flex-wrap: wrap; gap: 12px 20px; margin-bottom: 24px; color: var(--accent); font-size: 13px; }
.lesson-basics-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; }
.lesson-wide { grid-column: 1 / -1; }
.lesson-steps { margin-block: 16px; padding-left: 22px; font-size: 14px; line-height: 1.8; color: var(--muted); }
ol.lesson-steps { list-style: decimal; }
ul.lesson-steps { list-style: disc; }
.lesson-steps li + li { margin-top: 8px; }
.lesson-definitions dt { font-size: 14px; font-weight: 600; margin-top: 16px; }
.lesson-definitions dd { color: var(--muted); font-size: 14px; line-height: 1.8; margin-top: 4px; }
.lesson-string-list { margin-top: 16px; font-size: 14px; line-height: 2; }
.chord-legend { color: var(--muted); font-size: 12px; line-height: 1.8; margin-bottom: 24px; }
.chord-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; }
.chord-card h2 { font-size: 17px; display: flex; justify-content: space-between; gap: 8px; }
.chord-card h2 span { color: var(--accent); }
.chord-diagram { display: block; width: 100%; max-width: 240px; height: auto; margin: 20px auto; }
.chord-fret, .chord-string { stroke: var(--muted); stroke-width: 1.5; }
.chord-nut { stroke: var(--text); stroke-width: 5; }
.chord-string-label, .chord-open-muted { fill: var(--text); font-size: 14px; }
.chord-fret-label { fill: var(--muted); font-size: 12px; }
.chord-finger { fill: var(--text); }
.chord-finger-number { fill: var(--surface); font-size: 12px; font-weight: 700; }
.chord-detail-layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2fr); gap: 24px; }
.chord-detail-diagram { text-align: center; align-self: start; }
.chord-detail-diagram h2 { font-size: 36px; color: var(--accent); }
.chord-detail-diagram .chord-legend { margin-bottom: 0; }
.strumming-lessons { display: grid; gap: 24px; margin-top: 24px; }
.strumming-pattern { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 8px; margin-block: 24px; max-width: 640px; }
.strumming-beat { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.strumming-stroke { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 64px; width: 100%; border-radius: 8px; background: var(--soft); color: var(--accent); font-size: 20px; font-weight: 600; }
.strumming-rest { color: var(--muted); }
.strumming-stroke > span { font-size: 15px; }
.strumming-count { color: var(--muted); font-size: 13px; }
@media (max-width: 1100px) { .chord-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 900px) { .chord-detail-layout { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 767px) {
  .lesson-hero, .lesson-grid, .lesson-basics-grid { grid-template-columns: minmax(0, 1fr); }
  .lesson-hero .practice-card { padding: 24px; }
  .lesson-hero img { min-height: 0; max-height: 260px; }
  .chord-grid { gap: 12px; }
  .chord-card { padding: 16px 12px; }
  .chord-card h2 { font-size: 15px; flex-wrap: wrap; }
  .strumming-pattern { gap: 4px; }
  .strumming-stroke { font-size: 17px; }
}
@media (max-width: 479px) {
  .chord-grid { grid-template-columns: minmax(0, 1fr); }
  .chord-card { padding: 20px; }
  .chord-card h2 { font-size: 17px; }
}
```

## assets/js/tuner.js

```javascript
// Microphone lifecycle and UI for the tuner only. No recordings or audio uploads.
import { detectPitch, describePitch, PitchStabilizer } from "./tuner-pitch.js";

export function mountTuner(page) {
  const find = (id) => page.querySelector(`#tuner-${id}`);
  const startButton = find("start");
  const stopButton = find("stop");
  const container = page.querySelector(".tuner-container");
  const stabilizer = new PitchStabilizer();
  let stream = null;
  let context = null;
  let source = null;
  let analyser = null;
  let frame = null;
  let generation = 0;
  let active = false;
  let pending = false;
  let lastRead = 0;
  let lastReliable = 0;

  function clearPitch() {
    find("note").textContent = "—";
    find("octave").textContent = "";
    find("frequency").textContent = "— Hz";
    find("cents").textContent = "— cents";
    find("status").textContent = "Play a string";
    find("indicator").hidden = true;
    find("meter").setAttribute("aria-valuenow", "0");
    find("meter").setAttribute("aria-valuetext", "No reliable pitch");
    delete container.dataset.tuning;
    page.querySelectorAll("[data-tuning-note]").forEach((node) => delete node.dataset.active);
  }

  function showError(state, message) {
    find("microphone").textContent = state;
    find("error").textContent = message;
    find("error").hidden = false;
  }

  function stopTuner() {
    generation++;
    active = false;
    pending = false;
    cancelAnimationFrame(frame);
    frame = null;
    if (stream) stream.getTracks().forEach((track) => track.stop());
    if (source) source.disconnect();
    if (analyser) analyser.disconnect();
    if (context) {
      context.onstatechange = null;
      if (context.state !== "closed") void context.close().catch(() => {});
    }
    stream = context = source = analyser = null;
    stabilizer.reset();
    clearPitch();
    find("microphone").textContent = "Microphone inactive";
    startButton.disabled = false;
    stopButton.disabled = true;
  }

  function renderPitch(frequency) {
    const pitch = describePitch(frequency);
    find("note").textContent = pitch.note;
    find("octave").textContent = pitch.octave;
    find("frequency").textContent = `${pitch.frequency.toFixed(1)} Hz`;
    const rounded = Math.round(pitch.cents);
    find("cents").textContent = `${rounded > 0 ? "+" : ""}${rounded === 0 ? 0 : rounded} cents`;
    find("status").textContent = pitch.status;
    container.dataset.tuning = pitch.tuning;
    const cents = Math.max(-50, Math.min(50, pitch.cents));
    find("indicator").hidden = false;
    find("indicator").style.left = `${50 + cents}%`;
    find("meter").setAttribute("aria-valuenow", cents.toFixed(1));
    find("meter").setAttribute("aria-valuetext", `${pitch.note}${pitch.octave}, ${rounded} cents, ${pitch.status}`);
    page.querySelectorAll("[data-tuning-note]").forEach((node) => {
      node.toggleAttribute("data-active", node.dataset.tuningNote === `${pitch.note}${pitch.octave}`);
    });
  }

  async function startTuner() {
    if (active || pending) return;
    find("error").hidden = true;
    if (!window.isSecureContext) {
      showError("Microphone unavailable", "Microphone access requires HTTPS or localhost. Open AUDIA using a secure address.");
      return;
    }
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!navigator.mediaDevices?.getUserMedia || !AudioContextClass) {
      showError("Microphone unavailable", "Your browser does not support the audio features required by the tuner.");
      return;
    }
    const ticket = ++generation;
    pending = true;
    startButton.disabled = true;
    stopButton.disabled = false;
    find("microphone").textContent = "Requesting microphone";
    try {
      // Resume directly from the button gesture, including on mobile browsers.
      const audioContext = new AudioContextClass();
      context = audioContext;
      await audioContext.resume();
      if (ticket !== generation) return;
      const microphone = await navigator.mediaDevices.getUserMedia({ audio: {
        echoCancellation: false, noiseSuppression: false, autoGainControl: false,
      } });
      // Stop may be pressed while the browser's permission prompt is still open.
      if (ticket !== generation) {
        microphone.getTracks().forEach((track) => track.stop());
        return;
      }
      stream = microphone;
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 4096;
      source = audioContext.createMediaStreamSource(microphone);
      source.connect(analyser);
      // No connection to destination: the microphone never plays through speakers.
      const samples = new Float32Array(analyser.fftSize);
      active = true;
      pending = false;
      lastRead = 0;
      lastReliable = performance.now();
      find("microphone").textContent = "Listening";
      microphone.getTracks().forEach((track) => track.addEventListener("ended", () => {
        if (ticket !== generation) return;
        stopTuner();
        showError("Microphone unavailable", "The microphone was disconnected. Reconnect it and start the tuner again.");
      }, { once: true }));
      audioContext.onstatechange = () => {
        if (!active || ticket !== generation || audioContext.state === "running") return;
        stopTuner();
        showError("Microphone inactive", "Audio was interrupted. Press Start Tuner to listen again.");
      };

      function listen(now) {
        if (!active || ticket !== generation) return;
        // About twelve estimates per second keeps processing light on phones.
        if (now - lastRead >= 80) {
          lastRead = now;
          try {
            analyser.getFloatTimeDomainData(samples);
            const pitch = detectPitch(samples, audioContext.sampleRate);
            const frequency = pitch ? stabilizer.push(pitch.frequency) : null;
            if (frequency) { renderPitch(frequency); lastReliable = now; }
            if (now - lastReliable > 650) {
              stabilizer.reset();
              clearPitch();
              lastReliable = now;
            }
          } catch {
            stopTuner();
            showError("Microphone unavailable", "Audio could not be processed. Stop other audio apps and try again.");
            return;
          }
        }
        frame = requestAnimationFrame(listen);
      }
      frame = requestAnimationFrame(listen);
    } catch (error) {
      if (ticket !== generation) return;
      stopTuner();
      if (["NotAllowedError", "PermissionDeniedError", "SecurityError"].includes(error.name)) {
        showError("Permission denied", "Microphone access is required to use the guitar tuner. Please allow microphone access in your browser settings.");
      } else if (["NotFoundError", "DevicesNotFoundError"].includes(error.name)) {
        showError("Microphone unavailable", "No microphone was detected on this device.");
      } else {
        showError("Microphone unavailable", "The microphone could not be started. It may be in use by another app. Close it and try again.");
      }
    }
  }

  startButton.addEventListener("click", startTuner);
  stopButton.addEventListener("click", () => { stopTuner(); find("error").hidden = true; });
  window.addEventListener("pagehide", stopTuner);
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopTuner(); });
}
```

## assets/js/tuner-pitch.js

```javascript
// Pure pitch calculations, separate from microphone controls and page rendering.
// YIN: de Cheveigné & Kawahara (2002), doi:10.1121/1.1458024.
const NOTE_NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];

export function detectPitch(input, sampleRate) {
  if (!input.length || !Number.isFinite(sampleRate) || sampleRate <= 0) return null;
  let mean = 0;
  for (const value of input) mean += value;
  mean /= input.length;
  let energy = 0;
  for (const value of input) energy += (value - mean) ** 2;
  if (Math.sqrt(energy / input.length) < 0.008) return null;

  // Average groups of samples to reduce work while preserving guitar pitches.
  const step = Math.max(1, Math.floor(sampleRate / 12000));
  const rate = sampleRate / step;
  const samples = new Float32Array(Math.floor(input.length / step));
  for (let index = 0; index < samples.length; index++) {
    let sum = 0;
    for (let offset = 0; offset < step; offset++) sum += input[index * step + offset] - mean;
    samples[index] = sum / step;
  }
  const minLag = Math.floor(rate / 420);
  const maxLag = Math.ceil(rate / 65);
  const windowSize = samples.length - maxLag - 1;
  if (windowSize < maxLag) return null;
  const difference = new Float32Array(maxLag + 1);
  difference[0] = 1;
  let runningSum = 0;
  for (let lag = 1; lag <= maxLag; lag++) {
    let sum = 0;
    for (let index = 0; index < windowSize; index++) {
      const delta = samples[index] - samples[index + lag];
      sum += delta * delta;
    }
    runningSum += sum;
    // Cumulative mean normalized difference rejects nonperiodic input.
    difference[lag] = runningSum ? (sum * lag) / runningSum : 1;
  }
  let lag = minLag;
  while (lag < maxLag && difference[lag] >= 0.15) lag++;
  if (lag >= maxLag) return null;
  while (lag + 1 <= maxLag && difference[lag + 1] < difference[lag]) lag++;
  if (lag >= maxLag) return null;
  const left = difference[lag - 1];
  const center = difference[lag];
  const right = difference[lag + 1];
  const denominator = left - 2 * center + right;
  const refinedLag = lag + (denominator ? (left - right) / (2 * denominator) : 0);
  const frequency = rate / refinedLag;
  if (!Number.isFinite(frequency) || frequency < 65 || frequency > 420) return null;
  return { frequency, confidence: 1 - center };
}

export function describePitch(frequency) {
  const midi = Math.round(69 + 12 * Math.log2(frequency / 440));
  const target = 440 * 2 ** ((midi - 69) / 12);
  const cents = 1200 * Math.log2(frequency / target);
  const note = NOTE_NAMES[((midi % 12) + 12) % 12];
  const octave = Math.floor(midi / 12) - 1;
  const magnitude = Math.abs(cents);
  const status = magnitude <= 5 ? "In Tune"
    : cents < 0 ? (magnitude <= 15 ? "Slightly Flat" : "Too Flat")
    : magnitude <= 15 ? "Slightly Sharp" : "Too Sharp";
  return { note, octave, frequency, cents, status,
    tuning: magnitude <= 5 ? "in-tune" : cents < 0 ? "flat" : "sharp" };
}

export class PitchStabilizer {
  constructor() { this.reset(); }
  reset() { this.readings = []; this.smoothed = null; }
  push(frequency) {
    const semitones = 69 + 12 * Math.log2(frequency / 440);
    if (this.readings.length && Math.abs(semitones - this.readings.at(-1)) > 0.35) {
      this.readings = [];
    }
    this.readings.push(semitones);
    if (this.readings.length > 5) this.readings.shift();
    if (this.readings.length < 3) return null;
    const sorted = [...this.readings].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    this.smoothed = this.smoothed === null || Math.abs(median - this.smoothed) > 0.5
      ? median : this.smoothed * 0.6 + median * 0.4;
    return 440 * 2 ** ((this.smoothed - 69) / 12);
  }
}
```

## tests/test_practice.py

```python
"""New feature routes use the existing auth/security hooks and disposable data."""
import re
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from support import create_app
from modules.database import db, initialize
from modules.models import User
from werkzeug.security import generate_password_hash


class PracticeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="audia-practice-")
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "practice-tests-only",
            "DATABASE_URL": f'sqlite:///{Path(self.directory.name) / "test.db"}',
        })
        initialize(self.app)
        with self.app.app_context():
            db().add(User(name="Practice Player", email="practice@example.com",
                          password_hash=generate_password_hash("practice-password-123")))
            db().commit()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app.extensions["engine"].dispose()
        self.directory.cleanup()

    def sign_in(self):
        csrf = self.client.get("/api/auth/session").json["csrf_token"]
        result = self.client.post("/api/auth/login", json={
            "email": "practice@example.com", "password": "practice-password-123",
        }, headers={"X-CSRF-Token": csrf})
        self.assertEqual(result.status_code, 200)

    def test_guest_redirects_and_security(self):
        for path in ("/tuner", "/lessons", "/lessons/getting-started", "/lessons/chords",
                     "/lessons/chords/c-major", "/lessons/strumming"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertEqual(response.location, "/login")
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.client.post("/api/chat", json={"message": "hello"}).status_code, 403)
        self.assertEqual(self.client.get("/api/products").status_code, 401)

    def test_pages_assets_and_navigation(self):
        self.sign_in()
        for path in ("/tuner", "/lessons", "/lessons/getting-started", "/lessons/chords", "/lessons/strumming"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            html = response.get_data(as_text=True)
            for link in re.findall(r'(?:href|src)="([^"]+)"', html):
                if link.startswith("/"):
                    with self.client.get(link.split("#")[0]) as linked:
                        self.assertEqual(linked.status_code, 200, link)
        for path in ("/", "/shop", "/account"):
            html = self.client.get(path).get_data(as_text=True)
            self.assertIn('href="/tuner"', html)
            self.assertIn('href="/lessons"', html)
        for filename in ("css/practice.css", "css/tuner.css", "css/lessons.css", "js/tuner.js", "js/tuner-pitch.js"):
            with self.client.get("/static/" + filename) as asset:
                self.assertEqual(asset.status_code, 200)

    def test_all_chord_shapes_and_missing_chord(self):
        self.sign_in()
        shapes = {
            "c-major": (1, 2, 3), "g-major": (0, 3, 3), "d-major": (2, 1, 3),
            "a-major": (1, 2, 3), "e-major": (0, 3, 3), "a-minor": (1, 2, 3),
            "e-minor": (0, 4, 2), "d-minor": (2, 1, 3),
        }
        for slug, (muted, opened, fretted) in shapes.items():
            html = self.client.get("/lessons/chords/" + slug).get_data(as_text=True)
            diagram = ElementTree.fromstring(re.search(r'<svg class="chord-diagram".*?</svg>', html, re.S)[0])
            strings = diagram.findall(".//line[@class='chord-string']")
            self.assertEqual(len(strings), 6, slug)
            self.assertEqual([int(line.attrib["x1"]) for line in strings], [35, 65, 95, 125, 155, 185])
            markers = [node.text for node in diagram.findall(".//text[@class='chord-open-muted']")]
            self.assertEqual(markers.count("X"), muted, slug)
            self.assertEqual(markers.count("O"), opened, slug)
            self.assertEqual(len(diagram.findall(".//circle")), fretted, slug)
            self.assertIn("Finger placement", html)
        self.assertEqual(self.client.get("/lessons/chords/missing-chord").status_code, 404)

    def test_revoked_session_and_read_only_routes(self):
        self.sign_in()
        csrf = self.client.get("/api/auth/session").json["csrf_token"]
        cookie = self.client.get_cookie("session").value
        self.assertEqual(self.client.post("/tuner").status_code, 405)
        self.client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
        self.client.set_cookie("session", cookie)
        self.assertEqual(self.client.get("/tuner").status_code, 302)
        self.assertEqual(self.client.get("/lessons").status_code, 302)


if __name__ == "__main__":
    unittest.main()
```

## tests/tuner-pitch.cjs

```javascript
// Run with node tests/tuner-pitch.cjs. No microphone or npm dependency required.
const assert = require('node:assert/strict');
const fs = require('node:fs');

(async () => {
  const code = fs.readFileSync('assets/js/tuner-pitch.js', 'utf8');
  const { detectPitch, describePitch, PitchStabilizer } = await import(
    'data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
  const targets = [[82.406889, 'E', 2], [110, 'A', 2], [146.832384, 'D', 3],
    [195.997718, 'G', 3], [246.941651, 'B', 3], [329.627557, 'E', 4]];
  for (const rate of [44100, 48000, 96000]) {
    for (const [target, note, octave] of targets) {
      for (const cents of [-25, -10, 0, 10, 25]) {
        const frequency = target * 2 ** (cents / 1200);
        // A plucked-string-like signal with harmonics and a decaying envelope.
        const samples = Float32Array.from({ length: 4096 }, (_, index) => {
          const phase = 2 * Math.PI * frequency * index / rate;
          return Math.exp(-index / rate * 3) * (.2 * Math.sin(phase) + .12 * Math.sin(phase * 2) + .06 * Math.sin(phase * 3));
        });
        const detected = detectPitch(samples, rate);
        assert.ok(detected, `${note}${octave}, ${cents} cents, ${rate} Hz`);
        const pitch = describePitch(detected.frequency);
        assert.equal(pitch.note, note); assert.equal(pitch.octave, octave);
        assert.ok(Math.abs(pitch.cents - cents) < 2, `Pitch error: ${pitch.cents - cents} cents`);
        assert.equal(pitch.status, cents === 0 ? 'In Tune' : cents < -15 ? 'Too Flat'
          : cents < 0 ? 'Slightly Flat' : cents > 15 ? 'Too Sharp' : 'Slightly Sharp');
      }
    }
  }
  assert.equal(detectPitch(new Float32Array(4096), 48000), null);
  assert.equal(detectPitch(new Float32Array(4096).fill(.2), 48000), null, 'DC input');
  assert.equal(detectPitch(Float32Array.from({ length: 4096 }, (_, i) => .001 * Math.sin(i)), 48000), null);
  let seed = 123;
  const noise = Float32Array.from({ length: 4096 }, () => {
    seed = (1664525 * seed + 1013904223) >>> 0;
    return (seed / 2 ** 32 - .5) * .3;
  });
  assert.equal(detectPitch(noise, 48000), null, 'Broadband noise');
  const smoother = new PitchStabilizer();
  assert.equal(smoother.push(110), null); assert.equal(smoother.push(110.1), null);
  assert.ok(Math.abs(smoother.push(110) - 110) < .1);
  assert.equal(smoother.push(196), null, 'One outlier cannot change the note');
  assert.equal(smoother.push(110), null); smoother.push(110);
  assert.ok(Math.abs(smoother.push(110) - 110) < .1);
  smoother.reset(); assert.equal(smoother.push(82.4), null);
  console.log('PASS: 90 harmonic pitch cases across six strings, three sample rates, flat/sharp/in-tune; silence, weak input, noise and stabilization');
})().catch(error => { console.error(error); process.exitCode = 1; });
```

## tests/practice.cjs

```javascript
// Run against python tests/serve.py (disposable database), never production.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';

(async () => {
  const browser = await chromium.launch({ headless: true, args: [
    '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
  ] });
  const errors = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const email = `practice-${Date.now()}@example.com`;
    let session = await (await context.request.get(base + '/api/auth/session')).json();
    const register = await context.request.post(base + '/api/auth/register', {
      headers: { 'X-CSRF-Token': session.csrf_token },
      data: { name: 'Practice Player', email, password: 'practice-password-123' },
    });
    assert.equal(register.status(), 201);
    session = await (await context.request.get(base + '/api/auth/session')).json();
    assert.equal((await context.request.post(base + '/api/auth/login', {
      headers: { 'X-CSRF-Token': session.csrf_token }, data: { email, password: 'practice-password-123' },
    })).status(), 200);

    // Use real Web Audio nodes and streams for deterministic pitch/lifecycle tests.
    // The app still executes its actual getUserMedia -> analyser -> YIN path.
    await context.addInitScript(() => {
      const NativeAudioContext = window.AudioContext;
      const nativeGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
      window.__audio = { mode: 'sine', calls: 0, stopped: 0, contexts: [], frequency: 110, stream: null };
      window.AudioContext = class extends NativeAudioContext {
        constructor(...args) { super(...args); window.__audio.contexts.push(this); }
      };
      navigator.mediaDevices.getUserMedia = async (constraints) => {
        const state = window.__audio;
        state.calls++;
        if (state.mode === 'pending') await new Promise(resolve => { state.resolve = resolve; });
        if (['denied', 'missing', 'busy'].includes(state.mode)) {
          throw new DOMException('Test microphone error', state.mode === 'denied'
            ? 'NotAllowedError' : state.mode === 'missing' ? 'NotFoundError' : 'NotReadableError');
        }
        let stream;
        if (state.mode === 'native') stream = await nativeGetUserMedia(constraints);
        else {
          const generator = new NativeAudioContext();
          await generator.resume();
          const oscillator = generator.createOscillator();
          oscillator.frequency.value = state.frequency;
          const gain = generator.createGain(); gain.gain.value = .2;
          const destination = generator.createMediaStreamDestination();
          oscillator.connect(gain); gain.connect(destination); oscillator.start();
          stream = destination.stream;
          state.setPitch = frequency => oscillator.frequency.setValueAtTime(frequency, generator.currentTime);
          state.setVolume = volume => gain.gain.setValueAtTime(volume, generator.currentTime);
          state.disconnect = () => { stream.getTracks()[0].dispatchEvent(new Event('ended')); };
          state.cleanup = () => { oscillator.stop(); void generator.close(); };
        }
        for (const track of stream.getTracks()) {
          const stop = track.stop.bind(track);
          track.stop = () => { state.stopped++; stop(); state.cleanup?.(); };
        }
        state.stream = stream;
        return stream;
      };
    });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    const newRequests = [];
    page.on('request', request => {
      if (request.method() !== 'GET') newRequests.push(request.method() + ' ' + new URL(request.url()).pathname);
    });
    const ready = () => page.locator('#root:not([inert])').waitFor();
    const start = () => page.getByRole('button', { name: 'Start Tuner', exact: true }).click();
    const stop = () => page.getByRole('button', { name: 'Stop Tuner', exact: true }).click();
    await page.goto(base + '/tuner'); await ready();
    assert.equal(await page.evaluate(() => window.__audio.calls), 0, 'No permission prompt on page load');
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    const targets = [[82.406889, 'E', '2'], [110, 'A', '2'], [146.832384, 'D', '3'],
      [195.997718, 'G', '3'], [246.941651, 'B', '3'], [329.627557, 'E', '4']];
    for (const [frequency, note, octave] of targets) {
      await page.evaluate(frequency => window.__audio.setPitch(frequency), frequency);
      await page.waitForFunction(({ note, octave }) => document.querySelector('#tuner-note').textContent === note
        && document.querySelector('#tuner-octave').textContent === octave
        && document.querySelector('#tuner-status').textContent === 'In Tune', { note, octave });
      assert.equal(await page.locator(`[data-tuning-note="${note}${octave}"][data-active]`).count(), 1);
      assert.ok(Math.abs(parseFloat(await page.locator('#tuner-frequency').innerText()) - frequency) < .5);
    }
    for (const [cents, status] of [[-25, 'Too Flat'], [-10, 'Slightly Flat'], [10, 'Slightly Sharp'], [25, 'Too Sharp']]) {
      await page.evaluate(frequency => window.__audio.setPitch(frequency), 110 * 2 ** (cents / 1200));
      await page.getByText(status, { exact: true }).waitFor();
      const position = await page.locator('#tuner-indicator').evaluate(node => parseFloat(node.style.left));
      assert.ok(cents < 0 ? position < 50 : position > 50);
    }
    await page.evaluate(() => window.__audio.setVolume(0));
    await page.getByText('Play a string', { exact: true }).waitFor();
    assert.equal(await page.locator('#tuner-indicator').isHidden(), true);
    await page.evaluate(() => { window.__audio.setPitch(110); window.__audio.setVolume(.2); });
    await page.getByText('In Tune', { exact: true }).waitFor();
    await stop();
    await page.waitForFunction(() => window.__audio.contexts.every(context => context.state === 'closed'));
    assert.equal(await page.evaluate(() => window.__audio.stream.getTracks().every(track => track.readyState === 'ended')), true);

    for (const [mode, message] of [['denied', 'Permission denied'], ['missing', 'No microphone was detected'], ['busy', 'The microphone could not be started']]) {
      await page.evaluate(mode => { window.__audio.mode = mode; }, mode);
      await start(); await page.getByText(message, { exact: mode === 'denied' }).waitFor();
      assert.equal(await page.getByRole('button', { name: 'Start Tuner', exact: true }).isEnabled(), true);
      await page.waitForFunction(() => window.__audio.contexts.every(context => context.state === 'closed'));
    }
    await page.evaluate(() => { window.__audio.mode = 'pending'; });
    await start(); await page.getByText('Requesting microphone', { exact: true }).waitFor();
    await page.waitForFunction(() => Boolean(window.__audio.resolve));
    await stop(); await page.evaluate(() => { window.__audio.mode = 'sine'; window.__audio.resolve(); });
    await page.waitForFunction(() => window.__audio.stopped === 2);
    assert.equal(await page.locator('#tuner-microphone').innerText(), 'Microphone inactive');
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => window.__audio.disconnect());
    await page.getByText(/The microphone was disconnected/).waitFor();

    // Also exercise actual browser microphone permission and capture with a fake device.
    await page.evaluate(() => { window.__audio.mode = 'native'; window.__audio.cleanup = null; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await stop();
    assert.equal(await page.evaluate(() => window.__audio.stream.getTracks()[0].readyState), 'ended');

    await page.evaluate(() => { window.__audio.mode = 'sine'; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { configurable: true, value: true });
      document.dispatchEvent(new Event('visibilitychange'));
      delete document.hidden;
    });
    await page.waitForFunction(() => window.__audio.stream.getTracks()[0].readyState === 'ended'
      && window.__audio.contexts.every(context => context.state === 'closed'));
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
    await page.waitForFunction(() => window.__audio.stream.getTracks()[0].readyState === 'ended'
      && window.__audio.contexts.every(context => context.state === 'closed'));

    await page.evaluate(() => { window.__audio.mode = 'sine'; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.goto(base + '/lessons'); await ready();
    assert.ok(await page.getByRole('heading', { name: 'Learn Guitar', exact: true }).count());
    await page.getByRole('link', { name: 'Start learning', exact: true }).click(); await ready();
    await page.getByRole('link', { name: 'Next: basic chords →', exact: true }).click(); await ready();
    assert.equal(await page.locator('.chord-diagram').count(), 8);
    await page.locator('.chord-card').first().click(); await ready();
    assert.equal(await page.locator('.chord-diagram .chord-string').count(), 6);
    await page.getByRole('link', { name: 'Add a strumming pattern →', exact: true }).click(); await ready();
    assert.equal(await page.locator('.strumming-pattern').count(), 3);
    for (const pattern of await page.locator('.strumming-pattern').all()) {
      assert.deepEqual(await pattern.locator('.strumming-count').allTextContents(), ['1', '&', '2', '&', '3', '&', '4', '&']);
    }

    const routes = ['/tuner', '/lessons', '/lessons/getting-started', '/lessons/chords', '/lessons/strumming',
      ...['c-major', 'g-major', 'd-major', 'a-major', 'e-major', 'a-minor', 'e-minor', 'd-minor'].map(slug => '/lessons/chords/' + slug)];
    for (const route of routes) {
      await page.goto(base + route); await ready();
      for (const theme of ['dark', 'light']) {
        if (await page.locator('html').evaluate(node => node.classList.contains('dark')) !== (theme === 'dark')) {
          await page.locator('[data-action="theme"]').click();
        }
        for (const width of [320, 375, 768, 1024, 1440]) {
          await page.setViewportSize({ width, height: 1000 });
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${route}: ${theme} at ${width}px`);
          const clipped = await page.locator('.chord-diagram, .tuner-meter, .strumming-pattern, .practice-nav').evaluateAll(nodes =>
            nodes.some(node => { const box = node.getBoundingClientRect(); return box.left < 0 || box.right > innerWidth; }));
          assert.equal(clipped, false, `${route}: clipped component at ${width}px`);
          const tinyDiagrams = await page.locator('.chord-diagram').evaluateAll(nodes =>
            nodes.some(node => node.getBoundingClientRect().width < 180));
          assert.equal(tinyDiagrams, false, `${route}: chord diagram too small to read at ${width}px`);
          if (process.env.SCREENSHOT_DIR && width === 320 && ['/tuner', '/lessons', '/lessons/chords', '/lessons/strumming'].includes(route)) {
            fs.mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
            await page.screenshot({ path: `${process.env.SCREENSHOT_DIR}/${route.slice(1).replaceAll('/', '-')}-${theme}-mobile.png`, fullPage: true });
          }
        }
        if (process.env.SCREENSHOT_DIR && ['/tuner', '/lessons', '/lessons/chords', '/lessons/strumming'].includes(route)) {
          fs.mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
          await page.screenshot({ path: `${process.env.SCREENSHOT_DIR}/${route.slice(1).replaceAll('/', '-')}-${theme}.png`, fullPage: true });
        }
      }
    }
    assert.deepEqual(newRequests, [], 'Practice pages must never upload audio or mutate server state');
    assert.deepEqual(errors, [], 'No browser JavaScript errors');
    console.log('PASS: Audio capture, six strings, flat/sharp meter, silence recovery, denial/missing/busy, stop, pending cancellation, disconnect and restart');
    console.log('PASS: Lessons, eight SVG shapes, beat alignment, links, 130 layout/theme cases and no JavaScript errors or audio uploads');
    const storage = await context.storageState();
    await context.close();

    // Unsupported browser must produce an actionable message without an uncaught error.
    const unsupported = await browser.newContext({ storageState: storage });
    await unsupported.addInitScript(() => { window.AudioContext = undefined; window.webkitAudioContext = undefined; });
    const unsupportedPage = await unsupported.newPage();
    await unsupportedPage.goto(base + '/tuner'); await unsupportedPage.locator('#root:not([inert])').waitFor();
    await unsupportedPage.getByRole('button', { name: 'Start Tuner' }).click();
    await unsupportedPage.getByText(/Your browser does not support/).waitFor();
    await unsupportedPage.evaluate(() => Object.defineProperty(window, 'isSecureContext', { value: false, configurable: true }));
    await unsupportedPage.getByRole('button', { name: 'Start Tuner' }).click();
    await unsupportedPage.getByText(/Microphone access requires HTTPS or localhost/).waitFor();
    await unsupported.close();
    console.log('PASS: Unsupported audio API, insecure address and page lifecycle cleanup');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
```

## docs/guitar-practice.md

````markdown
# AUDIA guitar tuner and lessons

The two features are integrated into the existing Flask application. Sign in and
open **Guitar Tuner** or **Guitar Lessons** from the landing, store, or account
page. The new pages link back to the store, products, account, and each other,
and include the existing AUDIA Assistant.

## Architecture findings

AUDIA creates its Flask app in `app.py`. Existing HTML page routes use Jinja
templates; authentication, catalog, orders, administration, and chatbot APIs
are registered as blueprints. Those APIs use `/api` prefixes. `modules/ai.py`
provides the Gemini/RAG service called by `modules/chatbot.py`; it is not a
separate page blueprint. The database lifecycle lives in `modules/database.py`,
and SQLAlchemy records live in `modules/models.py`. Normal development uses
PostgreSQL; tests use disposable SQLite databases.

Templates extend `templates/base.html`. It loads `assets/css/shared.css`, the
page's stylesheet, and `assets/js/app.js`. Assets are served at `/static/`.
The shared stylesheet contains existing utilities, typography, cards, buttons,
dialogs, chatbot styling, and theme variables. Page controllers use ordinary
JavaScript modules. Repeated client-side components use HTML templates, and
navigation uses normal page URLs. Icons use the existing inline SVG style.

`modules/auth.py` installs app-wide session restoration, CSRF checks, security
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
| `modules/tuner.py` | Authenticated `/tuner` page blueprint; no audio reaches Python. |
| `modules/lessons.py` | Authenticated lesson routes and missing-chord 404 handling. |
| `modules/lessons_content.py` | Static chord shapes, finger instructions, and strumming patterns. |
| `templates/practice/base.html` | Shared header, content area, and existing chatbot for both new features. |
| `templates/practice/feature_links.html` | Reusable links added below existing page headers, visible on mobile too. |
| `templates/tuner/tuner.html` | Live note readout, meter, microphone controls, errors, privacy text, and string reference. |
| `templates/lessons/index.html` | Lesson landing page and category links. |
| `templates/lessons/getting_started.html` | Guitar parts, posture, pick grip, string names, and tuning instructions. |
| `templates/lessons/chords.html` | Library of eight chords. |
| `templates/lessons/chord_detail.html` | One chord's diagram and playing instructions. |
| `templates/lessons/_chord_diagram.html` | Reusable Jinja macro that draws an accessible SVG chord diagram. |
| `templates/lessons/strumming.html` | Down/up strokes, beat counts, patterns, and practice tips. |
| `assets/css/practice.css` | Shared layout for these two features, using AUDIA's existing theme variables. |
| `assets/css/tuner.css` | Tuner layout, meter, note display, and string highlight. Imports `practice.css`. |
| `assets/css/lessons.css` | Lesson grids, chord diagrams, and strumming pattern layouts. Imports `practice.css`. |
| `assets/js/tuner.js` | Start/stop controls, audio resource cleanup, errors, and pitch display. |
| `assets/js/tuner-pitch.js` | Independent YIN pitch estimator, note/cents conversion, and stabilization. |
| `tests/test_practice.py` | Routes, auth, assets, navigation, chord structure, and session revocation tests. |
| `tests/tuner-pitch.cjs` | Deterministic pitch tests with generated harmonic signals. |
| `tests/practice.cjs` | Browser audio, error/lifecycle, lessons, responsive, and theme checks. |
| `docs/guitar-practice.md` | This architecture and operating guide. |
| `docs/guitar-practice-source.md` | Complete updated contents of implementation, integration, test, and guide files. |

Lessons are static server-rendered pages, so they do not need a `lessons.js`
controller. SVG diagrams and ordinary links work without another frontend
framework or external image service.

## Existing files minimally modified

| File | Change made for this task |
| --- | --- |
| `app.py` | Import and register the `tuner` and `lessons` blueprints: four added lines. |
| `assets/js/app.js` | Include the two new page names in its existing signed-in check; dynamically start the tuner controller on the tuner page only. |
| `templates/landing.html` | Include the practice navigation partial after the existing header. |
| `templates/storefront.html` | Include the same navigation partial after the existing header. |
| `templates/account.html` | Include the same navigation partial after the existing header. |

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

To add a chord, add a record to `CHORDS` in `modules/lessons_content.py` with
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

The complete updated source is provided in `guitar-practice-source.md`,
including whole existing integration files rather than isolated snippets.
````
