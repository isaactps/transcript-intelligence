"""
sentiment_analyzer.py
---------------------
Compute sentiment trends across call types and themes.

DATA AVAILABILITY:
  Each meeting has:
    * `overallSentiment`  — categorical: very-negative .. very-positive
    * `sentimentScore`    — float on a 1..5 scale (1 worst, 5 best)
    * Per-utterance `sentimentType` — neutral / positive / negative

  These are pre-computed by the upstream transcription/intelligence pipeline.
  We TRUST and AGGREGATE them rather than re-running a sentiment model.

WHY TRUST THE PRE-LABELS?
  * Per-utterance sentiment is hard to outperform with a vanilla off-the-shelf
    model on conversational data; the upstream model has full context.
  * Re-running a model would introduce inconsistency between the score the
    user sees in the source data and what we report.
  * Our value-add is AGGREGATION + TREND DETECTION, not raw labelling.

WHAT WE COMPUTE:

  1. Distribution of sentiment by call_type and primary_theme.
  2. Sentiment over TIME (weekly), to surface trends like "external sentiment
     dropped in mid-March" — that's the Detect outage signal.
  3. Per-customer sentiment trajectory — flag accounts whose sentiment is
     trending DOWN call-over-call.
  4. Sentiment "swing" within a single call (start vs end). A call that
     starts very-negative but ends mixed-positive is a recovered situation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def utterance_sentiment_to_score(s: str) -> float:
    """Map per-utterance label to a numeric value for averaging."""
    return {"positive": 1.0, "negative": -1.0, "neutral": 0.0}.get(s, 0.0)


def per_utterance_score_frame(utterance_frame: pd.DataFrame) -> pd.DataFrame:
    """Add a numeric `score` column to the long utterance frame."""
    out = utterance_frame.copy()
    out["score"] = out["sentiment"].map(utterance_sentiment_to_score)
    return out


def sentiment_by_call_type(meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """Mean and distribution of meeting sentiment_score grouped by call_type."""
    g = meetings_frame.groupby("call_type")["sentiment_score"]
    df = g.agg(["count", "mean", "median", "std", "min", "max"]).round(2)
    return df.sort_values("mean")


def sentiment_by_theme(meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """Mean meeting sentiment_score by primary theme."""
    g = meetings_frame.groupby("primary_theme")["sentiment_score"]
    df = g.agg(["count", "mean", "std"]).round(2).sort_values("mean")
    return df


def sentiment_distribution_matrix(meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab: rows=call_type, cols=overall_sentiment label."""
    order = ["very-negative", "negative", "mixed-negative",
             "mixed-positive", "positive", "very-positive"]
    ct = pd.crosstab(meetings_frame["call_type"], meetings_frame["overall_sentiment"])
    # Reorder columns; some may be missing in a given grouping
    cols = [c for c in order if c in ct.columns]
    return ct[cols]


def weekly_sentiment_trend(meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """Mean sentiment_score per (week, call_type)."""
    df = meetings_frame.copy()
    df["week"] = df["start_time"].dt.tz_convert(None).dt.to_period("W").apply(lambda p: p.start_time)
    g = df.groupby(["week", "call_type"])["sentiment_score"].mean().reset_index()
    return g


def in_call_sentiment_swing(utterance_frame: pd.DataFrame) -> pd.DataFrame:
    """
    For each meeting, compute the sentiment score in the FIRST and LAST
    third of the call. A negative-to-positive swing is a great sign for
    account health. The reverse is alarming.
    """
    out = []
    for mid, group in utterance_frame.groupby("meeting_id"):
        scores = group["sentiment"].map(utterance_sentiment_to_score).values
        if len(scores) < 6:
            continue
        third = max(1, len(scores) // 3)
        first_avg = scores[:third].mean()
        last_avg = scores[-third:].mean()
        out.append({
            "meeting_id": mid,
            "first_third_score": round(float(first_avg), 3),
            "last_third_score": round(float(last_avg), 3),
            "swing": round(float(last_avg - first_avg), 3),
        })
    return pd.DataFrame(out)


def customer_trajectory(meetings_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Per-customer sentiment trajectory: for each non-Aegis domain that
    appears in 2+ calls, track the sentiment_score over time.

    Returns one row per (customer, call) sorted by time, with a `delta`
    showing the change vs the customer's previous call.
    """
    rows = []
    df = meetings_frame.copy()
    df = df.sort_values("start_time")
    for _, row in df.iterrows():
        if not row["external_domains"]:
            continue
        for dom in [d.strip() for d in row["external_domains"].split(",") if d.strip()]:
            rows.append({
                "customer": dom,
                "meeting_id": row["meeting_id"],
                "start_time": row["start_time"],
                "title": row["title"],
                "call_type": row["call_type"],
                "sentiment_score": row["sentiment_score"],
                "primary_theme": row["primary_theme"],
            })
    df = pd.DataFrame(rows).sort_values(["customer", "start_time"])
    df["prev_score"] = df.groupby("customer")["sentiment_score"].shift(1)
    df["delta_vs_prev"] = (df["sentiment_score"] - df["prev_score"]).round(2)
    return df
