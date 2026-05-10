"""
narrative_tracer.py
-------------------
BONUS INSIGHT #3 — Cross-call narrative tracing.

WHO CARES?
  Executives. PMs writing post-incident comms. Anyone trying to understand
  "what happened with X event and how did it ripple through the company."

THE INSIGHT:
  Many real-world events (an outage, a launch, a competitive escalation)
  span MULTIPLE calls — internal war rooms, customer support tickets,
  account-team renewal conversations, and exec all-hands updates.

  Today, you'd manually read 12 different transcripts to reconstruct
  what happened. We can do it automatically by:

    1. Defining "narrative anchors" (a small set of seed keywords for an
       event of interest — e.g., the Detect Outage, the Comply v2 launch).
    2. Pulling EVERY meeting whose title, topics, summary, or transcript
       contains those anchors.
    3. Sorting them chronologically and grouping by call_type.
    4. Surfacing the timeline + downstream impact summary.

  This is what makes Transcript Intelligence INTELLIGENT — it stitches
  together what a human leader would otherwise miss.

WHAT WE BUILD HERE:
  A function `trace_narrative(anchors)` that returns a chronological
  story, grouping calls by call_type and showing the propagation of
  the event through the company.

EXAMPLES IN THIS DATASET:
  - "Detect Outage" anchor catches ~16 internal/external/support calls
    spanning ~10 days
  - "Comply v2" anchor traces the full launch journey
  - "SentinelShield" anchor traces competitive pressure
"""

from __future__ import annotations

import re

import pandas as pd


def _meeting_text(m) -> str:
    """All-text bag for keyword search on a meeting."""
    parts = [m.title, m.summary] + m.topics + [m.full_text]
    return " ".join(parts).lower()


def trace_narrative(meetings, anchors: list[str]) -> pd.DataFrame:
    """
    Find every meeting matching any anchor keyword and return a
    chronologically-sorted timeline.

    `anchors` are case-insensitive substring matches.
    """
    anchors_l = [a.lower() for a in anchors]
    rows = []
    for m in meetings:
        blob = _meeting_text(m)
        hits = [a for a in anchors_l if a in blob]
        if not hits:
            continue
        # Determine call_type the same way as the classifier
        all_emails = m.all_emails
        external = any(e.split("@")[-1] != "aegiscloud.com" for e in all_emails)
        if "support case" in m.title.lower():
            ct = "support"
        elif external:
            ct = "external"
        else:
            ct = "internal"
        rows.append({
            "start_time": m.start_time,
            "call_type": ct,
            "title": m.title,
            "sentiment_score": m.sentiment_score,
            "overall_sentiment": m.overall_sentiment,
            "summary": m.summary[:240] + ("…" if len(m.summary) > 240 else ""),
            "matched_anchors": ", ".join(hits),
            "external_customer": ", ".join(sorted({e.split("@")[-1] for e in all_emails
                                                   if e.split("@")[-1] != "aegiscloud.com"})),
        })
    return pd.DataFrame(rows).sort_values("start_time").reset_index(drop=True)


def narrative_summary_stats(timeline: pd.DataFrame) -> dict:
    """Summary stats for a narrative timeline."""
    if timeline.empty:
        return {}
    return {
        "n_calls": len(timeline),
        "first_call": timeline["start_time"].min(),
        "last_call": timeline["start_time"].max(),
        "duration_days": (timeline["start_time"].max() - timeline["start_time"].min()).days,
        "by_call_type": timeline["call_type"].value_counts().to_dict(),
        "n_unique_customers": timeline["external_customer"].replace("", pd.NA).dropna().nunique(),
        "avg_sentiment": round(timeline["sentiment_score"].mean(), 2),
    }
