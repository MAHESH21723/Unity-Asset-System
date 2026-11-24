"""Unity AI Architect: Flask web app that turns a game concept into Unity
asset recommendations, architecture, folder layout, C# starter scripts and a roadmap.

Run locally with ``python app.py`` (see README.md).
"""

from __future__ import annotations

import hmac
import io
import json
import logging
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from werkzeug.middleware.proxy_fix import ProxyFix

from ai_engine import ENGINES, generate_recommendations
from exports import build_markdown_report, build_starter_kit, safe_filename

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

GENRES = (
    "Platformer", "Puzzle", "RPG", "Shooter", "Action", "Strategy",
    "Adventure", "Simulation", "Racing", "Sandbox", "VR/AR", "Mobile Casual",
)
PLATFORMS = ("PC", "Android", "iOS", "Console", "WebGL", "VR/AR")
AUDIENCES = ("Kids", "Casual", "Core", "Hardcore")

DEMO_NOTICE = "Public demo: data is shared and resets, don't enter personal information."

MAX_TITLE = 100
MIN_DESCRIPTION = 20
MAX_DESCRIPTION = 2000
HISTORY_LIMIT = 100

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    genre TEXT NOT NULL,
    platform TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    generated_scripts TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""


# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #
def get_db() -> sqlite3.Connection:
    """Return the per-request SQLite connection (closed automatically)."""
    if "db" not in g:
        g.db = sqlite3.connect(g.app_database)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(database: str | os.PathLike[str]) -> None:
    """Create the database file and schema if they do not exist."""
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(SCHEMA)
    conn.close()


def count_projects() -> int:
    try:
        return get_db().execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    except sqlite3.Error:
        logger.exception("Could not count projects")
        return 0


def _get_project(project_id: int) -> sqlite3.Row:
    project = get_db().execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if project is None:
        abort(404)
    return project


def _like_pattern(text: str) -> str:
    """Escape LIKE wildcards so user input is matched literally."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def validate_form(form: dict[str, str]) -> list[str]:
    """Return a list of human-readable validation errors (empty when valid)."""
    errors = []
    name = form["project_name"]
    if not name:
        errors.append("Project Name (Game Title) is required.")
    elif len(name) > MAX_TITLE:
        errors.append(f"Project Name must be {MAX_TITLE} characters or less.")

    for field, label, allowed in (
        ("genre", "Genre", GENRES),
        ("platform", "Platform", PLATFORMS),
        ("target_audience", "Target Audience", AUDIENCES),
    ):
        if not form[field]:
            errors.append(f"{label} selection is required.")
        elif form[field] not in allowed:
            errors.append(f"{label} selection is not valid.")

    description = form["description"]
    if not description:
        errors.append("Game Description is required.")
    elif len(description) < MIN_DESCRIPTION:
        errors.append(f"Game Description should be at least {MIN_DESCRIPTION} characters to allow meaningful analysis.")
    elif len(description) > MAX_DESCRIPTION:
        errors.append(f"Game Description must be {MAX_DESCRIPTION} characters or less.")

    if form["engine_choice"] not in ENGINES:
        errors.append("Engine selection is not valid.")
    return errors


# --------------------------------------------------------------------------- #
# Application factory
# --------------------------------------------------------------------------- #
def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.update(
        # Without SECRET_KEY a random per-process key is used (sessions reset on restart).
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.getenv("DATABASE_PATH", str(BASE_DIR / "unity_ai.db")),
        CSRF_ENABLED=True,
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if os.getenv("RENDER"):
        # Behind Render's HTTPS proxy: trust one hop of X-Forwarded-* headers.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
        app.config["SESSION_COOKIE_SECURE"] = True
    app.config["DEMO_DATA"] = os.getenv("DEMO_DATA") == "1"
    if test_config:
        app.config.update(test_config)

    init_db(app.config["DATABASE"])

    @app.before_request
    def _setup_request() -> None:
        g.app_database = app.config["DATABASE"]
        if app.config["CSRF_ENABLED"] and request.method == "POST":
            sent = request.form.get("csrf_token", "")
            expected = session.get("csrf_token", "")
            if not expected or not hmac.compare_digest(sent, expected):
                abort(400, description="Invalid or missing CSRF token. Reload the page and try again.")

    @app.teardown_appcontext
    def _close_db(_exc: BaseException | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.context_processor
    def _inject_helpers() -> dict[str, Any]:
        def csrf_token() -> str:
            if "csrf_token" not in session:
                session["csrf_token"] = secrets.token_hex(16)
            return session["csrf_token"]

        return {
            "csrf_token": csrf_token,
            "demo_mode": app.config["DEMO_DATA"],
            "demo_notice": DEMO_NOTICE,
        }

    @app.after_request
    def _security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        )
        return response

    register_routes(app)
    register_error_handlers(app)
    return app


def _form_context(form: dict[str, str] | None = None) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "genres": GENRES,
        "platforms": PLATFORMS,
        "audiences": AUDIENCES,
        "engines": ENGINES,
        "total_saved": count_projects(),
    }
    ctx.update(form or {})
    return ctx


def register_routes(app: Flask) -> None:
    """Attach all routes to ``app``."""

    @app.get("/")
    def index():
        """Render the input form."""
        return render_template("index.html", **_form_context())

    @app.post("/analyze")
    def analyze():
        """Validate input, run the engine, store the report and redirect to it."""
        form = {
            "project_name": request.form.get("project_name", "").strip(),
            "genre": request.form.get("genre", "").strip(),
            "platform": request.form.get("platform", "").strip(),
            "target_audience": request.form.get("target_audience", "").strip(),
            "description": request.form.get("description", "").strip(),
            "engine_choice": request.form.get("engine_choice", "auto").strip() or "auto",
        }

        errors = validate_form(form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("index.html", **_form_context(form)), 400

        try:
            report, used_engine = generate_recommendations(
                title=form["project_name"],
                genre=form["genre"],
                platform=form["platform"],
                audience=form["target_audience"],
                description=form["description"],
                force_engine=form["engine_choice"],
            )
            scripts = report.pop("scripts", {})
            db = get_db()
            cursor = db.execute(
                "INSERT INTO projects (project_name, genre, platform, target_audience, description,"
                " recommendations, generated_scripts) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    form["project_name"], form["genre"], form["platform"], form["target_audience"],
                    form["description"], json.dumps(report), json.dumps(scripts),
                ),
            )
            db.commit()
        except Exception:
            logger.exception("Failed to generate recommendations")
            flash("Something went wrong while generating recommendations. Please try again.", "danger")
            return render_template("index.html", **_form_context(form)), 500

        requested = form["engine_choice"]
        message = f"Analyzed '{form['project_name']}' using the {used_engine.upper()} engine."
        if requested not in ("auto", used_engine):
            message += f" ({requested.upper()} was unavailable, so the offline engine was used.)"
        flash(message, "success")
        return redirect(url_for("results", project_id=cursor.lastrowid))

    @app.get("/results/<int:project_id>")
    def results(project_id: int):
        """Show the stored report."""
        project = _get_project(project_id)
        try:
            recs = json.loads(project["recommendations"])
            scripts = json.loads(project["generated_scripts"])
        except json.JSONDecodeError:
            logger.exception("Corrupt stored report %s", project_id)
            flash("This saved report is corrupted and cannot be displayed.", "danger")
            return redirect(url_for("history"))
        return render_template("results.html", project=project, recs=recs, scripts=scripts)

    @app.get("/history")
    def history():
        """List saved reports with optional text search and genre filter."""
        query = request.args.get("q", "").strip()[:100]
        genre_filter = request.args.get("genre", "").strip()
        db = get_db()

        genres = [r["genre"] for r in db.execute("SELECT DISTINCT genre FROM projects ORDER BY genre")]
        sql = "SELECT id, project_name, genre, platform, target_audience, created_at, description FROM projects WHERE 1=1"
        params: list[Any] = []
        if query:
            sql += " AND (project_name LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\')"
            params += [_like_pattern(query)] * 2
        if genre_filter:
            sql += " AND genre = ?"
            params.append(genre_filter)
        sql += " ORDER BY created_at DESC, id DESC LIMIT ?"
        params.append(HISTORY_LIMIT)

        projects = db.execute(sql, params).fetchall()
        return render_template(
            "history.html", projects=projects, genres=genres, selected_genre=genre_filter, search_query=query
        )

    @app.post("/delete/<int:project_id>")
    def delete_project(project_id: int):
        """Delete one saved report."""
        db = get_db()
        db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        db.commit()
        flash("Recommendation history deleted successfully.", "success")
        return redirect(url_for("history"))

    def _load_export_data(project_id: int):
        project = _get_project(project_id)
        try:
            return project, json.loads(project["recommendations"]), json.loads(project["generated_scripts"])
        except json.JSONDecodeError:
            abort(500, description="Stored report is corrupted.")

    @app.get("/export/<int:project_id>")
    def export_project(project_id: int):
        """Download the report as Markdown."""
        project, recs, scripts = _load_export_data(project_id)
        markdown = build_markdown_report(project, recs, scripts)
        return send_file(
            io.BytesIO(markdown.encode("utf-8")),
            mimetype="text/markdown",
            as_attachment=True,
            download_name=f"{safe_filename(project['project_name'])}_RecommendationReport.md",
        )

    @app.get("/download-zip/<int:project_id>")
    def download_zip(project_id: int):
        """Download the folder layout and C# scripts as a ZIP."""
        project, recs, scripts = _load_export_data(project_id)
        return send_file(
            build_starter_kit(project, recs, scripts),
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{safe_filename(project['project_name'])}_UnityStarterKit.zip",
        )


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(413)
    @app.errorhandler(500)
    def _error(error):
        code = getattr(error, "code", 500)
        titles = {400: "Bad request", 404: "Not found", 413: "Request too large", 500: "Server error"}
        description = error.description if code in (400, 404) else titles.get(code, "Error")
        return render_template("error.html", code=code, title=titles.get(code, "Error"), description=description), code


app = create_app()

if __name__ == "__main__":
    # Local-only by default; set FLASK_DEBUG=1 explicitly for development.
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
