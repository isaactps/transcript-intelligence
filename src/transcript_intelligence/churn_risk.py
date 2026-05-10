"""
churn_risk.py
-------------
BONUS INSIGHT #1 — Account-level churn-risk scoring.

WHO CARES?
  Customer Success leadership, sales managers, the renewal forecasting team.
  Today, CS leaders manually scan call notes one account at a time.
  This automates that scan into a ranked list with explanations.

HOW IT WORKS:
  We compute a per-customer "churn risk score" from four independent signals
  visible across their meetings:

    A. Sentiment trajectory      — has their average score dropped from a
                                   prior baseline? Has any single call
                                   bottomed out below 2.5?
    B. Churn-signal moments      — count of `keyMoments` with type
                                   `churn_signal` across their calls.
    C. Competitive mentions      — competitor names appearing in transcripts
                                   (SentinelShield is the big one in this
                                   dataset).
    D. Reliability/SLA breach    — meetings tagged with outage or sla breach
                                   topics. Outages drive churn.

  Each signal contributes 0..3 points; total = 0..12. We bucket into
  Low (<3), Medium (3-6), High (7+).

WHY THIS APPROACH?
  Each signal is independent and explainable. A CS lead can see WHY a
  customer is flagged ("3 recent churn-signal moments + 1 competitor
  mention + sentiment dropped from 4.7 to 1.6"). That's directly actionable,
  unlike a black-box risk score.

LIMITATIONS:
  This is a heuristic; with more data we'd train a real model. With a wider
  range of customers we'd also normalize by account tier and tenure.
"""

from __future__ import annotations

import re
from collections import defaultdict

import pandas as pd

# Known competitor names mentioned in the transcripts. In production we'd
# pull this from a competitive-intel knowledge base.
COMPETITORS = ["sentinelshield", "sentinel shield"]

CHURN_KEYMOMENT_TYPES = {"churn_signal"}
NEGATIVE_KEYMOMENT_TYPES = {"churn_signal", "concern", "escalation"}


def _competitor_mentions(text: str) -> list[str]:
    """Find competitor names in a single transcript blob."""
    found = []
    low = text.lower()
    for c in COMPETITORS:
        if re.search(rf"\b{re.escape(c)}\b", low):
            found.append(c)
    return found


def per_customer_churn_score(meetings, meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-customer churn-risk score with explanations.

    Returns a DataFrame ranked from highest to lowest risk.
    """
    # Map meeting_id -> Meeting object for easy access to transcript text
    by_id = {m.meeting_id: m for m in meetings}

    # Group rows of meetings_frame by external customer domain
    customer_data: dict[str, list[dict]] = defaultdict(list)
    for _, row in meetings_frame.iterrows():
        if not row["external_domains"]:
            continue
        for dom in [d.strip() for d in row["external_domains"].split(",") if d.strip()]:
            customer_data[dom].append(row)

    rows = []
    for customer, calls in customer_data.items():
        scores = [r["sentiment_score"] for r in calls]
        # ----- Signal A: sentiment trajectory -----
        n_calls = len(calls)
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        signal_a = 0
        if min_score <= 2.0:
            signal_a += 2
        elif min_score <= 2.5:
            signal_a += 1
        if n_calls >= 2:
            # If the most recent call is >= 1.0 lower than the FIRST call
            calls_sorted = sorted(calls, key=lambda r: r["start_time"])
            first_score = calls_sorted[0]["sentiment_score"]
            last_score = calls_sorted[-1]["sentiment_score"]
            if last_score - first_score <= -1.0:
                signal_a += 1

        # ----- Signal B: churn-signal key moments -----
        n_churn_moments = 0
        for r in calls:
            for k in by_id[r["meeting_id"]].key_moments:
                if k.get("type", "") in CHURN_KEYMOMENT_TYPES:
                    n_churn_moments += 1
        signal_b = min(3, n_churn_moments)  # cap at 3

        # ----- Signal C: competitor mentions -----
        comp_mentions = []
        for r in calls:
            comp_mentions.extend(_competitor_mentions(by_id[r["meeting_id"]].full_text))
        n_comp = len(set(comp_mentions))  # number of unique competitors mentioned
        n_comp_total = len(comp_mentions) # total mentions
        signal_c = 0
        if n_comp_total >= 5:
            signal_c = 3
        elif n_comp_total >= 2:
            signal_c = 2
        elif n_comp_total >= 1:
            signal_c = 1

        # ----- Signal D: reliability / SLA-breach exposure -----
        reliability_topics = {"outage", "sla breach", "incident response",
                              "platform outage", "service outage",
                              "infrastructure reliability"}
        n_reliability = sum(
            1 for r in calls
            for t in r["topics"] if t in reliability_topics
        )
        signal_d = min(3, n_reliability)

        total = signal_a + signal_b + signal_c + signal_d
        bucket = "High" if total >= 7 else "Medium" if total >= 3 else "Low"

        # Reasons string
        reasons = []
        if signal_a:
            reasons.append(f"sentiment dipped (min {min_score:.1f}, avg {avg_score:.1f})")
        if signal_b:
            reasons.append(f"{n_churn_moments} churn-signal moment(s)")
        if signal_c:
            reasons.append(f"{n_comp_total} competitor mention(s) [{', '.join(set(comp_mentions))}]")
        if signal_d:
            reasons.append(f"{n_reliability} reliability/SLA topic hit(s)")

        rows.append({
            "customer": customer,
            "n_calls": n_calls,
            "avg_sentiment": round(avg_score, 2),
            "min_sentiment": round(min_score, 2),
            "signal_A_sentiment": signal_a,
            "signal_B_churn_moments": signal_b,
            "signal_C_competitor": signal_c,
            "signal_D_reliability": signal_d,
            "risk_score": total,
            "risk_bucket": bucket,
            "reasons": "; ".join(reasons) if reasons else "(no signals)",
        })

    df = pd.DataFrame(rows).sort_values("risk_score", ascending=False)
    return df.reset_index(drop=True)
