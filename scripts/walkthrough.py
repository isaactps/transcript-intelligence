#!/usr/bin/env python3
"""
walkthrough.py — interactive console walkthrough of every analysis module.

Mirrors what the (now-deleted) reference notebook used to show: prints the
key DataFrame from each module so a reviewer can see a representative result
without opening anything.

Usage:
    python scripts/walkthrough.py --data /path/to/dataset
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence import (
    actions_per_customer,
    actions_per_owner,
    add_call_type_to_frame,
    build_action_frame,
    categorize_all,
    cluster_sanity_check,
    coaching_flags,
    customer_trajectory,
    in_call_sentiment_swing,
    load_all,
    meetings_to_frame,
    narrative_summary_stats,
    per_customer_churn_score,
    per_meeting_dynamics,
    per_utterance_score_frame,
    sentiment_by_call_type,
    sentiment_by_theme,
    sentiment_distribution_matrix,
    trace_narrative,
    utterances_to_frame,
    weekly_sentiment_trend,
)


def banner(text: str) -> None:
    print(f"\n{'=' * 78}\n{text}\n{'=' * 78}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Walkthrough of every analysis module.")
    ap.add_argument("--data", required=True, help="Path to dataset directory.")
    args = ap.parse_args()

    banner("STEP 1 — Load the data")
    meetings = load_all(args.data)
    mf = meetings_to_frame(meetings)
    uf = utterances_to_frame(meetings)
    print(f"Loaded {len(meetings)} meetings, {len(uf):,} utterances")

    banner("STEP 2 — Call type classification")
    mf = add_call_type_to_frame(mf, meetings)
    print(mf["call_type"].value_counts())
    for ct in ["support", "external", "internal"]:
        print(f"\n--- {ct.upper()} samples ---")
        for t in mf[mf.call_type == ct]["title"].head(3):
            print(" •", t)

    banner("STEP 3 — Topic / theme categorization")
    mf = categorize_all(mf)
    print("Primary theme distribution:")
    print(mf["primary_theme"].value_counts())
    print("\nTF-IDF cluster sanity check:")
    cluster_df, _ = cluster_sanity_check(meetings, k=8)
    print(cluster_df.to_string(index=False))

    banner("STEP 4 — Sentiment analysis")
    uf = per_utterance_score_frame(uf)
    print("\nBy call type:")
    print(sentiment_by_call_type(mf))
    print("\nBy theme:")
    print(sentiment_by_theme(mf))
    print("\nWeekly trend (pivoted):")
    print(weekly_sentiment_trend(mf).pivot(index="week", columns="call_type",
                                           values="sentiment_score"))
    print("\nDistribution matrix:")
    print(sentiment_distribution_matrix(mf))
    print("\nLargest customer-trajectory drops:")
    traj = customer_trajectory(mf)
    drops = traj.dropna(subset=["delta_vs_prev"]).sort_values("delta_vs_prev").head(5)
    print(drops[["customer", "title", "sentiment_score",
                 "prev_score", "delta_vs_prev"]].to_string(index=False))

    banner("STEP 5 — BONUS #1: Churn risk")
    churn = per_customer_churn_score(meetings, mf)
    print(churn.head(10)[["customer", "n_calls", "avg_sentiment", "min_sentiment",
                           "risk_score", "risk_bucket", "reasons"]].to_string(index=False))

    banner("STEP 6 — BONUS #2: Action item / commitment tracker")
    af = build_action_frame(mf)
    print(f"Total: {len(af)} action items, "
          f"{(af.owner != '(unassigned)').sum()} with owner, "
          f"{(af.deadline_phrase != '').sum()} with deadline phrase")
    print("\nTop-10 owners by load:")
    print(actions_per_owner(af).head(10).to_string())
    print("\nTop-10 customers by open commitments:")
    print(actions_per_customer(af).head(10).to_string())

    banner("STEP 7 — BONUS #3: Cross-call narrative tracing")
    for label, anchors in [
        ("Detect Outage", ["detect outage", "detect pipeline failure",
                           "detect reliability", "detect latency"]),
        ("Comply v2 launch", ["comply v2"]),
        ("SentinelShield competitive pressure", ["sentinelshield"]),
    ]:
        t = trace_narrative(meetings, anchors)
        print(f"\n{label}: {narrative_summary_stats(t)}")

    banner("STEP 8 — BONUS #4: Conversation dynamics")
    dyn = per_meeting_dynamics(meetings)
    flags = coaching_flags(dyn, mf)
    flagged = flags[flags.coaching_flags != ""]
    print(f"Calls with at least one coaching flag: {len(flagged)} / {len(flags)}")
    print(flagged[["title", "call_type", "aegis_talk_pct",
                   "customer_talk_pct", "coaching_flags"]].head(10).to_string(index=False))

    banner("STEP 9 — In-call sentiment swings")
    swings = in_call_sentiment_swing(uf).sort_values("swing", ascending=False)
    print("\nMost positive swings (negative → positive):")
    print(swings.head(5).to_string(index=False))
    print("\nMost negative swings (positive → negative):")
    print(swings.tail(5).to_string(index=False))

    print("\n✓ Walkthrough complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
