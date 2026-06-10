def get_roadmap_prompt_guidelines():
    """
    Returns guidelines and requirements for generating a development roadmap.
    """
    return """
5. **Development Roadmap**:
   - Provide a 4-phase roadmap showing:
     - `title`: Title of the phase (e.g. Phase 1: Project Setup).
     - `duration`: Estimated duration (e.g., "1 Day", "3 Days", etc.).
     - `tasks`: A list of strings representing specific tasks to be completed in this phase.
   - Phases:
     - Phase 1: Project Setup (Folder structure, basic settings, importing packages).
     - Phase 2: Core Gameplay Mechanics (Implementing the primary gameplay loops and starter scripts).
     - Phase 3: Systems Integration & Polishing (UI, save system, audio, visual polish).
     - Phase 4: Testing & Deployment (Optimization, build validation, export configurations).
"""
