"""Console-script entry points that don't naturally live in a single module."""

from __future__ import annotations

import argparse


def walkthrough() -> int:
    """Entry point for `ti-walkthrough`.

    Mirrors `scripts/walkthrough.py` so it works after `pip install` too.
    """
    from .data_loader import load_all, meetings_to_frame, utterances_to_frame
    from .call_type_classifier import add_call_type_to_frame
    from .topic_categorizer import categorize_all, cluster_sanity_check
    from .sentiment_analyzer import (
        per_utterance_score_frame,
        sentiment_by_call_type,
        sentiment_by_theme,
        weekly_sentiment_trend,
    )
    from .churn_risk import per_customer_churn_score
    from .action_item_tracker import (
        actions_per_customer,
        actions_per_owner,
        build_action_frame,
    )
    from .narrative_tracer import narrative_summary_stats, trace_narrative
    from .conversation_dynamics import coaching_flags, per_meeting_dynamics

    ap = argparse.ArgumentParser(description="Walk through every analysis module.")
    ap.add_argument("--data", required=True, help="Dataset directory.")
    args = ap.parse_args()

    def banner(t: str) -> None:
        print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")

    banner("STEP 1 — Load")
    meetings = load_all(args.data)
    mf = meetings_to_frame(meetings)
    uf = utterances_to_frame(meetings)
    print(f"Loaded {len(meetings)} meetings, {len(uf):,} utterances")

    banner("STEP 2 — Call type classification")
    mf = add_call_type_to_frame(mf, meetings)
    print(mf["call_type"].value_counts())

    banner("STEP 3 — Theme categorization")
    mf = categorize_all(mf)
    print(mf["primary_theme"].value_counts())
    cluster_df, _ = cluster_sanity_check(meetings, k=8)
    print("\nTF-IDF cluster sanity check:")
    print(cluster_df.to_string(index=False))

    banner("STEP 4 — Sentiment")
    uf = per_utterance_score_frame(uf)
    print(sentiment_by_call_type(mf))
    print(sentiment_by_theme(mf))
    print(weekly_sentiment_trend(mf).pivot(index="week", columns="call_type",
                                            values="sentiment_score"))

    banner("STEP 5 — BONUS #1: Churn risk")
    print(per_customer_churn_score(meetings, mf).head(10).to_string(index=False))

    banner("STEP 6 — BONUS #2: Action items")
    af = build_action_frame(mf)
    print(actions_per_owner(af).head(10).to_string())
    print(actions_per_customer(af).head(10).to_string())

    banner("STEP 7 — BONUS #3: Narratives")
    for label, anchors in [
        ("Detect Outage", ["detect outage", "detect pipeline failure"]),
        ("Comply v2 launch", ["comply v2"]),
        ("SentinelShield", ["sentinelshield"]),
    ]:
        print(f"{label}: {narrative_summary_stats(trace_narrative(meetings, anchors))}")

    banner("STEP 8 — BONUS #4: Conversation dynamics")
    flags = coaching_flags(per_meeting_dynamics(meetings), mf)
    print(f"Calls with coaching flag: {(flags.coaching_flags != '').sum()} / {len(flags)}")

    print("\n✓ Walkthrough complete.")
    return 0
