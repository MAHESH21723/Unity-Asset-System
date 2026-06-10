def get_asset_prompt_guidelines():
    """
    Returns guidelines and requirements for recommending Unity assets based on a game idea.
    """
    return """
1. **Asset Recommendations**: Recommend between 3 to 6 suitable Unity Assets.
   - For each asset, specify:
     - `name`: Name of the asset (e.g., DOTween, Cinemachine, TextMeshPro, etc.).
     - `purpose`: Why the developer should use this asset in their specific game.
     - `rating`: "Essential", "Highly Recommended", or "Recommended".
     - `category`: Category (e.g. Animation, Camera, UI, Input, Audio, etc.).
   - Include standard Unity Packages (like Input System, Addressables, Cinemachine, Universal RP) as well as popular Unity Asset Store utilities if helpful.
"""
