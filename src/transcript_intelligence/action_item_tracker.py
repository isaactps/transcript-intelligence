"""
action_item_tracker.py
----------------------
BONUS INSIGHT #2 — Action-item & commitment tracker.

WHO CARES?
  Every call leader. PMs, eng leads, account managers, support managers
  all walk away with action items. Today they live in scattered docs and
  meeting notes, and follow-through is poor.

WHAT WE DO:
  Each `summary.json` already contains a clean `actionItems` list. We:

    1. Parse owner names out of each item (most use "Name: do X" format).
    2. Extract any explicit deadline phrases.
    3. Cross-link the action item back to the meeting + customer.
    4. Aggregate by owner to surface workload concentration.
    5. Flag deadlines that are EXTERNAL-FACING (action item from a customer
       call) — those are the highest-stakes commitments.

WHY THIS MATTERS:
  * Account managers can see EVERY commitment they made to a customer
    across calls in one view.
  * VPs can see who is overloaded with action items.
  * If a commitment is missed, you can trace the original conversation.

  Several of the calls in this dataset have promises like "I'll get the
  technical remediation report to you by Tuesday" — those are the moments
  customers remember.
"""

from __future__ import annotations

import re

import pandas as pd

# Regex to pull "Owner Name:" prefix at start of an action-item string.
OWNER_RE = re.compile(r"^([A-Z][\w\.\-']+(?:\s+[A-Z][\w\.\-']+){0,2}):\s*(.+)$")

# Regex to find common deadline phrases inside the action text.
DEADLINE_RE = re.compile(
    r"\b(by\s+(?:end\s+of\s+\w+|next\s+\w+|this\s+\w+|\w+day|"
    r"the\s+\w+|tomorrow|today|monday|tuesday|wednesday|thursday|"
    r"friday|saturday|sunday|q\d|early\s+next\s+week|first\s+week\s+of\s+\w+|"
    r"march|april|may|june|july|august|\w+\s+\d{1,2}))\b",
    re.IGNORECASE,
)


def parse_action(item: str) -> dict:
    """Pull owner + deadline phrase out of a single action-item string."""
    m = OWNER_RE.match(item.strip())
    owner = m.group(1).strip() if m else "(unassigned)"
    body = m.group(2).strip() if m else item.strip()
    d = DEADLINE_RE.search(body)
    deadline = d.group(1) if d else ""
    return {"owner": owner, "body": body, "deadline_phrase": deadline}


def build_action_frame(meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """Long-format frame: one row per action item across the dataset."""
    rows = []
    for _, m in meetings_frame.iterrows():
        for raw in m["action_items"]:
            parsed = parse_action(raw)
            rows.append({
                "meeting_id": m["meeting_id"],
                "title": m["title"],
                "call_type": m["call_type"],
                "primary_theme": m["primary_theme"],
                "external_domains": m["external_domains"],
                "start_time": m["start_time"],
                "owner": parsed["owner"],
                "deadline_phrase": parsed["deadline_phrase"],
                "action": parsed["body"],
                "raw": raw,
            })
    return pd.DataFrame(rows)


def actions_per_owner(action_frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate by owner: how many actions, how many customer-facing,
       and the call types they span."""
    g = action_frame.groupby("owner")
    df = g.agg(
        n_actions=("action", "count"),
        n_customer_facing=("call_type", lambda s: int((s == "external").sum())),
        n_support=("call_type", lambda s: int((s == "support").sum())),
        n_internal=("call_type", lambda s: int((s == "internal").sum())),
        themes=("primary_theme", lambda s: ", ".join(sorted(set(s)))),
    )
    return df.sort_values("n_actions", ascending=False)


def actions_per_customer(action_frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate commitments BY customer (external + support only)."""
    df = action_frame[action_frame["external_domains"] != ""].copy()
    df["customer"] = df["external_domains"].str.split(",").str[0].str.strip()
    g = df.groupby("customer")["action"].agg(["count"]).rename(columns={"count": "open_commitments"})
    return g.sort_values("open_commitments", ascending=False)
