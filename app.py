import os
import json
import sqlite3
import io
import zipfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from dotenv import load_dotenv

# Import the recommendation logic
from ai_engine import generate_recommendations

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "unity_asset_recommender_secure_key_12345")
DATABASE = 'unity_ai.db'

def get_db():
    """Returns a connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it doesn't exist."""
    with get_db() as conn:
        conn.execute("""
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
        """)
        conn.commit()

# Initialize Database on startup
init_db()

@app.route('/')
def index():
    """Renders the main recommendation input form page."""
    # Count total recommendations saved
    try:
        with get_db() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()
            total_saved = row['count'] if row else 0
    except Exception:
        total_saved = 0
        
    return render_template('index.html', total_saved=total_saved)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Validates form input, triggers recommendation AI engine, and saves to database."""
    # Form data extraction
    project_name = request.form.get('project_name', '').strip()
    genre = request.form.get('genre', '').strip()
    platform = request.form.get('platform', '').strip()
    target_audience = request.form.get('target_audience', '').strip()
    description = request.form.get('description', '').strip()
    engine_choice = request.form.get('engine_choice', 'auto').strip()

    # Input Validation
    errors = []
    if not project_name:
        errors.append("Project Name (Game Title) is required.")
    elif len(project_name) > 100:
        errors.append("Project Name must be 100 characters or less.")
        
    if not genre:
        errors.append("Genre selection is required.")
        
    if not platform:
        errors.append("Platform selection is required.")
        
    if not target_audience:
        errors.append("Target Audience selection is required.")
        
    if not description:
        errors.append("Game Description is required.")
    elif len(description) < 20:
        errors.append("Game Description should be at least 20 characters to allow meaningful analysis.")
    elif len(description) > 2000:
        errors.append("Game Description must be 2000 characters or less.")

    if errors:
        for error in errors:
            flash(error, "danger")
        try:
            with get_db() as conn:
                row = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()
                total_saved = row['count'] if row else 0
        except Exception:
            total_saved = 0
        return render_template('index.html', 
                               project_name=project_name, 
                               genre=genre, 
                               platform=platform, 
                               target_audience=target_audience, 
                               description=description,
                               total_saved=total_saved)

    try:
        # Call AI Engine
        recommendations, used_engine = generate_recommendations(
            title=project_name,
            genre=genre,
            platform=platform,
            audience=target_audience,
            description=description,
            force_engine=engine_choice
        )
        
        # Extract C# scripts from generated content
        scripts = recommendations.get("scripts", {})
        # Remove raw script block from main recommendations data to keep it tidy
        recommendations_no_scripts = recommendations.copy()
        if "scripts" in recommendations_no_scripts:
            del recommendations_no_scripts["scripts"]

        # Save to SQLite Database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (project_name, genre, platform, target_audience, description, recommendations, generated_scripts)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                project_name,
                genre,
                platform,
                target_audience,
                description,
                json.dumps(recommendations_no_scripts),
                json.dumps(scripts)
            ))
            conn.commit()
            project_id = cursor.lastrowid
            
        flash(f"Successfully analyzed '{project_name}' using {used_engine.upper()}!", "success")
        return redirect(url_for('results', project_id=project_id))
        
    except Exception as e:
        flash(f"Failed to generate recommendations: {str(e)}", "danger")
        return render_template('index.html', 
                               project_name=project_name, 
                               genre=genre, 
                               platform=platform, 
                               target_audience=target_audience, 
                               description=description)

@app.route('/results/<int:project_id>')
def results(project_id):
    """Loads a recommendation from the database and renders the results dashboard."""
    try:
        with get_db() as conn:
            project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            
        if not project:
            flash("Project recommendations not found.", "warning")
            return redirect(url_for('index'))
            
        recommendations = json.loads(project['recommendations'])
        generated_scripts = json.loads(project['generated_scripts'])
        
        return render_template('results.html', 
                               project=project, 
                               recs=recommendations, 
                               scripts=generated_scripts)
    except Exception as e:
        flash(f"Error loading results: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/history')
def history():
    """Displays a list of past recommendation requests with search and genre filters."""
    query = request.args.get('q', '').strip()
    genre_filter = request.args.get('genre', '').strip()
    
    try:
        with get_db() as conn:
            # Get unique genres in DB for filtering dropdown
            genres_rows = conn.execute("SELECT DISTINCT genre FROM projects ORDER BY genre ASC").fetchall()
            genres = [r['genre'] for r in genres_rows]
            
            # Formulate SQL query
            sql = "SELECT id, project_name, genre, platform, target_audience, created_at, description FROM projects WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (project_name LIKE ? OR description LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
                
            if genre_filter:
                sql += " AND genre = ?"
                params.append(genre_filter)
                
            sql += " ORDER BY created_at DESC"
            
            projects = conn.execute(sql, params).fetchall()
            
        return render_template('history.html', 
                               projects=projects, 
                               genres=genres, 
                               selected_genre=genre_filter, 
                               search_query=query)
    except Exception as e:
        flash(f"Error loading history: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    """Deletes a recommendation history item from the database."""
    try:
        with get_db() as conn:
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
        flash("Recommendation history deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting history: {str(e)}", "danger")
        
    return redirect(url_for('history'))

@app.route('/export/<int:project_id>')
def export_project(project_id):
    """Exports the recommended details into a clean markdown document."""
    try:
        with get_db() as conn:
            project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            
        if not project:
            return "Project not found", 404
            
        recs = json.loads(project['recommendations'])
        scripts = json.loads(project['generated_scripts'])
        
        # Formulate Markdown string
        md = f"""# Unity Asset Recommendation Report: {project['project_name']}
Generated on: {project['created_at']}

## 1. Project Specifications
- **Genre:** {project['genre']}
- **Platform:** {project['platform']}
- **Target Audience:** {project['target_audience']}
- **Description:** {project['description']}

## 2. Project Analysis
- **Complexity:** {recs.get('analysis', {}).get('complexity', 'N/A')}
- **Art Requirements:** {recs.get('analysis', {}).get('art_requirements', 'N/A')}
- **Monetization:** {recs.get('analysis', {}).get('monetization', 'N/A')}
- **Core Mechanics:**
"""
        for mech in recs.get('analysis', {}).get('mechanics', []):
            md += f"  - {mech}\n"
        md += "\n- **Required Systems:**\n"
        for sys in recs.get('analysis', {}).get('required_systems', []):
            md += f"  - {sys}\n"
            
        md += "\n## 3. Recommended Unity Assets\n"
        for asset in recs.get('assets', []):
            md += f"### {asset.get('name')} ({asset.get('rating')})\n"
            md += f"- **Category:** {asset.get('category')}\n"
            md += f"- **Purpose:** {asset.get('purpose')}\n\n"
            
        md += "## 4. Suggested Software Architecture\n"
        md += "### Recommended Managers\n"
        for manager in recs.get('architecture', {}).get('managers', []):
            md += f"- **{manager.get('name')}:** {manager.get('purpose')}\n"
        md += "\n### Recommended Systems\n"
        for sys in recs.get('architecture', {}).get('systems', []):
            md += f"- **{sys.get('name')}:** {sys.get('purpose')}\n"
            
        md += "\n## 5. Suggested Folder Structure\n"
        
        def format_tree(node, depth=0):
            tree_str = ""
            if isinstance(node, dict):
                for k, v in node.items():
                    tree_str += "  " * depth + f"├── {k}\n"
                    tree_str += format_tree(v, depth + 1)
            return tree_str
            
        md += "```\n" + format_tree(recs.get('folder_structure', {})) + "```\n\n"
        
        md += "## 6. Development Roadmap\n"
        for phase in recs.get('roadmap', {}).get('phases', []):
            md += f"### {phase.get('title')} (Duration: {phase.get('duration')})\n"
            for t in phase.get('tasks', []):
                md += f"- [ ] {t}\n"
            md += "\n"
            
        md += "## 7. Starter C# Scripts\n"
        for fn, code in scripts.items():
            md += f"### File: {fn}\n"
            md += f"```csharp\n{code}\n```\n\n"
            
        safe_name = "".join(x for x in project['project_name'] if x.isalnum() or x in " -_").strip().replace(" ", "_")
        if not safe_name:
            safe_name = "Unity_Project"
            
        return send_file(
            io.BytesIO(md.encode('utf-8')),
            mimetype='text/markdown',
            as_attachment=True,
            download_name=f"{safe_name}_RecommendationReport.md"
        )
    except Exception as e:
        return f"Error exporting report: {str(e)}", 500

@app.route('/download-zip/<int:project_id>')
def download_zip(project_id):
    """Generates a zip file mapping the recommended folder structure and C# starter scripts."""
    try:
        with get_db() as conn:
            project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            
        if not project:
            return "Project not found", 404
            
        recs = json.loads(project['recommendations'])
        scripts = json.loads(project['generated_scripts'])
        
        # Create ZIP in-memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # Recursive directory builder
            paths = []
            def collect_paths(node, current_path=""):
                if not isinstance(node, dict) or not node:
                    paths.append(current_path)
                    return
                for key, val in node.items():
                    new_path = f"{current_path}/{key}" if current_path else key
                    collect_paths(val, new_path)
                    
            folder_tree = recs.get("folder_structure", {})
            if not folder_tree:
                # Default safety folder structure
                folder_tree = {
                    "Assets": {
                        "Art": {},
                        "Audio": {},
                        "Prefabs": {},
                        "Scenes": {},
                        "Scripts": {
                            "Managers": {},
                            "Systems": {},
                            "Gameplay": {},
                            "UI": {}
                        }
                    }
                }
            
            collect_paths(folder_tree)
            
            # Write folder .keep files
            for p in paths:
                zip_dir_path = p.strip("/") + "/"
                zipf.writestr(zip_dir_path + ".keep", "This placeholder keeps the empty folder structure intact in Unity.")
                
            # Write Scripts in their appropriate subfolders
            for filename, content in scripts.items():
                subfolder = "Assets/Scripts"
                filename_lower = filename.lower()
                
                # Intelligent folder placing
                if "manager" in filename_lower:
                    subfolder = "Assets/Scripts/Managers"
                elif "system" in filename_lower or "save" in filename_lower or "load" in filename_lower:
                    subfolder = "Assets/Scripts/Systems"
                elif "controller" in filename_lower or "movement" in filename_lower or "character" in filename_lower:
                    subfolder = "Assets/Scripts/Gameplay"
                elif "ui" in filename_lower or "menu" in filename_lower or "canvas" in filename_lower:
                    subfolder = "Assets/Scripts/UI"
                    
                full_path = f"{subfolder}/{filename}"
                zipf.writestr(full_path, content)
                
            # Create a Project Readme
            readme = f"""# Unity Starter Kit: {project['project_name']}
--------------------------------------------------
This Unity Assets Starter Kit was automatically generated using the AI-Powered Unity Asset Recommendation System.

## Project Details:
- Game Title: {project['project_name']}
- Genre: {project['genre']}
- Platform: {project['platform']}
- Target Audience: {project['target_audience']}

## Guidelines:
1. Extract the contents of this ZIP file.
2. Drag and drop the complete 'Assets' folder structure directly into your Unity Project window (replacing or merging with your existing Assets directory).
3. Open scripts inside Assets/Scripts/ and adjust inspector fields or reference hooks.

Generated on: {project['created_at']}
"""
            zipf.writestr("Assets/README_StarterKit.txt", readme)
            
        memory_file.seek(0)
        
        safe_name = "".join(x for x in project['project_name'] if x.isalnum() or x in " -_").strip().replace(" ", "_")
        if not safe_name:
            safe_name = "Unity_Project"
            
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{safe_name}_UnityStarterKit.zip"
        )
    except Exception as e:
        return f"Error downloading starter kit: {str(e)}", 500

if __name__ == '__main__':
    # Default Flask port
    app.run(host='0.0.0.0', port=5000, debug=True)
