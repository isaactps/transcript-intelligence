"""
pipeline.py
-----------
End-to-end orchestration: ingest → enrich → analyze → save.

Run: python pipeline.py [--data PATH] [--out PATH]

Outputs (under --out, default /home/claude/work/transcript_intelligence/outputs):
  meetings.csv             — wide frame with call_type, primary_theme, sentiment
  utterances.csv           — long frame, one row per spoken sentence
  action_items.csv         — parsed action items
  churn_risk.csv           — per-customer churn risk ranking
  conversation_dynamics.csv— talk-time + coaching flags
  narrative_*.csv          — outage / launch / competitive narratives
  insights.json            — top-line summary stats for the deck
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .action_item_tracker import (actions_per_customer, actions_per_owner,
                                 build_action_frame)
from .call_type_classifier import add_call_type_to_frame
from .churn_risk import per_customer_churn_score
from .conversation_dynamics import coaching_flags, per_meeting_dynamics
from .data_loader import load_all, meetings_to_frame, utterances_to_frame
from .narrative_tracer import narrative_summary_stats, trace_narrative
from .sentiment_analyzer import (customer_trajectory, in_call_sentiment_swing,
                                per_utterance_score_frame, sentiment_by_call_type,
                                sentiment_by_theme,
                                sentiment_distribution_matrix,
                                weekly_sentiment_trend)
from .topic_categorizer import categorize_all, cluster_sanity_check


def run(data_dir: str, out_dir: str) -> dict:
    """Run the full pipeline and write outputs."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/8] Loading transcripts from {data_dir} …")
    meetings = load_all(data_dir)
    print(f"      → {len(meetings)} meetings loaded")

    print("[2/8] Building wide meeting frame + classifying call types …")
    mf = meetings_to_frame(meetings)
    mf = add_call_type_to_frame(mf, meetings)

    print("[3/8] Categorizing topics into themes …")
    mf = categorize_all(mf)

    print("[4/8] Building utterance long frame …")
    uf = utterances_to_frame(meetings)
    uf = per_utterance_score_frame(uf)

    print("[5/8] Sentiment aggregations …")
    sent_by_ct = sentiment_by_call_type(mf)
    sent_by_theme = sentiment_by_theme(mf)
    sent_matrix = sentiment_distribution_matrix(mf)
    weekly = weekly_sentiment_trend(mf)
    swings = in_call_sentiment_swing(uf).sort_values("swing", ascending=False)
    traj = customer_trajectory(mf)

    print("[6/8] Bonus insights …")
    af = build_action_frame(mf)
    apo = actions_per_owner(af)
    apc = actions_per_customer(af)
    churn = per_customer_churn_score(meetings, mf)
    dyn = per_meeting_dynamics(meetings)
    flags = coaching_flags(dyn, mf)

    print("[7/8] Narrative tracing …")
    n_outage = trace_narrative(meetings, ["detect outage", "detect pipeline failure",
                                           "detect reliability", "detect latency"])
    n_launch = trace_narrative(meetings, ["comply v2"])
    n_compete = trace_narrative(meetings, ["sentinelshield"])

    print("[8/8] Persisting CSVs + insights JSON …")
    # Note: meetings_frame contains list/dict columns — drop them from CSV
    mf_to_csv = mf.copy()
    for c in ["topics", "action_items", "key_moment_types",
              "secondary_themes", "theme_scores"]:
        if c in mf_to_csv.columns:
            mf_to_csv[c] = mf_to_csv[c].apply(lambda v: json.dumps(v, default=str)
                                              if not isinstance(v, str) else v)
    mf_to_csv.to_csv(out / "meetings.csv", index=False)
    uf.to_csv(out / "utterances.csv", index=False)
    af.to_csv(out / "action_items.csv", index=False)
    apo.to_csv(out / "actions_per_owner.csv")
    apc.to_csv(out / "actions_per_customer.csv")
    churn.to_csv(out / "churn_risk.csv", index=False)
    flags.to_csv(out / "conversation_dynamics.csv", index=False)
    n_outage.to_csv(out / "narrative_detect_outage.csv", index=False)
    n_launch.to_csv(out / "narrative_comply_v2_launch.csv", index=False)
    n_compete.to_csv(out / "narrative_sentinelshield.csv", index=False)
    sent_by_ct.to_csv(out / "sentiment_by_call_type.csv")
    sent_by_theme.to_csv(out / "sentiment_by_theme.csv")
    sent_matrix.to_csv(out / "sentiment_distribution_matrix.csv")
    weekly.to_csv(out / "weekly_sentiment.csv", index=False)
    swings.to_csv(out / "in_call_swings.csv", index=False)
    traj.to_csv(out / "customer_trajectories.csv", index=False)

    # Top-line summary for the deck
    insights = {
        "n_meetings": len(meetings),
        "n_utterances": len(uf),
        "n_action_items": len(af),
        "call_type_counts": mf["call_type"].value_counts().to_dict(),
        "primary_theme_counts": mf["primary_theme"].value_counts().to_dict(),
        "sentiment_by_call_type": sent_by_ct.to_dict(),
        "sentiment_by_theme": sent_by_theme.to_dict(),
        "high_risk_accounts": churn.head(5)[["customer", "risk_score",
                                              "risk_bucket", "reasons"]
                                            ].to_dict(orient="records"),
        "narrative_outage": narrative_summary_stats(n_outage),
        "narrative_launch": narrative_summary_stats(n_launch),
        "narrative_compete": narrative_summary_stats(n_compete),
        "top_owners_by_action_count": apo.head(5).reset_index().to_dict(orient="records"),
        "n_calls_with_coaching_flag": int((flags["coaching_flags"] != "").sum()),
    }
    with open(out / "insights.json", "w") as f:
        json.dump(insights, f, indent=2, default=str)

    print(f"\n✓ Done. Outputs in {out}")
    return insights

def _cli() -> int:
    """Entry point for the `ti-pipeline` console script."""
    ap = argparse.ArgumentParser(description="Run the full pipeline end-to-end.")
    ap.add_argument("--data", required=True, help="Dataset directory.")
    ap.add_argument("--out", default="outputs", help="Output directory (default: ./outputs).")
    args = ap.parse_args()
    insights = run(args.data, args.out)
    print("\n=== Top-line insights ===")
    print(json.dumps(insights, indent=2, default=str)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
