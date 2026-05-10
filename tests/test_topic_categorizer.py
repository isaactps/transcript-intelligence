"""Unit tests for transcript_intelligence.topic_categorizer."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence.topic_categorizer import THEMES, categorize_one


def test_outage_topic_routes_to_reliability() -> None:
    res = categorize_one(
        ["outage", "incident response", "rca"],
        "INCIDENT: Detect Pipeline Failure",
    )
    assert res["primary"] == "Reliability & Incidents"
    assert res["primary_score"] > 0


def test_renewal_routes_to_renewal_theme() -> None:
    res = categorize_one(
        ["renewal", "churn risk", "retention"],
        "Aegis / Quantum Edge - Renewal Concerns",
    )
    assert res["primary"] == "Renewal & Churn Risk"


def test_compliance_routes_to_compliance() -> None:
    res = categorize_one(
        ["compliance", "soc 2", "audit"],
        "Aegis / Redwood Clinical - ISO 27001 Preparation",
    )
    assert res["primary"] == "Compliance & Audit"


def test_no_match_returns_other() -> None:
    res = categorize_one(["unrelated topic"], "Random Title")
    assert res["primary"] == "Other"
    assert res["primary_score"] == 0.0


def test_secondary_themes_surfaced() -> None:
    """A meeting with both reliability AND renewal signals returns one as
    primary and the other as a secondary."""
    res = categorize_one(
        ["outage", "incident response", "renewal", "churn risk"],
        "Some Meeting",
    )
    # Primary will be whichever scored higher; the other should appear as secondary
    assert res["primary"] in {"Reliability & Incidents", "Renewal & Churn Risk"}
    assert len(res["secondary"]) >= 1


def test_taxonomy_has_eight_themes() -> None:
    """The deck claims 8 themes — let's enforce it."""
    assert len(THEMES) == 8
