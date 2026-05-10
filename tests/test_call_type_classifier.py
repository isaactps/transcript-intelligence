"""Unit tests for transcript_intelligence.call_type_classifier."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence.call_type_classifier import classify


def test_support_case_title_wins() -> None:
    """A title starting with 'Support Case' is always 'support'."""
    ct, conf, _ = classify(
        "Support Case #1234 - Customer X latency",
        ["agent@aegiscloud.com", "user@customer.com"],
    )
    assert ct == "support"
    assert conf >= 0.95


def test_aegis_slash_external() -> None:
    """'Aegis / Customer Name - Topic' → external."""
    ct, _, _ = classify(
        "Aegis / Quantum Edge - Renewal Concerns",
        ["am@aegiscloud.com", "vp@quantumedge.com"],
    )
    assert ct == "external"


def test_non_aegis_attendee_external() -> None:
    """Any attendee with a non-Aegis email → external."""
    ct, _, _ = classify(
        "Quarterly Sync",
        ["alice@aegiscloud.com", "bob@bigcorp.com"],
    )
    assert ct == "external"


def test_internal_keyword_in_title() -> None:
    """Internal-meeting keyword in title → internal."""
    ct, _, _ = classify(
        "Weekly Engineering Standup",
        ["a@aegiscloud.com", "b@aegiscloud.com"],
    )
    assert ct == "internal"


def test_aegis_only_default_internal() -> None:
    """Only Aegis attendees + no other signal → internal."""
    ct, _, _ = classify(
        "Random Discussion",
        ["a@aegiscloud.com", "b@aegiscloud.com"],
    )
    assert ct == "internal"


def test_empty_emails_is_internal() -> None:
    """No emails at all → internal (safer default)."""
    ct, _, _ = classify("Anything", [])
    assert ct == "internal"


def test_support_takes_priority_over_external_signal() -> None:
    """A 'Support Case' title wins even when a customer is dialled in."""
    ct, _, _ = classify(
        "Support Case #5678 - Outage",
        ["a@aegiscloud.com", "user@othercorp.com"],
    )
    assert ct == "support"
