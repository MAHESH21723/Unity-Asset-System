# AI-Powered Unity Asset Recommendation System

A web-based AI assistant built with Python Flask and OpenAI / Gemini APIs to accelerate game prototyping for Unity developers. The system analyzes a developer's game concept, genre, platform, and target audience, generating tailored assets, software architecture systems, directory templates, starter C# scripts, and phase roadmaps.

---

## Key Features

1. **AI Processing Engine**: Automatically extracts genre mechanics, complexity, art guidelines, and monetization plans using structured prompt templates.
2. **Unified API Selection**: Integrates both OpenAI (`GPT-4o-mini`) and Gemini (`Gemini 1.5 Flash`) SDKs with auto-detection.
3. **Interactive Mock Mode**: Fallback engine that generates realistic recommendations offline or if no API keys are provided.
4. **Starter C# Code Generator**: Generates 2-3 custom starter scripts (e.g. `GameManager.cs`, `PlayerController.cs`) relevant to the game's genre.
5. **Project Starter Kit ZIP Exporter**: Compiles scripts and creates the suggested directory layout matching Unity's folder hierarchy with `.keep` placeholders in a downloadable ZIP.
6. **Markdown Exporter**: Generates a clean, detailed developer report file (.md) of the recommendation.
7. **SQLite History Dashboard**: Persists prior submissions with full text-search and genre filter options.

---

## Technology Stack

- **Backend**: Python 3.11+, Flask Web Server, SQLite (database storage)
- **AI Services**: OpenAI API, Google Gemini API, dotenv variables config
- **Frontend**: HTML5, CSS3, Bootstrap 5, FontAwesome, custom interactive JS script

---

## Installation & Setup

1. **Clone the project & install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   # Flask configuration
   SECRET_KEY=unity_asset_recommender_secure_key_12345

   # AI API Keys (Optional - falls back to Mock Mode if empty)
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the Server**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://localhost:5000`.

---

## Project Structure

```
UnityAssetRecommendationSystem/
│
├── app.py                     # Main Flask router and export logic
├── requirements.txt           # Python library requirements
├── unity_ai.db                # SQLite database (auto-generated)
├── .env                       # Environment variables config
│
├── ai_engine/                 # AI processing backend
│   ├── __init__.py            # API coordinator and parser
│   ├── asset_recommender.py   # Asset prompt definitions
│   ├── architecture_generator.py # Manager, system & folder prompts
│   ├── script_generator.py    # Starter C# script guidelines
│   ├── roadmap_generator.py   # Development timeline prompts
│   └── mock_engine.py         # Dynamic offline mock generator
│
├── templates/                 # Frontend pages
│   ├── base.html              # Core layout and CSS imports
│   ├── index.html             # Parameter form & load screens
│   ├── results.html           # Project output tabs dashboard
│   └── history.html           # Previous recommendations list
│
└── static/                    # Static UI resources
    ├── css/
    │   └── style.css          # Color scheme, fonts & layout styles
    └── js/
        └── main.js            # Input, loader and tabs scripts
```
