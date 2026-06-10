def get_script_prompt_guidelines():
    """
    Returns guidelines and requirements for generating starter C# scripts.
    """
    return """
4. **Starter C# Scripts**:
   - Provide the complete code for 2 or 3 essential C# scripts for the game.
   - For example, if it is a platformer, generate GameManager.cs and PlayerController.cs.
   - If it is a puzzle game, generate GameManager.cs and GridManager.cs.
   - The C# scripts should be valid Unity scripts, complete, clean, with comments explaining key parts.
   - They should use standard Unity life-cycle methods (Awake, Start, Update, FixedUpdate, etc.) as appropriate.
   - Provide them as a key-value dictionary where keys are filenames (e.g., "GameManager.cs") and values are the exact code contents.
"""
