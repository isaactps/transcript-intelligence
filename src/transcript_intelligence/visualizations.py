"""
visualizations.py
-----------------
Render the charts the slide deck needs.

Each chart is exported as a high-DPI PNG in /outputs/figures/.
The visual style is consistent — palette derived from the narrative:
   navy (#1E2761) — primary
   coral/orange (#E6754F) — alarming / negative signal
   teal (#3CA39A) — positive / growth
   slate gray (#4B5563) — neutral
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .action_item_tracker import build_action_frame
from .call_type_classifier import add_call_type_to_frame
from .churn_risk import per_customer_churn_score
from .conversation_dynamics import coaching_flags, per_meeting_dynamics
from .data_loader import load_all, meetings_to_frame, utterances_to_frame
from .narrative_tracer import trace_narrative
from .sentiment_analyzer import (per_utterance_score_frame, sentiment_by_call_type,
                                sentiment_by_theme,
                                sentiment_distribution_matrix,
                                weekly_sentiment_trend)
from .topic_categorizer import categorize_all

# --- Visual style ---
NAVY = "#1E2761"
CORAL = "#E6754F"
TEAL = "#3CA39A"
SLATE = "#4B5563"
LIGHT = "#F4F5F7"
MUTED = "#9CA3AF"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": SLATE,
    "axes.titlecolor": NAVY,
    "axes.titleweight": "bold",
    "xtick.color": SLATE,
    "ytick.color": SLATE,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def fig_call_type_distribution(mf: pd.DataFrame, out: Path):
    counts = mf["call_type"].value_counts()
    fig, ax = plt.subplots(figsize=(7.5, 4))
    colors = {"external": NAVY, "internal": TEAL, "support": CORAL}
    bars = ax.bar(counts.index, counts.values,
                  color=[colors[c] for c in counts.index], width=0.6)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width()/2, v + 0.7, str(v),
                ha="center", fontsize=12, fontweight="bold", color=SLATE)
    ax.set_ylim(0, max(counts.values) * 1.15)
    ax.set_ylabel("Number of meetings")
    ax.set_title("Call distribution across the 100-meeting sample")
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "01_call_type_distribution.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_theme_distribution(mf: pd.DataFrame, out: Path):
    counts = mf["primary_theme"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    bars = ax.barh(counts.index, counts.values, color=NAVY, height=0.65)
    for b, v in zip(bars, counts.values):
        ax.text(v + 0.4, b.get_y() + b.get_height()/2, str(v),
                va="center", fontsize=11, color=SLATE)
    ax.set_xlim(0, max(counts.values) * 1.1)
    ax.set_xlabel("Number of meetings")
    ax.set_title("Themes by meeting volume")
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "02_theme_distribution.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_sentiment_by_call_type(mf: pd.DataFrame, out: Path):
    df = sentiment_by_call_type(mf).reset_index()
    fig, ax = plt.subplots(figsize=(7.5, 4))
    colors = {"external": NAVY, "internal": TEAL, "support": CORAL}
    bars = ax.bar(df["call_type"], df["mean"],
                  color=[colors[c] for c in df["call_type"]], width=0.6)
    # Draw error bars (std)
    ax.errorbar(df["call_type"], df["mean"], yerr=df["std"],
                fmt="none", ecolor=SLATE, capsize=6, capthick=1.2, alpha=0.7)
    for b, v in zip(bars, df["mean"]):
        ax.text(b.get_x() + b.get_width()/2, v + 0.08, f"{v:.2f}",
                ha="center", fontsize=12, fontweight="bold", color=SLATE)
    ax.axhline(3.0, color=MUTED, linestyle="--", linewidth=1, alpha=0.6)
    ax.text(2.4, 3.05, "neutral baseline (3.0)", color=MUTED,
            fontsize=9, ha="right", va="bottom")
    ax.set_ylim(0, 5)
    ax.set_ylabel("Mean sentiment score (1-5 scale)")
    ax.set_title("Sentiment skew by call type — support drags lowest")
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "03_sentiment_by_call_type.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_sentiment_by_theme(mf: pd.DataFrame, out: Path):
    df = sentiment_by_theme(mf).reset_index().sort_values("mean")
    fig, ax = plt.subplots(figsize=(8.5, 5))
    # Color bars by mean: red below 3, green above 4, slate in between
    bar_colors = [CORAL if m < 3 else (TEAL if m >= 4 else NAVY) for m in df["mean"]]
    bars = ax.barh(df["primary_theme"], df["mean"], color=bar_colors, height=0.65)
    for b, v in zip(bars, df["mean"]):
        ax.text(v + 0.05, b.get_y() + b.get_height()/2, f"{v:.2f}",
                va="center", fontsize=11, fontweight="bold", color=SLATE)
    ax.axvline(3.0, color=MUTED, linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlim(0, 5)
    ax.set_xlabel("Mean sentiment score (1-5 scale)")
    ax.set_title("Sentiment by theme — Reliability is the wound")
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "04_sentiment_by_theme.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_weekly_sentiment(mf: pd.DataFrame, out: Path):
    weekly = weekly_sentiment_trend(mf)
    pivot = weekly.pivot(index="week", columns="call_type", values="sentiment_score")
    fig, ax = plt.subplots(figsize=(11, 4.6))
    colors = {"external": NAVY, "internal": TEAL, "support": CORAL}
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], marker="o", linewidth=2.4,
                color=colors[col], label=col, markersize=6)
    # Shade the outage week
    outage_start = pd.Timestamp("2026-03-09")
    outage_end = pd.Timestamp("2026-03-22")
    ax.axvspan(outage_start, outage_end, color=CORAL, alpha=0.10, zorder=0)
    ax.text(outage_start + (outage_end - outage_start)/2, 4.65,
            "Detect outage window", color=CORAL, fontsize=10, fontweight="bold",
            ha="center", va="top")
    ax.set_ylim(1, 5)
    ax.set_ylabel("Mean weekly sentiment score")
    ax.set_xlabel("")
    ax.set_title("Weekly sentiment by call type — the outage is visible in the data")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "05_weekly_sentiment.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_outage_narrative(meetings, out: Path):
    """Timeline of the Detect outage narrative — with sentiment scores."""
    timeline = trace_narrative(
        meetings,
        ["detect outage", "detect pipeline failure", "detect reliability",
         "detect latency"]
    )
    if timeline.empty:
        return
    timeline = timeline.sort_values("start_time").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    colors = {"external": NAVY, "internal": TEAL, "support": CORAL}
    for ct, group in timeline.groupby("call_type"):
        ax.scatter(
            group["start_time"], group["sentiment_score"],
            s=110, c=colors[ct], alpha=0.85, edgecolor="white", linewidth=1.5,
            label=ct, zorder=3,
        )
    ax.plot(timeline["start_time"], timeline["sentiment_score"],
            color="#D1D5DB", linewidth=1, alpha=0.7, zorder=1)

    # Pick just 3-4 representative annotations spread across the timeline
    annotations = [
        ("INCIDENT: Detect Pipeline Failure", "war room", (10, 18)),
        ("Trailhead Marketplace Detect Alerts", "support fallout", (10, -22)),
        ("URGENT: Northstar Pharma compliance impact", "customer escalation", (10, 18)),
        ("Win/Loss Analysis - Q1", "still cited 6 weeks later", (10, -22)),
    ]
    used = set()
    for needle, label, offset in annotations:
        match = timeline[timeline["title"].str.contains(needle.split(":")[0], case=False, na=False)]
        match = match[~match.index.isin(used)]
        if match.empty:
            continue
        r = match.iloc[0]
        used.add(match.index[0])
        ax.annotate(
            label, (r["start_time"], r["sentiment_score"]),
            xytext=offset, textcoords="offset points",
            fontsize=9, color=NAVY, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=SLATE, lw=0.7),
        )

    ax.set_ylim(1, 5)
    ax.set_ylabel("Sentiment score (1-5)")
    ax.set_title(f"Detect Outage narrative — {len(timeline)} calls span "
                 f"{(timeline['start_time'].max() - timeline['start_time'].min()).days} days "
                 "across all three call types")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.axhline(3.0, color=MUTED, linestyle="--", linewidth=1, alpha=0.5)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out / "06_outage_narrative.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_churn_risk(meetings, mf: pd.DataFrame, out: Path):
    df = per_customer_churn_score(meetings, mf).head(10).iloc[::-1]  # reverse for barh
    bucket_color = {"High": CORAL, "Medium": "#F4A261", "Low": TEAL}
    colors = [bucket_color[b] for b in df["risk_bucket"]]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.barh(df["customer"], df["risk_score"], color=colors, height=0.6)
    for b, v, bucket in zip(bars, df["risk_score"], df["risk_bucket"]):
        ax.text(v + 0.15, b.get_y() + b.get_height()/2, f"{v}  ({bucket})",
                va="center", fontsize=10, fontweight="bold", color=SLATE)
    ax.set_xlim(0, 13)
    ax.set_xlabel("Churn risk score (0-12)")
    ax.set_title("Top-10 customers by churn risk score")
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    # Legend
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=bucket_color[b], label=b) for b in ["High", "Medium", "Low"]]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "07_churn_risk.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_actions_per_owner(mf: pd.DataFrame, out: Path):
    af = build_action_frame(mf)
    apo = (af.groupby("owner")
           .agg(n=("action", "count"),
                cust=("call_type", lambda s: int((s == "external").sum())))
           .sort_values("n", ascending=False)
           .head(10).iloc[::-1])
    fig, ax = plt.subplots(figsize=(9.5, 5))
    internal_part = apo["n"] - apo["cust"]
    ax.barh(apo.index, apo["cust"], color=NAVY, label="Customer-facing", height=0.65)
    ax.barh(apo.index, internal_part, left=apo["cust"], color=MUTED,
            label="Internal", height=0.65)
    for i, (idx, row) in enumerate(apo.iterrows()):
        ax.text(row["n"] + 0.4, i, str(int(row["n"])),
                va="center", fontsize=10, fontweight="bold", color=SLATE)
    ax.set_xlabel("Action items owned (across 100 meetings)")
    ax.set_title("Top-10 owners by action-item load")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "08_actions_per_owner.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_talktime_distribution(meetings, mf: pd.DataFrame, out: Path):
    dyn = per_meeting_dynamics(meetings)
    df = dyn.merge(mf[["meeting_id", "call_type"]], on="meeting_id")
    fig, ax = plt.subplots(figsize=(9, 4.6))
    # Boxplot of customer_talk_pct by call_type, but only external+support
    cats = ["external", "support"]
    data = [df[df.call_type == c]["customer_talk_pct"].values for c in cats]
    box = ax.boxplot(data, labels=[f"External\n(n={len(d)})" for d in data[:1]] +
                     [f"Support\n(n={len(d)})" for d in data[1:]],
                     patch_artist=True, widths=0.5,
                     medianprops=dict(color="white", linewidth=2),
                     boxprops=dict(linewidth=0),
                     whiskerprops=dict(color=SLATE),
                     capprops=dict(color=SLATE))
    for patch, color in zip(box["boxes"], [NAVY, CORAL]):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    ax.set_ylabel("Customer share of talk-time (%)")
    ax.set_title("Customer voice share — healthy balance overall, with outliers")
    ax.set_ylim(0, 60)
    ax.axhline(50, color=MUTED, linestyle="--", linewidth=1, alpha=0.6)
    ax.text(2.45, 50.7, "50/50 line", color=MUTED, fontsize=9)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E5E7EB", linestyle="-", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "09_talktime_distribution.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def render_all(data_dir: str, out_dir: str):
    out = Path(out_dir) / "figures"
    out.mkdir(parents=True, exist_ok=True)

    print(f"Loading {data_dir} …")
    meetings = load_all(data_dir)
    mf = meetings_to_frame(meetings)
    mf = add_call_type_to_frame(mf, meetings)
    mf = categorize_all(mf)

    print("Rendering charts …")
    fig_call_type_distribution(mf, out)
    fig_theme_distribution(mf, out)
    fig_sentiment_by_call_type(mf, out)
    fig_sentiment_by_theme(mf, out)
    fig_weekly_sentiment(mf, out)
    fig_outage_narrative(meetings, out)
    fig_churn_risk(meetings, mf, out)
    fig_actions_per_owner(mf, out)
    fig_talktime_distribution(meetings, mf, out)
    print(f"✓ {len(list(out.glob('*.png')))} charts written to {out}")

def _cli() -> int:
    """Entry point for the `ti-figures` console script."""
    import argparse
    ap = argparse.ArgumentParser(description="Render all chart PNGs.")
    ap.add_argument("--data", required=True, help="Dataset directory.")
    ap.add_argument("--out", default="outputs",
                    help="Output dir; charts go to <out>/figures/ (default: ./outputs).")
    args = ap.parse_args()
    render_all(args.data, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
