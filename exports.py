"""Builders for the Markdown report and the Unity starter-kit ZIP."""

from __future__ import annotations

import io
import re
import zipfile
from collections.abc import Mapping
from typing import Any

DEFAULT_TREE: dict[str, Any] = {
    "Assets": {
        "Art": {},
        "Audio": {},
        "Prefabs": {},
        "Scenes": {},
        "Scripts": {"Managers": {}, "Systems": {}, "Gameplay": {}, "UI": {}},
    }
}


def safe_filename(name: str, fallback: str = "Unity_Project") -> str:
    """Reduce a project name to a filesystem- and header-safe file stem."""
    cleaned = "".join(ch for ch in name if ch.isalnum() or ch in " -_").strip().replace(" ", "_")
    return cleaned or fallback


def script_folder(filename: str) -> str:
    """Choose the ``Assets/Scripts`` sub-folder for a script by its name words."""
    stem = filename.rsplit(".", 1)[0]
    words = {w.lower() for w in re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+", stem)}

    if words & {"ui", "menu", "canvas", "hud", "panel"}:
        return "Assets/Scripts/UI"
    if words & {"manager", "managers", "spawner"}:
        return "Assets/Scripts/Managers"
    if words & {"controller", "player", "movement", "character", "shooter", "projectile", "health", "enemy"}:
        return "Assets/Scripts/Gameplay"
    if words & {"system", "save", "load", "stats", "inventory"}:
        return "Assets/Scripts/Systems"
    return "Assets/Scripts"


def format_tree(node: Mapping[str, Any], prefix: str = "") -> str:
    """Render a nested folder dict as an ASCII tree."""
    lines = []
    items = list(node.items())
    for index, (name, child) in enumerate(items):
        last = index == len(items) - 1
        lines.append(f"{prefix}{'`-- ' if last else '|-- '}{name}")
        if isinstance(child, Mapping) and child:
            lines.append(format_tree(child, prefix + ("    " if last else "|   ")).rstrip("\n"))
    return "\n".join(lines) + "\n"


def collect_leaf_paths(node: Any, current: str = "") -> list[str]:
    """Return the path of every leaf folder in the tree."""
    if not isinstance(node, Mapping) or not node:
        return [current] if current else []
    paths: list[str] = []
    for key, child in node.items():
        paths.extend(collect_leaf_paths(child, f"{current}/{key}" if current else str(key)))
    return paths


def build_markdown_report(project: Mapping[str, Any], recs: Mapping[str, Any], scripts: Mapping[str, str]) -> str:
    """Build the developer report as Markdown."""
    analysis = recs.get("analysis", {})
    architecture = recs.get("architecture", {})
    out = [
        f"# Unity Asset Recommendation Report: {project['project_name']}",
        f"Generated on: {project['created_at']}",
        "",
        "## 1. Project Specifications",
        f"- **Genre:** {project['genre']}",
        f"- **Platform:** {project['platform']}",
        f"- **Target Audience:** {project['target_audience']}",
        f"- **Description:** {project['description']}",
        "",
        "## 2. Project Analysis",
        f"- **Complexity:** {analysis.get('complexity', 'N/A')}",
        f"- **Art Requirements:** {analysis.get('art_requirements', 'N/A')}",
        f"- **Monetization:** {analysis.get('monetization', 'N/A')}",
        "- **Core Mechanics:**",
        *[f"  - {m}" for m in analysis.get("mechanics", [])],
        "- **Required Systems:**",
        *[f"  - {s}" for s in analysis.get("required_systems", [])],
        "",
        "## 3. Recommended Unity Assets",
    ]
    for asset in recs.get("assets", []):
        out += [
            f"### {asset.get('name')} ({asset.get('rating')})",
            f"- **Category:** {asset.get('category')}",
            f"- **Purpose:** {asset.get('purpose')}",
            "",
        ]

    out += ["## 4. Suggested Software Architecture", "### Recommended Managers"]
    out += [f"- **{m.get('name')}:** {m.get('purpose')}" for m in architecture.get("managers", [])]
    out += ["", "### Recommended Systems"]
    out += [f"- **{s.get('name')}:** {s.get('purpose')}" for s in architecture.get("systems", [])]

    out += ["", "## 5. Suggested Folder Structure", "```", format_tree(recs.get("folder_structure", {})).rstrip("\n"), "```", ""]

    out.append("## 6. Development Roadmap")
    for phase in recs.get("roadmap", {}).get("phases", []):
        out.append(f"### {phase.get('title')} (Duration: {phase.get('duration')})")
        out += [f"- [ ] {task}" for task in phase.get("tasks", [])]
        out.append("")

    out.append("## 7. Starter C# Scripts")
    for filename, code in scripts.items():
        out += [f"### File: {filename}", "````csharp", code.rstrip("\n"), "````", ""]

    return "\n".join(out) + "\n"


def build_starter_kit(project: Mapping[str, Any], recs: Mapping[str, Any], scripts: Mapping[str, str]) -> io.BytesIO:
    """Build an in-memory ZIP with the folder layout and starter scripts."""
    tree = recs.get("folder_structure") or DEFAULT_TREE
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in collect_leaf_paths(tree):
            archive.writestr(f"{path.strip('/')}/.keep", "Placeholder that keeps this empty folder in version control.\n")

        for filename, content in scripts.items():
            # Names are validated on save; re-check here as defense in depth.
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\.cs", filename):
                continue
            archive.writestr(f"{script_folder(filename)}/{filename}", content)

        archive.writestr(
            "Assets/README_StarterKit.txt",
            f"Unity Starter Kit: {project['project_name']}\n"
            f"{'-' * 50}\n"
            "Generated by Unity AI Architect.\n\n"
            f"Game title:      {project['project_name']}\n"
            f"Genre:           {project['genre']}\n"
            f"Platform:        {project['platform']}\n"
            f"Target audience: {project['target_audience']}\n"
            f"Generated on:    {project['created_at']}\n\n"
            "How to use\n"
            "1. Extract this ZIP.\n"
            "2. Copy the Assets folder into your Unity project (merge when asked).\n"
            "3. Assign the serialized fields (prefabs, UI references) in the Inspector.\n",
        )

    buffer.seek(0)
    return buffer
