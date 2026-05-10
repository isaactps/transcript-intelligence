"""
conversation_dynamics.py
------------------------
BONUS INSIGHT #4 — Conversation dynamics / call-coaching metrics.

WHO CARES?
  Sales managers and CS managers coaching their teams. Support managers
  benchmarking their reps. Product managers analyzing customer voice.

WHAT WE COMPUTE PER MEETING:
  * Talk-time per speaker (seconds)
  * Talk-time ratio (Aegis-side vs customer-side, when applicable)
  * Number of turns per speaker
  * "Customer voice share" — how much air-time the customer got vs the
    Aegis rep on external/support calls

THE COACHING SIGNAL:
  In renewal/external calls, top-performing reps tend to LISTEN more than
  they talk. A persistent pattern of Aegis dominating talk-time on
  customer calls is a coaching opportunity. Conversely, on a support call
  where the customer is talking >70%, the rep may not be steering the
  resolution.
"""

from __future__ import annotations

from collections import defaultdict

import pandas as pd

INTERNAL_DOMAIN = "aegiscloud.com"


def _speaker_is_aegis(speaker_name: str, all_emails: list[str]) -> bool:
    """
    Decide whether a speaker is Aegis-side.

    Strategy: every email maps to a domain. We try to match the speaker's
    name to an email by checking if any token of the email's local-part
    (split on . / _) appears as a case-insensitive substring of the
    speaker name, OR if the last name portion matches.

    If we can't match the speaker to any email, default to Aegis only when
    ALL attendees are Aegis (otherwise unknown → customer, since the
    typical pattern is 1-2 Aegis reps + 1-2 named customer attendees).
    """
    if not speaker_name:
        return True  # treat unknowns as Aegis

    name_tokens = [t.lower().strip("'.") for t in speaker_name.split() if t]
    if not name_tokens:
        return True

    # Domains in the meeting
    domains = {e.split("@")[-1].lower() for e in all_emails}
    only_aegis = domains == {INTERNAL_DOMAIN}
    if only_aegis:
        return True

    # Try to match speaker tokens to email local-parts
    for e in all_emails:
        local, _, domain = e.partition("@")
        local_tokens = [t.lower() for t in local.replace("_", ".").split(".") if t]
        # First-name match OR last-name match OR initial+lastname match
        match = False
        # Last-name token match (most reliable)
        if local_tokens and local_tokens[-1] in name_tokens:
            match = True
        # First-name match (less reliable but ok)
        elif local_tokens and local_tokens[0] in name_tokens:
            # Avoid matching "t.hargrove" → "thomas" with an empty/short token
            if len(local_tokens[0]) >= 3:
                match = True
            elif len(local_tokens) > 1 and local_tokens[1] in name_tokens:
                match = True  # initial+last form like t.hargrove

        if match:
            return domain == INTERNAL_DOMAIN

    # Couldn't match — treat as customer (the safer assumption when there
    # are external attendees and we couldn't tag the speaker).
    return False


def per_meeting_dynamics(meetings) -> pd.DataFrame:
    """Compute talk-time and turn-count per speaker per meeting."""
    rows = []
    for m in meetings:
        # Talk-time per speaker
        talk = defaultdict(float)
        turns = defaultdict(int)
        for u in m.transcript:
            spk = u.get("speaker_name") or "?"
            secs = max(0.0, (u.get("endTime", 0) or 0) - (u.get("time", 0) or 0))
            talk[spk] += secs
            turns[spk] += 1
        total = sum(talk.values()) or 1.0

        emails = m.all_emails
        aegis_secs = 0.0
        cust_secs = 0.0
        for spk, secs in talk.items():
            if _speaker_is_aegis(spk, emails):
                aegis_secs += secs
            else:
                cust_secs += secs
        denom = aegis_secs + cust_secs or 1.0
        rows.append({
            "meeting_id": m.meeting_id,
            "title": m.title,
            "n_speakers": len(talk),
            "total_talk_sec": round(total, 1),
            "aegis_talk_pct": round(100 * aegis_secs / denom, 1),
            "customer_talk_pct": round(100 * cust_secs / denom, 1),
            "longest_speaker": max(talk, key=talk.get) if talk else "",
            "longest_speaker_pct": round(100 * max(talk.values()) / total, 1) if talk else 0.0,
        })
    return pd.DataFrame(rows)


def coaching_flags(dynamics_frame: pd.DataFrame, meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Join dynamics with the wide meetings frame and flag coaching opportunities.

    Calibration note: across THIS dataset Aegis-side talk-time on external
    calls averages ~57% (median 58%). We use slightly tighter thresholds:
      * External call where Aegis talks >65% → "Aegis-heavy" (worth a look)
      * Support call where customer talks <35% → "Limited customer input"
      * Single Aegis speaker takes >50% on a multi-speaker external call →
        rep dominating; co-presenters not getting space
    """
    df = dynamics_frame.merge(meetings_frame[["meeting_id", "call_type"]], on="meeting_id")
    flags = []
    for _, r in df.iterrows():
        f = []
        if r.call_type == "external" and r.aegis_talk_pct > 65:
            f.append(f"Aegis-heavy external call ({r.aegis_talk_pct:.0f}% Aegis)")
        if r.call_type == "support" and r.customer_talk_pct < 35:
            f.append(f"Limited customer input on support call ({r.customer_talk_pct:.0f}% cust)")
        if r.call_type != "internal" and r.n_speakers >= 3 and r.longest_speaker_pct > 50:
            f.append(f"{r.longest_speaker} held the floor ({r.longest_speaker_pct:.0f}%)")
        flags.append("; ".join(f))
    df["coaching_flags"] = flags
    return df
