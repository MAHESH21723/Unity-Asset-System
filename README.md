# Unity AI Architect

A Flask web app that turns a game concept into a ready-to-use Unity project plan: recommended assets and packages, a manager/system architecture, a folder structure, compilable C# starter scripts and a four-phase development roadmap.

It works **fully offline** out of the box using a built-in rule-based engine. Optionally, it can call Google Gemini or OpenAI; every AI response is parsed and sanitized before it is stored or displayed.

## Features

- **Concept analysis**: core mechanics, required systems, art needs, monetization and complexity, tailored to genre, platform and audience.
- **Asset recommendations**: Unity packages and Asset Store tools with a rating (Essential, Highly Recommended, Recommended) and a purpose for your game.
- **Architecture and folder layout**: suggested managers and systems, plus a Unity `Assets/` tree.
- **C# starter scripts**: genre-specific scripts (platformer, puzzle, RPG, shooter, generic) that compile in Unity 2021 LTS and later (including Unity 6). Copy or download each script from the results page.
- **Exports**: a Markdown report and a starter-kit ZIP containing the folder layout and scripts in sensible sub-folders.
- **History**: every analysis is saved to SQLite with search, genre filter and delete.
- **Optional AI engines**: Gemini and OpenAI, selected through environment variables, with automatic fallback to the offline engine if a provider is missing or fails.
- **Security basics**: CSRF protection, strict input validation, parameterized SQL, escaped output, a Content-Security-Policy and other security headers, and sanitized AI output (safe file and folder names only).

## Tech stack

- Python 3.10+ (developed on 3.11 to 3.15), Flask 3, SQLite (`sqlite3`)
- Jinja2 templates, Bootstrap 5, Font Awesome, vanilla JavaScript
- pytest for tests
- Optional: `openai` and `google-genai` SDKs

## Live demo

**Live demo: [https://unity-asset-system.onrender.com](https://unity-asset-system.onrender.com)** (free hosting: the first visit after a quiet spell can take up to a minute to wake up)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/MAHESH21723/Unity-Asset-System)

To host your own copy for free:

1. Sign in to [Render](https://render.com) with GitHub.
2. Click the **Deploy to Render** button above.
3. Review the blueprint (`render.yaml`) and click **Apply**.

Free-plan notes: the service sleeps after about 15 minutes idle, so the first request after a pause takes about a minute. The filesystem is ephemeral, so saved reports resets on every restart or redeploy. The demo sets `DEMO_DATA=1`, which shows a "public demo" banner. You need no server or domain of your own, and local use is unchanged (see Setup below).
## Setup

```bash
git clone https://github.com/MAHESH21723/Unity-Asset-System.git
cd Unity-Asset-System

python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# macOS / Linux:         source .venv/bin/activate

pip install -r requirements.txt
```

Optional configuration: copy `.env.example` to `.env` and edit it. Nothing is required; the defaults work.

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Signs sessions and CSRF tokens | random per start |
| `FLASK_DEBUG` | `1` enables the Flask debugger | `0` |
| `HOST`, `PORT` | Bind address for `python app.py` | `127.0.0.1`, `5000` |
| `DATABASE_PATH` | SQLite file (created on startup) | `unity_ai.db` |
| `GEMINI_API_KEY`, `OPENAI_API_KEY` | Enable AI engines | unset (offline) |
| `GEMINI_MODEL`, `OPENAI_MODEL` | Model names | `gemini-2.0-flash`, `gpt-4o-mini` |

To use an AI provider, also run `pip install -r requirements-ai.txt` and set the matching key in `.env`. The AI integrations are optional and not exercised by the test suite (providers are mocked).

## Run

```bash
python app.py
```

Open <http://127.0.0.1:5000>. The database is created automatically on first start.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The suite covers the routes (validation, CSRF, XSS escaping, search and SQL-injection safety, exports, delete), the offline engine, JSON parsing, provider fallback, report sanitizing and the export builders.

## Project structure

```
Unity-Asset-System/
├── app.py                  # Flask app factory, routes, validation, DB helpers
├── exports.py              # Markdown report and starter-kit ZIP builders
├── ai_engine/
│   ├── __init__.py         # Engine selection, prompt building, provider calls, fallback
│   ├── schema.py           # Validation/sanitizing of every report (AI or offline)
│   ├── mock_engine.py      # Offline rule-based engine and genre profiles
│   ├── unity_scripts/      # Real C# starter scripts per genre (.cs files)
│   ├── asset_recommender.py, architecture_generator.py,
│   │   script_generator.py, roadmap_generator.py   # Prompt guideline fragments
├── templates/              # Jinja2 pages (index, results, history, error)
├── static/                 # CSS and JavaScript (no inline scripts)
├── tests/                  # pytest suite
├── requirements*.txt       # Runtime, optional AI, and dev dependencies
└── .env.example            # Documented configuration template
```

## Author

Created by **Maheshwaran** ([@MAHESH21723](https://github.com/MAHESH21723), kmaheshwaran9965@gmail.com).

## License

Released under the [MIT License](LICENSE).
