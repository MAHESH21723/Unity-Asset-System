import os
import json
import re
from dotenv import load_dotenv

# Import prompt segments
from ai_engine.asset_recommender import get_asset_prompt_guidelines
from ai_engine.architecture_generator import get_architecture_prompt_guidelines
from ai_engine.script_generator import get_script_prompt_guidelines
from ai_engine.roadmap_generator import get_roadmap_prompt_guidelines
from ai_engine.mock_engine import generate_mock_data

# Load env variables
load_dotenv()

def clean_json_response(raw_text):
    """
    Cleans raw text from LLM response to extract and parse JSON object safely.
    """
    raw_text = raw_text.strip()
    
    # Try direct parse
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass
        
    # Find JSON block using regex (```json ... ``` or ``` ... ```)
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
            
    # Try finding first '{' and last '}'
    first_brace = raw_text.find('{')
    last_brace = raw_text.rfind('}')
    if first_brace != -1 and last_brace != -1:
        try:
            return json.loads(raw_text[first_brace:last_brace+1])
        except json.JSONDecodeError:
            pass
            
    raise ValueError("Failed to parse valid JSON from AI response. Raw response: " + raw_text[:300])

def generate_recommendations(title, genre, platform, audience, description, force_engine=None):
    """
    Core function that chooses the engine (Gemini, OpenAI, or Mock Fallback) and runs the recommendation query.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Force mock mode or decide dynamically
    engine = "mock"
    if force_engine == "mock":
        engine = "mock"
    elif force_engine == "gemini" and gemini_key:
        engine = "gemini"
    elif force_engine == "openai" and openai_key:
        engine = "openai"
    else:
        # Auto-detect
        if gemini_key:
            engine = "gemini"
        elif openai_key:
            engine = "openai"
            
    if engine == "mock":
        print("Using Mock/Demo Mode (No API keys found or forced).")
        return generate_mock_data(title, genre, platform, audience, description), "mock"
        
    # Build prompt
    prompt = f"""
You are an expert AI game design assistant and Unity developer.
Analyze the following game concept and generate a Unity asset and architecture recommendations report.

Game Specifications:
- Title: {title}
- Genre: {genre}
- Platform: {platform}
- Target Audience: {audience}
- Description: {description}

You must return the response as a single, valid JSON object containing all the analyzed modules.
JSON Schema structure:
{{
  "analysis": {{
    "genre": "{genre}",
    "mechanics": ["Core mechanic 1", "Core mechanic 2", "etc."],
    "required_systems": ["Required sub-system 1", "Required sub-system 2", "etc."],
    "art_requirements": "Specific summary of art/asset styling needed.",
    "monetization": "Tailored monetization suggestion.",
    "complexity": "Low, Medium, or High based on platform and genre."
  }},
  "assets": [
    {{
      "name": "Asset Name",
      "purpose": "Detailed explanation of why it is needed for this specific game concept.",
      "rating": "Essential, Highly Recommended, or Recommended.",
      "category": "e.g. Animation, Camera, UI, Input, Audio, Utility"
    }}
  ],
  "architecture": {{
    "managers": [
      {{
        "name": "GameManager or similar",
        "purpose": "Specific role of this script/manager in this game."
      }}
    ],
    "systems": [
      {{
        "name": "SaveSystem or similar",
        "purpose": "Explain how this system supports the game logic."
      }}
    ]
  }},
  "folder_structure": {{
    "Assets": {{
      "Art": {{}},
      "Audio": {{}},
      "Scripts": {{
        "Managers": {{}},
        "Systems": {{}}
      }}
    }}
  }},
  "roadmap": {{
    "phases": [
      {{
        "title": "Phase 1: Project Setup",
        "duration": "Estimated time (e.g. 1 Day)",
        "tasks": ["Create folders", "Import packages"]
      }}
    ]
  }},
  "scripts": {{
    "GameManager.cs": "// C# class template with singleton, comments and standard Unity methods",
    "PlayerController.cs": "// C# controller template tailored for this game concept"
  }}
}}

Ensure that:
1. The output is strictly valid JSON. Do not write text before or after the JSON.
2. The scripts generated in the "scripts" section are functional C# starter code for Unity. Provide 2 or 3 scripts (e.g. GameManager.cs and PlayerController.cs or LevelManager.cs) that are relevant to this genre and title. Use comments and clean templates. Do not use placeholders or write pseudocode.

Specific module instructions:
{get_asset_prompt_guidelines()}
{get_architecture_prompt_guidelines()}
{get_script_prompt_guidelines()}
{get_roadmap_prompt_guidelines()}
"""

    if engine == "gemini":
        print("Invoking Gemini API...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            parsed_data = clean_json_response(response.text)
            return parsed_data, "gemini"
        except Exception as e:
            print(f"Gemini API failure: {e}. Falling back to Mock mode.")
            return generate_mock_data(title, genre, platform, audience, description), "mock"
            
    elif engine == "openai":
        print("Invoking OpenAI API...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            parsed_data = clean_json_response(response.choices[0].message.content)
            return parsed_data, "openai"
        except Exception as e:
            print(f"OpenAI API failure: {e}. Falling back to Mock mode.")
            return generate_mock_data(title, genre, platform, audience, description), "mock"
            
    return generate_mock_data(title, genre, platform, audience, description), "mock"
