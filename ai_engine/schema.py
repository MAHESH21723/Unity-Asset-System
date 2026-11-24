"""Validation and sanitising of recommendation reports.

Reports can come from an LLM, so nothing in them is trusted. ``normalize_report``
coerces any parsed JSON into the exact shape the templates and exporters expect,
and restricts file names and folder names to safe characters. That protects the
HTML views, the Markdown export and the ZIP builder (no path traversal).
"""

from __future__ import annotations

import re
from typing import Any

from ai_engine.mock_engine import DEFAULT_FOLDER_STRUCTURE

MAX_ITEMS = 20
MAX_TEXT = 600
MAX_SCRIPT_CHARS = 20_000
MAX_SCRIPTS = 6
MAX_TREE_DEPTH = 6

_SCRIPT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,59}\.cs$")
_FOLDER_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.\-]{0,39}$")

RATINGS = ("Essential", "Highly Recommended", "Recommended")


def _text(value: Any, default: str = "") -> str:
    """Return ``value`` as a trimmed, length-limited string."""
    if value is None:
        return default
    return str(value).strip()[:MAX_TEXT] or default


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [t for t in (_text(v) for v in value[:MAX_ITEMS]) if t]


def _named_items(value: Any, keys: tuple[str, ...]) -> list[dict[str, str]]:
    """Keep only dict items that have a non-empty ``name``."""
    if not isinstance(value, list):
        return []
    items = []
    for raw in value[:MAX_ITEMS]:
        if isinstance(raw, dict) and _text(raw.get("name")):
            items.append({k: _text(raw.get(k)) for k in keys})
    return items


def _clean_tree(node: Any, depth: int = 0) -> dict[str, Any]:
    """Recursively keep only dicts whose keys are safe folder names."""
    if not isinstance(node, dict) or depth >= MAX_TREE_DEPTH:
        return {}
    cleaned: dict[str, Any] = {}
    for key, child in list(node.items())[:MAX_ITEMS * 3]:
        name = str(key).strip()
        if _FOLDER_NAME.match(name) and ".." not in name:
            cleaned[name] = _clean_tree(child, depth + 1)
    return cleaned


def _clean_rating(value: Any) -> str:
    text = _text(value, "Recommended")
    lowered = text.lower()
    if "essential" in lowered:
        return "Essential"
    if "highly" in lowered:
        return "Highly Recommended"
    return "Recommended"


def normalize_report(data: Any) -> dict[str, Any]:
    """Coerce arbitrary parsed JSON into a safe, complete report.

    Raises:
        ValueError: if ``data`` is not a dict or contains no usable content.
    """
    if not isinstance(data, dict):
        raise ValueError("Report must be a JSON object.")

    analysis_in = data.get("analysis") if isinstance(data.get("analysis"), dict) else {}
    analysis = {
        "genre": _text(analysis_in.get("genre"), "Unknown"),
        "mechanics": _text_list(analysis_in.get("mechanics")),
        "required_systems": _text_list(analysis_in.get("required_systems")),
        "art_requirements": _text(analysis_in.get("art_requirements"), "Not specified."),
        "monetization": _text(analysis_in.get("monetization"), "Not specified."),
        "complexity": _text(analysis_in.get("complexity"), "Medium"),
    }

    assets = [
        {**item, "rating": _clean_rating(item["rating"])}
        for item in _named_items(data.get("assets"), ("name", "purpose", "rating", "category"))
    ]

    architecture_in = data.get("architecture") if isinstance(data.get("architecture"), dict) else {}
    architecture = {
        "managers": _named_items(architecture_in.get("managers"), ("name", "purpose")),
        "systems": _named_items(architecture_in.get("systems"), ("name", "purpose")),
    }

    folder_structure = _clean_tree(data.get("folder_structure"))
    if not folder_structure:
        folder_structure = _clean_tree(DEFAULT_FOLDER_STRUCTURE)

    phases = []
    roadmap_in = data.get("roadmap") if isinstance(data.get("roadmap"), dict) else {}
    raw_phases = roadmap_in.get("phases")
    for raw in raw_phases[:MAX_ITEMS] if isinstance(raw_phases, list) else []:
        if isinstance(raw, dict) and _text(raw.get("title")):
            phases.append(
                {
                    "title": _text(raw.get("title")),
                    "duration": _text(raw.get("duration"), "TBD"),
                    "tasks": _text_list(raw.get("tasks")),
                }
            )

    scripts: dict[str, str] = {}
    scripts_in = data.get("scripts") if isinstance(data.get("scripts"), dict) else {}
    for filename, code in scripts_in.items():
        if len(scripts) >= MAX_SCRIPTS:
            break
        if isinstance(filename, str) and _SCRIPT_NAME.match(filename) and isinstance(code, str) and code.strip():
            scripts[filename] = code[:MAX_SCRIPT_CHARS]

    if not (assets or architecture["managers"] or scripts or phases):
        raise ValueError("Report contained no usable content.")

    return {
        "analysis": analysis,
        "assets": assets,
        "architecture": architecture,
        "folder_structure": folder_structure,
        "roadmap": {"phases": phases},
        "scripts": scripts,
    }
