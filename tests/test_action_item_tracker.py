"""Unit tests for transcript_intelligence.action_item_tracker."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence.action_item_tracker import parse_action


def test_parses_owner_prefix() -> None:
    parsed = parse_action("Maria Santos: send the report by Friday")
    assert parsed["owner"] == "Maria Santos"
    assert parsed["body"].startswith("send the report")


def test_extracts_friday_deadline() -> None:
    parsed = parse_action("Sarah Chen: ship the update by Friday")
    assert parsed["deadline_phrase"].lower().startswith("by friday")


def test_extracts_end_of_week_deadline() -> None:
    parsed = parse_action("Kevin O'Brien: deliver fix by end of week")
    assert "end of week" in parsed["deadline_phrase"].lower()


def test_unassigned_when_no_owner_prefix() -> None:
    parsed = parse_action("ship the update by Tuesday")
    assert parsed["owner"] == "(unassigned)"
    assert parsed["deadline_phrase"].lower().startswith("by tuesday")


def test_owner_with_apostrophe_preserved() -> None:
    parsed = parse_action("Kevin O'Brien: take the call")
    assert parsed["owner"] == "Kevin O'Brien"


def test_no_deadline_returns_empty_string() -> None:
    parsed = parse_action("David Kim: investigate the bug")
    assert parsed["deadline_phrase"] == ""
