import zipfile

import pytest

from exports import (
    build_markdown_report,
    build_starter_kit,
    collect_leaf_paths,
    format_tree,
    safe_filename,
    script_folder,
)

PROJECT = {
    "project_name": "Demo",
    "genre": "RPG",
    "platform": "PC",
    "target_audience": "Core",
    "description": "A demo.",
    "created_at": "2026-01-01 00:00:00",
}


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("My Cool Game!", "My_Cool_Game"),
        ("../../etc/passwd", "etcpasswd"),
        ("???", "Unity_Project"),
        ("Café 2", "Café_2"),
    ],
)
def test_safe_filename(raw, expected):
    assert safe_filename(raw) == expected


@pytest.mark.parametrize(
    "filename, folder",
    [
        ("GameManager.cs", "Assets/Scripts/Managers"),
        ("UIManager.cs", "Assets/Scripts/UI"),
        ("PlayerController.cs", "Assets/Scripts/Gameplay"),
        ("StatsSystem.cs", "Assets/Scripts/Systems"),
        ("Fluid.cs", "Assets/Scripts"),  # contains "ui" letters but not the word "UI"
    ],
)
def test_script_folder(filename, folder):
    assert script_folder(filename) == folder


def test_tree_helpers():
    tree = {"Assets": {"Art": {}, "Scripts": {"UI": {}}}}
    assert collect_leaf_paths(tree) == ["Assets/Art", "Assets/Scripts/UI"]
    rendered = format_tree(tree)
    assert "|-- Art" in rendered and "`-- Scripts" in rendered and "UI" in rendered


def test_markdown_report_sections():
    recs = {
        "analysis": {"mechanics": ["Jump"], "required_systems": ["Save"], "complexity": "Low"},
        "assets": [{"name": "DOTween", "rating": "Essential", "category": "Animation", "purpose": "Tweens"}],
        "architecture": {"managers": [{"name": "GM", "purpose": "Rules"}], "systems": []},
        "folder_structure": {"Assets": {"Art": {}}},
        "roadmap": {"phases": [{"title": "Phase 1", "duration": "1 Day", "tasks": ["Do it"]}]},
    }
    md = build_markdown_report(PROJECT, recs, {"A.cs": "class A {}"})
    for fragment in ("# Unity Asset Recommendation Report: Demo", "### DOTween (Essential)", "- [ ] Do it", "### File: A.cs", "class A {}"):
        assert fragment in md


def test_starter_kit_skips_unsafe_script_names():
    recs = {"folder_structure": {"Assets": {"Art": {}}}}
    buffer = build_starter_kit(PROJECT, recs, {"Good.cs": "class Good {}", "../../evil.cs": "x"})
    with zipfile.ZipFile(buffer) as zf:
        names = zf.namelist()
    assert "Assets/Art/.keep" in names
    assert "Assets/Scripts/Good.cs" in names
    assert not any("evil" in n for n in names)


def test_starter_kit_uses_default_tree_when_missing():
    with zipfile.ZipFile(build_starter_kit(PROJECT, {}, {})) as zf:
        assert any(n.startswith("Assets/Scripts/Managers/") for n in zf.namelist())
