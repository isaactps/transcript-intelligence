"""
call_type_classifier.py
-----------------------
Classify each meeting into one of the three call types described in the brief:

    - support  : a customer reaching out about a specific issue / ticket
    - external : account-team conversation with a customer (renewal, QBR,
                 onboarding, planning, etc.)
    - internal : Aegis-only meeting (standup, planning, postmortem, all-hands)

Approach: HYBRID rule-based.

Why rule-based here?
  The signal is very strong:
    * Every email has a domain. If everyone is @aegiscloud.com, it is internal.
    * Titles use stable patterns ("Support Case #...", "Aegis / Customer ...").
  An LLM would happily classify these but rule-based is faster, free,
  100% deterministic, and trivial to audit. We only fall back to LLM-style
  reasoning if the rules don't match.

Output: each Meeting gets a `call_type` and `confidence` field on the wide
frame.
"""

from __future__ import annotations

import re

INTERNAL_DOMAIN = "aegiscloud.com"

SUPPORT_TITLE_RE = re.compile(r"\b(support case|ticket|issue #|case #)\b", re.IGNORECASE)
INTERNAL_TITLE_KEYWORDS = (
    "standup", "sprint planning", "sprint retro", "all hands", "all-hands",
    "postmortem", "post-incident", "war room", "internal", "roadmap",
    "win/loss", "design review", "readiness", "audit preparation",
    "type ii", "team -", "incident:",
)


def classify(title: str, all_emails: list[str]) -> tuple[str, float, str]:
    """
    Return (call_type, confidence, reason).
    """
    title_l = title.lower()
    domains = {e.split("@")[-1].lower() for e in all_emails if "@" in e}
    has_external = any(d != INTERNAL_DOMAIN for d in domains)

    # Rule 1 — Title explicitly says "Support Case" → support, regardless
    # of whether the customer dialled in or it was Aegis-internal triage.
    if SUPPORT_TITLE_RE.search(title):
        return "support", 0.99, "title matches support-case pattern"

    # Rule 2 — Title starts with "Aegis / <Customer>" → external customer call
    if title_l.startswith("aegis /"):
        return "external", 0.99, "title format 'Aegis / <Customer>'"

    # Rule 3 — Any non-Aegis attendee → external customer call
    if has_external:
        return "external", 0.9, f"non-Aegis attendees: {sorted(domains - {INTERNAL_DOMAIN})}"

    # Rule 4 — Internal-meeting keyword in title
    if any(kw in title_l for kw in INTERNAL_TITLE_KEYWORDS):
        return "internal", 0.95, "internal-meeting keyword in title"

    # Rule 5 — Fallback: only Aegis attendees → internal
    return "internal", 0.8, "only Aegis attendees, no other strong signal"


def add_call_type_to_frame(meetings_frame, meetings):
    """Attach call_type, confidence, reason columns to the wide frame."""
    rows = [classify(m.title, m.all_emails) for m in meetings]
    meetings_frame = meetings_frame.copy()
    meetings_frame["call_type"] = [r[0] for r in rows]
    meetings_frame["call_type_conf"] = [r[1] for r in rows]
    meetings_frame["call_type_reason"] = [r[2] for r in rows]
    return meetings_frame
