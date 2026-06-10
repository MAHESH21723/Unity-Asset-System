def get_architecture_prompt_guidelines():
    """
    Returns guidelines and requirements for recommending software architecture and Unity folder structure.
    """
    return """
2. **Project Architecture**:
   - Recommend a set of Managers (e.g., GameManager, UIManager, LevelManager, etc.) with their specific `name` and `purpose`.
   - Recommend a set of Game Systems (e.g., Save System, Event System, Combat System, Quest System, etc.) with their `name` and `purpose`.
   
3. **Folder Structure**:
   - Generate a nested JSON-like structure showing how the Unity Assets folder should be organized.
   - It should start with "Assets" as the root. It should follow standard professional practices (e.g. Art, Audio, Prefabs, Scenes, Scripts with subfolders like Managers, Systems, UI, etc.).
   - Example format for JSON folder structure:
     {
       "Assets": {
         "Art": {
           "Sprites": {},
           "Models": {}
         },
         "Scripts": {
           "Managers": {},
           "Systems": {}
         }
       }
     }
"""
