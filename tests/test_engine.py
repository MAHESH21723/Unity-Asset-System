import json

import pytest

import ai_engine
from ai_engine import build_prompt, clean_json_response, generate_recommendations
from ai_engine.mock_engine import generate_mock_data, profile_key_for
from ai_engine.schema import normalize_report

REQUIRED_KEYS = {"analysis", "assets", "architecture", "folder_structure", "roadmap", "scripts"}


@pytest.mark.parametrize(
    "genre, expected_scripts",
    [
        ("Platformer", {"PlayerController.cs", "GameManager.cs"}),
        ("Puzzle", {"GridManager.cs", "GameManager.cs"}),
        ("RPG", {"InventoryManager.cs", "StatsSystem.cs"}),
        ("Shooter", {"PlayerShooter.cs", "Projectile.cs", "Health.cs"}),
        ("Racing", {"GameManager.cs", "UIManager.cs"}),
    ],
)
def test_mock_engine_scripts_per_genre(genre, expected_scripts):
    data = generate_mock_data("Demo", genre, "PC", "Core", "A demo description of a game.")
    assert REQUIRED_KEYS <= data.keys()
    assert set(data["scripts"]) == expected_scripts
    assert data["assets"] and data["architecture"]["managers"]
    assert len(data["roadmap"]["phases"]) == 4


def test_mock_scripts_look_like_valid_csharp():
    for genre in ("Platformer", "Puzzle", "RPG", "Shooter", "Other"):
        for name, code in generate_mock_data("D", genre, "PC", "Core", "x" * 30)["scripts"].items():
            class_name = name.removesuffix(".cs")
            assert f"class {class_name}" in code, name
            assert code.count("{") == code.count("}"), name
            assert "using UnityEngine;" in code or "using TMPro;" in code, name


def test_mock_engine_adapts_to_platform_and_audience():
    mobile = generate_mock_data("D", "Puzzle", "Android", "Kids", "x" * 30)["analysis"]
    vr = generate_mock_data("D", "Puzzle", "VR/AR", "Hardcore", "x" * 30)["analysis"]
    assert mobile["complexity"] == "Low to Medium"
    assert "In-app purchases" in mobile["monetization"]
    assert vr["complexity"] == "High"
    assert vr["monetization"] == "Premium purchase"


def test_mock_engine_results_are_independent_copies():
    first = generate_mock_data("D", "RPG", "PC", "Core", "x" * 30)
    first["assets"].clear()
    first["folder_structure"]["Assets"].clear()
    second = generate_mock_data("D", "RPG", "PC", "Core", "x" * 30)
    assert second["assets"] and second["folder_structure"]["Assets"]


def test_profile_key_for():
    assert profile_key_for("Mobile Platformer") == "platformer"
    assert profile_key_for("Strategy") == "generic"


def test_generate_recommendations_defaults_to_offline():
    report, engine = generate_recommendations("T", "Puzzle", "PC", "Core", "x" * 30)
    assert engine == "mock"
    assert REQUIRED_KEYS <= report.keys()


def test_forced_provider_without_key_uses_offline():
    _, engine = generate_recommendations("T", "Puzzle", "PC", "Core", "x" * 30, force_engine="gemini")
    assert engine == "mock"


def test_provider_used_when_key_present(monkeypatch):
    payload = generate_mock_data("T", "Puzzle", "PC", "Core", "x" * 30)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(ai_engine, "_call_openai", lambda prompt, key: "```json\n" + json.dumps(payload) + "\n```")
    report, engine = generate_recommendations("T", "Puzzle", "PC", "Core", "x" * 30)
    assert engine == "openai"
    assert "GridManager.cs" in report["scripts"]


def test_provider_failure_falls_back_to_offline(monkeypatch):
    def boom(prompt, key):
        raise RuntimeError("network down")

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(ai_engine, "_call_gemini", boom)
    _, engine = generate_recommendations("T", "Puzzle", "PC", "Core", "x" * 30)
    assert engine == "mock"


def test_provider_garbage_falls_back_to_offline(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(ai_engine, "_call_gemini", lambda prompt, key: "I cannot do that")
    _, engine = generate_recommendations("T", "Puzzle", "PC", "Core", "x" * 30)
    assert engine == "mock"


def test_build_prompt_contains_spec_and_guidelines():
    prompt = build_prompt("My Game", "RPG", "PC", "Core", "A long enough description")
    assert "My Game" in prompt and "RPG" in prompt
    assert "Asset Recommendations" in prompt and "Starter C# Scripts" in prompt


class TestCleanJsonResponse:
    def test_plain_json(self):
        assert clean_json_response('{"a": 1}') == {"a": 1}

    def test_fenced_json(self):
        assert clean_json_response('Here:\n```json\n{"a": 1}\n```\nDone') == {"a": 1}

    def test_json_surrounded_by_prose(self):
        assert clean_json_response('Sure! {"a": {"b": 2}} hope it helps') == {"a": {"b": 2}}

    @pytest.mark.parametrize("bad", ["", "no json here", "[1, 2, 3]", "{broken"])
    def test_invalid_raises(self, bad):
        with pytest.raises(ValueError):
            clean_json_response(bad)


class TestNormalizeReport:
    def test_rejects_non_dict_and_empty(self):
        with pytest.raises(ValueError):
            normalize_report([])
        with pytest.raises(ValueError):
            normalize_report({})

    def test_drops_unsafe_script_names(self):
        report = normalize_report(
            {
                "assets": [{"name": "A"}],
                "scripts": {
                    "../../evil.cs": "x",
                    "Good.cs": "class Good {}",
                    "a'b.cs": "x",
                    "NotCs.txt": "x",
                    "Empty.cs": "   ",
                },
            }
        )
        assert list(report["scripts"]) == ["Good.cs"]

    def test_sanitizes_folder_tree(self):
        report = normalize_report(
            {
                "assets": [{"name": "A"}],
                "folder_structure": {"Assets": {"../escape": {}, "Scripts": {"Managers": {}}, "bad/slash": {}}},
            }
        )
        assert report["folder_structure"] == {"Assets": {"Scripts": {"Managers": {}}}}

    def test_falls_back_to_default_tree_and_coerces_types(self):
        report = normalize_report(
            {
                "analysis": {"mechanics": "not a list", "complexity": 5},
                "assets": [{"name": "Tool", "rating": "ESSENTIAL!!", "purpose": None}, "junk", {"purpose": "no name"}],
                "folder_structure": "nope",
            }
        )
        assert report["analysis"]["mechanics"] == []
        assert report["analysis"]["complexity"] == "5"
        assert report["assets"] == [{"name": "Tool", "purpose": "", "rating": "Essential", "category": ""}]
        assert "Assets" in report["folder_structure"]
