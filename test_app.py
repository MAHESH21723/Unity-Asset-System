import unittest
import os
import json
import sqlite3
import zipfile
import io
from app import app, get_db, DATABASE

class UnityAssetSystemTests(unittest.TestCase):

    def setUp(self):
        """Sets up the Flask test client and configures temporary database settings."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # Ensure database is initialized
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

    def test_mock_engine(self):
        """Verifies that the mock generator outputs valid, structured schemas for different genres."""
        from ai_engine.mock_engine import generate_mock_data
        
        # Test Puzzle genre
        puzzle_data = generate_mock_data(
            title="Slide Box",
            genre="Puzzle",
            platform="Android",
            audience="Casual",
            description="Slide boxes to match their targets in a grid."
        )
        
        # Check primary dictionary fields
        self.assertIn("analysis", puzzle_data)
        self.assertIn("assets", puzzle_data)
        self.assertIn("architecture", puzzle_data)
        self.assertIn("folder_structure", puzzle_data)
        self.assertIn("roadmap", puzzle_data)
        self.assertIn("scripts", puzzle_data)
        
        # Verify script contents
        self.assertIn("GridManager.cs", puzzle_data["scripts"])
        self.assertIn("GameManager.cs", puzzle_data["scripts"])
        
        # Test Platformer genre
        plat_data = generate_mock_data(
            title="Mario Clone",
            genre="Platformer",
            platform="PC",
            audience="Core",
            description="Jump on platforms and collect golden coins."
        )
        self.assertIn("PlayerController.cs", plat_data["scripts"])
        self.assertIn("GameManager.cs", plat_data["scripts"])

    def test_index_route(self):
        """Verifies the index page returns successfully."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unity AI Architect", response.data)

    def test_history_route(self):
        """Verifies the history page loads and filters successfully."""
        response = self.app.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Recommendation History", response.data)

    def test_validation_failures(self):
        """Verifies backend validations for empty and too-short inputs."""
        # Missing title
        response = self.app.post('/analyze', data={
            'project_name': '',
            'genre': 'Puzzle',
            'platform': 'PC',
            'target_audience': 'Casual',
            'description': 'A valid long description for checking details.',
            'engine_choice': 'mock'
        }, follow_redirects=True)
        self.assertIn(b"Project Name (Game Title) is required.", response.data)
        
        # Description too short
        response = self.app.post('/analyze', data={
            'project_name': 'Valid Title',
            'genre': 'Puzzle',
            'platform': 'PC',
            'target_audience': 'Casual',
            'description': 'Short',
            'engine_choice': 'mock'
        }, follow_redirects=True)
        self.assertIn(b"Game Description should be at least 20 characters", response.data)

    def test_successful_analysis_and_exports(self):
        """Submits a valid request, checks DB storage, verifies Results view, Markdown export, and ZIP generation."""
        response = self.app.post('/analyze', data={
            'project_name': 'Test Runner Game',
            'genre': 'Platformer',
            'platform': 'PC',
            'target_audience': 'Core',
            'description': 'An endless runner game with procedurally generated obstacles and jumping mechanics.',
            'engine_choice': 'mock'
        }, follow_redirects=False)
        
        # Check redirection to results page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith('/results/'))
        
        # Extract project ID
        project_id = response.location.split('/')[-1]
        
        # Fetch results page
        results_resp = self.app.get(f'/results/{project_id}')
        self.assertEqual(results_resp.status_code, 200)
        self.assertIn(b"Test Runner Game", results_resp.data)
        self.assertIn(b"PlayerController.cs", results_resp.data)
        
        # Fetch Markdown export
        export_resp = self.app.get(f'/export/{project_id}')
        self.assertEqual(export_resp.status_code, 200)
        self.assertEqual(export_resp.mimetype, 'text/markdown')
        self.assertIn(b"# Unity Asset Recommendation Report: Test Runner Game", export_resp.data)
        
        # Fetch ZIP export
        zip_resp = self.app.get(f'/download-zip/{project_id}')
        self.assertEqual(zip_resp.status_code, 200)
        self.assertEqual(zip_resp.mimetype, 'application/zip')
        
        # Read ZIP contents in-memory
        with zipfile.ZipFile(io.BytesIO(zip_resp.data)) as zip_file:
            filenames = zip_file.namelist()
            # Verify file architecture placeholders inside ZIP
            self.assertTrue(any(f.startswith("Assets/Art/") for f in filenames))
            self.assertTrue(any(f.startswith("Assets/Scripts/Managers/GameManager.cs") for f in filenames))
            self.assertTrue(any(f.startswith("Assets/Scripts/Gameplay/PlayerController.cs") for f in filenames))
            self.assertIn("Assets/README_StarterKit.txt", filenames)

        # Delete history item
        delete_resp = self.app.post(f'/delete/{project_id}', follow_redirects=True)
        self.assertEqual(delete_resp.status_code, 200)
        self.assertIn(b"Recommendation history deleted successfully.", delete_resp.data)

if __name__ == '__main__':
    unittest.main()
