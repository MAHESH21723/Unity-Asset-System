"""Offline, rule-based recommendation engine.

This engine needs no network access or API key. It maps the chosen genre,
platform and audience to curated recommendations and ships real, compilable
Unity C# starter scripts (stored as ``.cs`` files in ``unity_scripts/``).
"""

from __future__ import annotations

import copy
from functools import lru_cache
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).parent / "unity_scripts"

DEFAULT_FOLDER_STRUCTURE: dict[str, Any] = {
    "Assets": {
        "Art": {"Sprites": {}, "Textures": {}, "Models": {}},
        "Audio": {"Music": {}, "SFX": {}},
        "Animations": {},
        "Materials": {},
        "Prefabs": {},
        "Scenes": {},
        "Scripts": {
            "Managers": {},
            "Systems": {},
            "UI": {},
            "Gameplay": {},
            "Utilities": {},
        },
        "Resources": {},
        "Settings": {},
    }
}


def _asset(name: str, purpose: str, rating: str, category: str) -> dict[str, str]:
    return {"name": name, "purpose": purpose, "rating": rating, "category": category}


def _role(name: str, purpose: str) -> dict[str, str]:
    return {"name": name, "purpose": purpose}


# Each profile describes one genre family. "folder" is the sub-directory of
# unity_scripts/ holding that genre's starter scripts.
GENRE_PROFILES: dict[str, dict[str, Any]] = {
    "platformer": {
        "folder": "platformer",
        "mechanics": [
            "Running & jumping physics",
            "Collectible items",
            "Obstacles and hazards",
            "Level transitions",
        ],
        "required_systems": [
            "Physics-based input handling",
            "Score & level progress tracking",
            "Camera follow (Cinemachine)",
        ],
        "assets": [
            _asset("Cinemachine", "Camera tracking and smooth screen shake", "Highly Recommended", "Camera"),
            _asset("DOTween (Demigiant)", "Smooth animation for UI, platforms and collectibles", "Highly Recommended", "Animation"),
            _asset("TextMeshPro", "Crisp text rendering for the HUD and score display", "Essential", "UI"),
            _asset("Corgi Engine", "Complete 2D/3D platformer controller framework (paid)", "Recommended", "Framework"),
            _asset("FMOD for Unity", "Interactive audio and dynamic music", "Recommended", "Audio"),
        ],
        "managers": [
            _role("GameManager", "Owns game state (Menu, Playing, GameOver, Paused), score and lives."),
            _role("LevelManager", "Controls level loading, spawn points and progression."),
            _role("UIManager", "Updates the coin counter, lives and pause menu."),
            _role("AudioManager", "Plays music and triggers jump/collect/death sound effects."),
        ],
        "systems": [
            _role("PlayerInputController", "Translates input into character motion actions."),
            _role("SaveSystem", "Persists unlocked levels and high scores via JSON or PlayerPrefs."),
            _role("CollectibleSystem", "Handles pickup triggers and scoring."),
        ],
    },
    "puzzle": {
        "folder": "puzzle",
        "mechanics": [
            "Grid configuration and matching",
            "Mechanism triggers",
            "Move limits and timers",
            "Unlockable levels",
        ],
        "required_systems": [
            "Grid alignment system",
            "Touch/gesture handling",
            "Progression & save system",
        ],
        "assets": [
            _asset("DOTween (Demigiant)", "Smooth board sliding, match pops and scale effects", "Highly Recommended", "Animation"),
            _asset("Lean Touch", "Robust gesture detection (swipes, pinches, multi-tap)", "Highly Recommended", "Input"),
            _asset("TextMeshPro", "Sharp numbers and text on puzzle tiles", "Essential", "UI"),
            _asset("Shapes", "Vector graphics for crisp puzzle elements without textures (paid)", "Recommended", "Graphics"),
        ],
        "managers": [
            _role("GameManager", "Manages game phases, victory checks and level loading."),
            _role("GridManager", "Generates boards, tracks tile state and triggers match logic."),
            _role("UIManager", "Shows stars, remaining moves, victory panels and level select."),
        ],
        "systems": [
            _role("PuzzleSolver", "Validates matches and detects deadlocked boards."),
            _role("SaveSystem", "Stores level completion metrics (stars, moves) in PlayerPrefs or JSON."),
        ],
    },
    "rpg": {
        "folder": "rpg",
        "mechanics": ["Combat systems", "Stat progression", "Dialogue trees", "Inventory system"],
        "required_systems": ["Inventory management", "Quest tracker", "Save & load", "Dialogue system"],
        "assets": [
            _asset("A* Pathfinding Project", "Fast pathfinding for companions and enemy AI", "Highly Recommended", "AI/Pathfinding"),
            _asset("Ink (Inkle)", "Scripting language for branching dialogue", "Highly Recommended", "Dialogue"),
            _asset("Odin Inspector", "Custom inspectors for database-heavy item stats (paid)", "Recommended", "Editor Utility"),
            _asset("Cinemachine", "Third-person follow cameras and dialogue zooms", "Essential", "Camera"),
        ],
        "managers": [
            _role("GameManager", "Owns the overall game loop, state preservation and scene navigation."),
            _role("InventoryManager", "Tracks items, slot limits and item usage."),
            _role("QuestManager", "Handles quest states (Active, Inactive, Completed) and rewards."),
            _role("DialogueManager", "Displays dialogue and choices parsed from Ink files."),
        ],
        "systems": [
            _role("StatsSystem", "Computes health, damage and armor from level and equipment."),
            _role("SaveSystem", "Serializes quest, inventory and location state to a save file."),
        ],
    },
    "shooter": {
        "folder": "shooter",
        "mechanics": ["Aiming and firing", "Projectile damage", "Enemy waves", "Pickups and power-ups"],
        "required_systems": ["Weapon system", "Health & damage system", "Enemy spawner", "Object pooling"],
        "assets": [
            _asset("Cinemachine", "Dynamic follow camera with impulse-based screen shake", "Highly Recommended", "Camera"),
            _asset("Input System (package)", "Rebindable keyboard, mouse and gamepad controls", "Highly Recommended", "Input"),
            _asset("TextMeshPro", "Ammo, score and health readouts", "Essential", "UI"),
            _asset("Post Processing / URP Volumes", "Hit flashes, bloom and screen effects", "Recommended", "Graphics"),
        ],
        "managers": [
            _role("GameManager", "Owns match state, score and restart flow."),
            _role("EnemySpawner", "Spawns waves of enemies and scales difficulty."),
            _role("UIManager", "Updates the HUD (health, ammo, score) and game-over screen."),
            _role("AudioManager", "Plays weapon, hit and ambience audio."),
        ],
        "systems": [
            _role("WeaponSystem", "Controls fire rate, projectile spawning and ammo."),
            _role("HealthSystem", "Applies damage and raises death events for players and enemies."),
            _role("PoolingSystem", "Reuses projectile objects to avoid garbage-collection spikes."),
        ],
    },
    "generic": {
        "folder": "generic",
        "mechanics": ["Core gameplay state loop", "User input actions", "Trigger boundaries and collisions"],
        "required_systems": ["Input management", "Application state", "UI & menu system"],
        "assets": [
            _asset("TextMeshPro", "High-quality text rendering across the game", "Essential", "UI"),
            _asset("DOTween (Demigiant)", "Procedural tweening for items and panels", "Highly Recommended", "Animation"),
            _asset("Addressables", "Scalable local and remote asset management", "Recommended", "Assets"),
        ],
        "managers": [
            _role("GameManager", "Coordinates the game loop, scores and system states."),
            _role("UIManager", "Manages screens, the HUD and panel transitions."),
        ],
        "systems": [
            _role("SaveSystem", "Loads and saves game stats and settings."),
            _role("InputSystem", "Interprets keyboard, gamepad or touch input."),
        ],
    },
}

# Maps a keyword found in the genre name to a profile key.
_GENRE_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("platformer", "platformer"),
    ("puzzle", "puzzle"),
    ("rpg", "rpg"),
    ("shooter", "shooter"),
)


@lru_cache(maxsize=None)
def _read_scripts(folder: str) -> dict[str, str]:
    """Load every ``.cs`` file in ``unity_scripts/<folder>`` (cached)."""
    directory = SCRIPTS_DIR / folder
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(directory.glob("*.cs"))}


def profile_key_for(genre: str) -> str:
    """Return the profile key (``platformer``, ``puzzle``...) for a genre label."""
    genre_lower = genre.lower()
    for keyword, key in _GENRE_KEYWORDS:
        if keyword in genre_lower:
            return key
    return "generic"


def _build_roadmap(platform: str) -> dict[str, Any]:
    return {
        "phases": [
            {
                "title": "Phase 1: Project Setup & Package Imports",
                "duration": "1-2 Days",
                "tasks": [
                    "Configure Unity project settings and the target platform.",
                    "Import TextMeshPro, the Input System and the recommended assets.",
                    "Create the recommended folder layout.",
                    "Create base scenes: Bootstrap, MainMenu and Level01.",
                ],
            },
            {
                "title": "Phase 2: Core Gameplay Mechanics",
                "duration": "3-5 Days",
                "tasks": [
                    "Add the starter scripts and wire them to characters or levels.",
                    "Configure controls and map inputs.",
                    "Build basic UI mockups and bind them to manager state.",
                    "Block out level segments or puzzle structures.",
                ],
            },
            {
                "title": "Phase 3: Systems Integration & Polish",
                "duration": "2-3 Days",
                "tasks": [
                    "Implement save/load for preferences and progress.",
                    "Add sound effects and background music triggers.",
                    "Polish with DOTween animations and camera transitions.",
                    "Fix gameplay-loop bugs and verify scene transitions.",
                ],
            },
            {
                "title": "Phase 4: Optimization & Deployment Settings",
                "duration": "2 Days",
                "tasks": [
                    f"Profile CPU/GPU and memory against the {platform} target.",
                    "Compress textures and tune quality settings.",
                    "Run a development build on a real device or standalone player.",
                    "Prepare store listing text, screenshots and icons.",
                ],
            },
        ]
    }


def generate_mock_data(
    title: str,
    genre: str,
    platform: str,
    audience: str,
    description: str,
) -> dict[str, Any]:
    """Build a full recommendation report without any external service.

    Args:
        title: Game title (used only for context; output is genre driven).
        genre: Genre label such as ``"Platformer"`` or ``"RPG"``.
        platform: Target platform such as ``"PC"`` or ``"Android"``.
        audience: Target audience such as ``"Kids"`` or ``"Core"``.
        description: Free-form game description.

    Returns:
        A dict with ``analysis``, ``assets``, ``architecture``,
        ``folder_structure``, ``roadmap`` and ``scripts`` keys.
    """
    profile = GENRE_PROFILES[profile_key_for(genre)]
    platform_lower = platform.lower()
    audience_lower = audience.lower()

    complexity = "Medium"
    art = "Stylized 2D sprites and clean UI elements."
    if platform_lower in ("android", "ios"):
        complexity = "Low to Medium"
        art = "Optimized low-poly 3D models or 2D sprites suited for mobile screens."
    elif platform_lower in ("vr/ar", "console"):
        complexity = "High"
        art = "High-fidelity assets, optimized shaders and immersive UI."

    monetization = "Premium purchase"
    if "casual" in audience_lower or "kids" in audience_lower:
        monetization = "In-app purchases (cosmetics) and ad-supported"

    return {
        "analysis": {
            "genre": genre,
            "mechanics": list(profile["mechanics"]),
            "required_systems": list(profile["required_systems"]),
            "art_requirements": art,
            "monetization": monetization,
            "complexity": complexity,
        },
        "assets": copy.deepcopy(profile["assets"]),
        "architecture": {
            "managers": copy.deepcopy(profile["managers"]),
            "systems": copy.deepcopy(profile["systems"]),
        },
        "folder_structure": copy.deepcopy(DEFAULT_FOLDER_STRUCTURE),
        "roadmap": _build_roadmap(platform),
        "scripts": dict(_read_scripts(profile["folder"])),
    }
