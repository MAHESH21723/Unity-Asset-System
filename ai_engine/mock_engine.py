import datetime

def generate_mock_data(title, genre, platform, audience, description):
    """
    Generates detailed mock recommendations based on the user's input.
    Provides extremely realistic output for Unity assets, architectures, C# starter code,
    and roadmaps based on the chosen genre and platform.
    """
    genre_lower = genre.lower()
    platform_lower = platform.lower()
    
    # 1. Base Structure of output
    data = {
        "analysis": {
            "genre": genre,
            "mechanics": [],
            "required_systems": [],
            "art_requirements": "",
            "monetization": "",
            "complexity": "Medium"
        },
        "assets": [],
        "architecture": {
            "managers": [],
            "systems": []
        },
        "folder_structure": {
            "Assets": {
                "Art": {
                    "Sprites": {},
                    "Textures": {},
                    "Models": {}
                },
                "Audio": {
                    "Music": {},
                    "SFX": {}
                },
                "Animations": {},
                "Materials": {},
                "Prefabs": {},
                "Scenes": {},
                "Scripts": {
                    "Managers": {},
                    "Systems": {},
                    "UI": {},
                    "Gameplay": {},
                    "Utilities": {}
                },
                "Resources": {},
                "Settings": {}
            }
        },
        "roadmap": {
            "phases": []
        },
        "scripts": {}
    }
    
    # Set default values based on inputs
    data["analysis"]["mechanics"] = ["Core gameplay loop based on " + genre, "User interaction and input handling"]
    data["analysis"]["complexity"] = "Medium"
    data["analysis"]["art_requirements"] = "Stylized 2D sprites and clean UI elements."
    data["analysis"]["monetization"] = "Premium purchase"
    
    if "casual" in audience.lower() or "kids" in audience.lower():
        data["analysis"]["monetization"] = "In-App Purchases (Cosmetics) & Ad-supported"
        
    if platform_lower in ["android", "ios"]:
        data["analysis"]["art_requirements"] = "Optimized low-poly 3D models or 2D sprites suited for mobile screens."
        data["analysis"]["complexity"] = "Low to Medium"
    elif platform_lower in ["vr/ar", "console"]:
        data["analysis"]["complexity"] = "High"
        data["analysis"]["art_requirements"] = "High-fidelity assets, optimized rendering shaders, and immersive UI."

    # Customize by Genre
    if "platformer" in genre_lower:
        data["analysis"]["mechanics"] = ["Running & Jumping physics", "Collectible items", "Obstacles/Hazards", "Level transitions"]
        data["analysis"]["required_systems"] = ["Physics Input System", "Score & Level Progress Tracking", "Camera Control (Cinemachine)"]
        
        # Assets
        data["assets"] = [
            {"name": "Cinemachine", "purpose": "Camera tracking and smooth screen shake", "rating": "Highly Recommended", "category": "Camera"},
            {"name": "DOTween (Demigiant)", "purpose": "Smooth animations for UI, platforms, and collectibles", "rating": "Highly Recommended", "category": "Animation"},
            {"name": "TextMeshPro", "purpose": "Advanced text rendering for UI and score display", "rating": "Essential", "category": "UI"},
            {"name": "Corgi Engine", "purpose": "Complete 2D/3D platformer controller framework", "rating": "Recommended (Paid)", "category": "Framework"},
            {"name": "FMOD Unity Integration", "purpose": "Interactive audio and dynamic music systems", "rating": "Recommended", "category": "Audio"}
        ]
        
        # Architecture
        data["architecture"]["managers"] = [
            {"name": "GameManager", "purpose": "Manages game states (Menu, Playing, GameOver, Paused) and score persistence."},
            {"name": "LevelManager", "purpose": "Controls level loading, spawn points, and progression."},
            {"name": "UIManager", "purpose": "Updates screen layouts, coins counter, lives, and pauses menus."},
            {"name": "AudioManager", "purpose": "Plays music tracks and triggers sound effects (jumping, dying, collecting)."}
        ]
        data["architecture"]["systems"] = [
            {"name": "PlayerInputController", "purpose": "Translates Unity Input System commands into character motion actions."},
            {"name": "SaveSystem", "purpose": "Saves unlocked levels and high scores using PlayerPrefs or JSON encryption."},
            {"name": "CollectibleSystem", "purpose": "Handles triggers and scoring logic for collectible items."}
        ]
        
        # Script
        data["scripts"]["PlayerController.cs"] = """using UnityEngine;

[RequireComponent(typeof(Rigidbody2D))]
[RequireComponent(typeof(Collider2D))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 8f;
    [SerializeField] private float jumpForce = 12f;
    
    [Header("Ground Check")]
    [SerializeField] private Transform groundCheckPoint;
    [SerializeField] private float groundCheckRadius = 0.2f;
    [SerializeField] private LayerMask groundLayer;
    
    private Rigidbody2D rb;
    private float horizontalInput;
    private bool isGrounded;
    private bool shouldJump;

    private void Start()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    private void Update()
    {
        // Get horizontal movement input
        horizontalInput = Input.GetAxisRaw("Horizontal");
        
        // Check ground status
        isGrounded = Physics2D.OverlapCircle(groundCheckPoint.position, groundCheckRadius, groundLayer);
        
        // Jump request check
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            shouldJump = true;
        }
    }

    private void FixedUpdate()
    {
        // Handle horizontal movement
        rb.linearVelocity = new Vector2(horizontalInput * moveSpeed, rb.linearVelocity.y);
        
        // Handle jumping
        if (shouldJump)
        {
            rb.linearVelocity = new Vector2(rb.linearVelocity.x, jumpForce);
            shouldJump = false;
        }
    }
}"""
        data["scripts"]["GameManager.cs"] = """using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [Header("Game State")]
    public int currentScore = 0;
    public int playerLives = 3;
    public bool isGameOver = false;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
        }
        else
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
    }

    public void AddScore(int amount)
    {
        currentScore += amount;
        Debug.Log("Score: " + currentScore);
    }

    public void TakeDamage(int damage)
    {
        playerLives -= damage;
        if (playerLives <= 0)
        {
            TriggerGameOver();
        }
    }

    private void TriggerGameOver()
    {
        isGameOver = true;
        Debug.Log("Game Over!");
    }

    public void RestartGame()
    {
        currentScore = 0;
        playerLives = 3;
        isGameOver = false;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }
}"""

    elif "puzzle" in genre_lower:
        data["analysis"]["mechanics"] = ["Grid configuration/matching", "Mechanism triggers", "Move limits/Timers", "Unlockable levels"]
        data["analysis"]["required_systems"] = ["Grid Alignment System", "Touch/Gesture Handling", "Progression & Save System"]
        
        data["assets"] = [
            {"name": "DOTween (Demigiant)", "purpose": "Essential for smooth board sliding, match popping, and scale effects", "rating": "Highly Recommended", "category": "Animation"},
            {"name": "LeanTouch", "purpose": "Robust and clean gesture detection (swipes, pinches, multi-tap)", "rating": "Highly Recommended", "category": "Input"},
            {"name": "TextMeshPro", "purpose": "Rendering sharp numbers and text on puzzle tiles", "rating": "Essential", "category": "UI"},
            {"name": "Shapes", "purpose": "Vector graphics library for crisp puzzle elements without textures", "rating": "Recommended (Paid)", "category": "Graphics"}
        ]
        
        data["architecture"]["managers"] = [
            {"name": "GameManager", "purpose": "Manages game phases, victory checks, and loading sequences."},
            {"name": "GridManager", "purpose": "Generates puzzle boards, tracks tile states, and triggers match logic."},
            {"name": "UIManager", "purpose": "Renders stars, remaining moves, victory panels, and level selection grids."}
        ]
        data["architecture"]["systems"] = [
            {"name": "PuzzleSolver", "purpose": "Determines valid states, validates matches, and check for deadlock boards."},
            {"name": "SaveSystem", "purpose": "Saves level completion metrics (stars earned, moves taken) to local SQLite or PlayerPrefs."}
        ]
        
        data["scripts"]["GridManager.cs"] = """using UnityEngine;
using System.Collections.Generic;

public class GridManager : MonoBehaviour
{
    public static GridManager Instance { get; private set; }

    [Header("Grid Config")]
    [SerializeField] private int width = 6;
    [SerializeField] private int height = 6;
    [SerializeField] private GameObject tilePrefab;
    [SerializeField] private float spacing = 1.1f;

    private GameObject[,] grid;

    private void Awake()
    {
        Instance = this;
    }

    private void Start()
    {
        GenerateGrid();
    }

    private void GenerateGrid()
    {
        grid = new GameObject[width, height];
        Vector3 startPos = transform.position - new Vector3((width - 1) * spacing / 2f, (height - 1) * spacing / 2f, 0);

        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                Vector3 position = startPos + new Vector3(x * spacing, y * spacing, 0);
                GameObject tile = Instantiate(tilePrefab, position, Quaternion.identity, transform);
                tile.name = $"Tile_{x}_{y}";
                grid[x, y] = tile;
            }
        }
    }

    public GameObject GetTileAt(int x, int y)
    {
        if (x >= 0 && x < width && y >= 0 && y < height)
            return grid[x, y];
        return null;
    }
}"""
        data["scripts"]["GameManager.cs"] = """using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    public int movesRemaining = 25;
    public bool isLevelComplete = false;

    private void Awake()
    {
        Instance = this;
    }

    public void UseMove()
    {
        if (isLevelComplete) return;
        
        movesRemaining--;
        if (movesRemaining <= 0)
        {
            TriggerGameOver();
        }
    }

    public void CheckWinCondition()
    {
        // Add custom win verification here
        isLevelComplete = true;
        Debug.Log("Puzzle Solved!");
    }

    private void TriggerGameOver()
    {
        Debug.Log("Out of moves!");
    }
}"""

    elif "rpg" in genre_lower:
        data["analysis"]["mechanics"] = ["Combat systems", "Stat progression", "Dialogue trees", "Inventory system"]
        data["analysis"]["required_systems"] = ["Inventory Management", "Quest Tracker", "Save & Load", "Dialogue System"]
        
        data["assets"] = [
            {"name": "A* Pathfinding Project", "purpose": "Fast pathfinding for player companions or enemy AI navigation", "rating": "Highly Recommended", "category": "AI/Pathfinding"},
            {"name": "Ink (Inkle)", "purpose": "Scripting language for complex interactive dialogue integration", "rating": "Highly Recommended", "category": "Dialogue"},
            {"name": "Odin Inspector", "purpose": "Customizing the inspector for managing database-heavy item stats", "rating": "Recommended (Paid)", "category": "Editor Utility"},
            {"name": "Cinemachine", "purpose": "Sleek 3rd person follow cams or dynamic dialogue camera zoom", "rating": "Essential", "category": "Camera"}
        ]
        
        data["architecture"]["managers"] = [
            {"name": "GameManager", "purpose": "Manages overarching game loop, state preservation, and scene navigation."},
            {"name": "InventoryManager", "purpose": "Tracks items, weights, slot limits, and item usage."},
            {"name": "QuestManager", "purpose": "Handles quest states (Active, Inactive, Completed) and triggers rewards."},
            {"name": "DialogueManager", "purpose": "Displays dialogues and choices parsed from Ink files."}
        ]
        data["architecture"]["systems"] = [
            {"name": "StatsSystem", "purpose": "Computes final stats (health, damage, armor) based on player level and equipment."},
            {"name": "SaveSystem", "purpose": "Serializes current quest, inventory, and location states to a encrypted binary file."}
        ]
        
        data["scripts"]["InventoryManager.cs"] = """using UnityEngine;
using System.Collections.Generic;

public class InventoryManager : MonoBehaviour
{
    public static InventoryManager Instance { get; private set; }

    [System.Serializable]
    public struct Item
    {
        public string id;
        public string name;
        public int amount;
    }

    [SerializeField] private List<Item> items = new List<Item>();
    [SerializeField] private int maxCapacity = 20;

    private void Awake()
    {
        Instance = this;
    }

    public bool AddItem(Item newItem)
    {
        if (items.Count >= maxCapacity)
        {
            Debug.LogWarning("Inventory full!");
            return false;
        }

        int index = items.FindIndex(i => i.id == newItem.id);
        if (index >= 0)
        {
            Item temp = items[index];
            temp.amount += newItem.amount;
            items[index] = temp;
        }
        else
        {
            items.Add(newItem);
        }
        
        Debug.Log($"Added {newItem.name} to inventory.");
        return true;
    }

    public void RemoveItem(string itemId, int amount)
    {
        int index = items.FindIndex(i => i.id == itemId);
        if (index >= 0)
        {
            Item temp = items[index];
            temp.amount -= amount;
            if (temp.amount <= 0)
                items.RemoveAt(index);
            else
                items[index] = temp;
        }
    }
}"""
        data["scripts"]["StatsSystem.cs"] = """using UnityEngine;

public class StatsSystem : MonoBehaviour
{
    [Header("Base Stats")]
    public int level = 1;
    public int experience = 0;
    public int baseMaxHealth = 100;
    public int currentHealth;
    public int strength = 10;
    public int defense = 5;

    private void Start()
    {
        currentHealth = baseMaxHealth;
    }

    public void AddExperience(int amount)
    {
        experience += amount;
        int expNeeded = level * 100;
        if (experience >= expNeeded)
        {
            LevelUp(expNeeded);
        }
    }

    private void LevelUp(int expNeeded)
    {
        experience -= expNeeded;
        level++;
        baseMaxHealth += 15;
        currentHealth = baseMaxHealth;
        strength += 2;
        defense += 1;
        Debug.Log($"Leveled up! Now Level {level}.");
    }

    public void TakeDamage(int rawDamage)
    {
        int netDamage = Mathf.Max(1, rawDamage - defense);
        currentHealth -= netDamage;
        Debug.Log($"Took {netDamage} damage. HP: {currentHealth}/{baseMaxHealth}");
        if (currentHealth <= 0)
        {
            Die();
        }
    }

    private void Die()
    {
        Debug.Log("Character has died.");
    }
}"""

    else:
        # Generic fallback
        data["analysis"]["mechanics"] = ["Core gameplay state loop", "User input actions", "Trigger boundaries and collisions"]
        data["analysis"]["required_systems"] = ["Input Management System", "Application State System", "UI & Menu System"]
        
        data["assets"] = [
            {"name": "TextMeshPro", "purpose": "High-quality text rendering across the game", "rating": "Essential", "category": "UI"},
            {"name": "DOTween (Demigiant)", "purpose": "Clean, procedural animation interface for dynamic items and panels", "rating": "Highly Recommended", "category": "Animation"},
            {"name": "Unity Addressables", "purpose": "Scalable local and remote assets configuration management", "rating": "Recommended", "category": "Assets"}
        ]
        
        data["architecture"]["managers"] = [
            {"name": "GameManager", "purpose": "Coordinates game loop, scores, and system states."},
            {"name": "UIManager", "purpose": "Manages screens, HUD, overlay overlays, and animations."}
        ]
        data["architecture"]["systems"] = [
            {"name": "SaveSystem", "purpose": "Loads and saves game stats and settings."},
            {"name": "InputSystem", "purpose": "Interprets player keyboard, gamepad, or mobile inputs."}
        ]
        
        data["scripts"]["GameManager.cs"] = """using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    public bool isGameActive = false;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
        }
        else
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
    }

    public void StartGame()
    {
        isGameActive = true;
        Debug.Log("Game Started.");
    }

    public void EndGame()
    {
        isGameActive = false;
        Debug.Log("Game Finished.");
    }
}"""
        data["scripts"]["UIManager.cs"] = """using UnityEngine;
using TMPro;

public class UIManager : MonoBehaviour
{
    public static UIManager Instance { get; private set; }

    [SerializeField] private GameObject menuPanel;
    [SerializeField] private GameObject hudPanel;
    [SerializeField] private TMP_Text statusText;

    private void Awake()
    {
        Instance = this;
    }

    public void ShowMainMenu()
    {
        menuPanel.SetActive(true);
        hudPanel.SetActive(false);
    }

    public void StartGameplayUI()
    {
        menuPanel.SetActive(false);
        hudPanel.SetActive(true);
    }

    public void SetStatusText(string text)
    {
        statusText.text = text;
    }
}"""

    # Customize Roadmap
    data["roadmap"]["phases"] = [
        {
            "title": "Phase 1: Project Setup & Package Imports",
            "duration": "1-2 Days",
            "tasks": [
                "Configure Unity project settings and target platform.",
                "Import text mesh pro, input systems and recommended assets.",
                "Set up the recommended Unity folder layout.",
                "Create base scenes: Bootstrap, MainMenu, and Level01."
            ]
        },
        {
            "title": "Phase 2: Core Gameplay Mechanics Implementation",
            "duration": "3-5 Days",
            "tasks": [
                f"Develop the starter scripts and connect them to characters or levels.",
                "Configure controls (Unity Input System) and map inputs.",
                "Setup basic UI mockups and bind them to variables in the GameManager.",
                "Build physical level segments or puzzle structures."
            ]
        },
        {
            "title": "Phase 3: Auxiliary Systems & Game Polishing",
            "duration": "2-3 Days",
            "tasks": [
                "Implement Save/Load persistence for player preferences and unlocked stats.",
                "Incorporate sound effects (SFX) and background music triggers.",
                "Polishing game actions using DOTween scaling and camera transitions (Cinemachine).",
                "Fix basic game loop bugs and verify flow transitions."
            ]
        },
        {
            "title": "Phase 4: Optimization & Deployment Settings",
            "duration": "2 Days",
            "tasks": [
                f"Run profile analyzers to verify CPU/GPU limits for target: {platform}.",
                "Compress texture assets and configure quality settings.",
                "Perform standalone build checks on local device.",
                "Prepare app store descriptions and icon details."
            ]
        }
    ]

    return data
