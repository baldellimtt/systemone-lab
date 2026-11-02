"""CI smoke tests — no GPU, no live Laya/Jev calls."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest
from typesafe_sdk import Choice, Noul, Score

ROOT = Path(__file__).resolve().parents[1]


def test_repo_layout() -> None:
    for rel in (
        "README.md",
        "LICENSE",
        "NOTICE",
        "requirements.txt",
        "ui/index.html",
        "scripts/start_laya.ps1",
        "scripts/start_laya.sh",
        "scripts/lab_ui.py",
        "examples/01_tre_primitivi.py",
        "data/tickets.json",
        "data/agent_traces.json",
    ):
        assert (ROOT / rel).is_file(), f"missing {rel}"


def test_example_scripts_parse() -> None:
    for path in sorted((ROOT / "examples").glob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_jev_lab_imports() -> None:
    importlib.import_module("jev_lab")
    importlib.import_module("jev_lab.client")
    importlib.import_module("jev_lab.pretty")


def test_question_primitives_construct() -> None:
    questions = {
        "billing": Noul(instructions="Is this about billing?"),
        "tone": Choice(
            instructions="Tone?",
            criteria={"calm": None, "frustrated": "annoyed", "angry": None},
        ),
        "urgency": Score(
            instructions="Urgency?",
            criteria=["can wait", "this week", "today"],
        ),
    }
    assert set(questions) == {"billing", "tone", "urgency"}


def test_ui_mentions_systemone_contract() -> None:
    html = (ROOT / "ui" / "index.html").read_text(encoding="utf-8")
    assert "/api/systemone" in html
    assert "noul" in html and "choice" in html and "score" in html


def test_dotenv_example_has_no_real_secret() -> None:
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "sk-" not in text or "sk-..." in text or "sk-codiv-..." in text
    assert "TYPESAFE_BASE_URL" in text


@pytest.mark.parametrize("script", ["start_laya.sh", "lab_ui.py"])
def test_scripts_exist(script: str) -> None:
    assert (ROOT / "scripts" / script).is_file()
