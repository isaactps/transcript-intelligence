"""
transcript_intelligence
=======================

A pipeline that turns call transcripts into leadership-ready insights.

Public API:

    >>> from transcript_intelligence import load_all, run_pipeline
    >>> meetings = load_all("/path/to/dataset")
    >>> insights = run_pipeline("/path/to/dataset", "./outputs")

Modules:

    data_loader            - ingest transcript folders into pandas frames
    call_type_classifier   - classify support / external / internal
    topic_categorizer      - 8-theme taxonomy + TF-IDF/KMeans validation
    sentiment_analyzer     - aggregations, weekly trend, in-call swings
    churn_risk             - bonus #1: per-account 0-12 risk score
    action_item_tracker    - bonus #2: parsed commitments + workload
    narrative_tracer       - bonus #3: cross-call story tracing
    conversation_dynamics  - bonus #4: talk-time + coaching flags
    visualizations         - render PNG charts
    pipeline               - orchestrator (entry point: ti-pipeline)
"""

from .data_loader import (
    Meeting,
    load_all,
    load_meeting,
    meetings_to_frame,
    utterances_to_frame,
)
from .call_type_classifier import classify, add_call_type_to_frame
from .topic_categorizer import (
    THEMES,
    categorize_all,
    categorize_one,
    cluster_sanity_check,
)
from .sentiment_analyzer import (
    customer_trajectory,
    in_call_sentiment_swing,
    per_utterance_score_frame,
    sentiment_by_call_type,
    sentiment_by_theme,
    sentiment_distribution_matrix,
    weekly_sentiment_trend,
)
from .churn_risk import per_customer_churn_score
from .action_item_tracker import (
    actions_per_customer,
    actions_per_owner,
    build_action_frame,
    parse_action,
)
from .narrative_tracer import narrative_summary_stats, trace_narrative
from .conversation_dynamics import coaching_flags, per_meeting_dynamics
from .pipeline import run as run_pipeline
from .visualizations import render_all as render_all_figures

__version__ = "0.1.0"
__all__ = [
    # data
    "Meeting",
    "load_all",
    "load_meeting",
    "meetings_to_frame",
    "utterances_to_frame",
    # classifiers
    "classify",
    "add_call_type_to_frame",
    "THEMES",
    "categorize_all",
    "categorize_one",
    "cluster_sanity_check",
    # sentiment
    "customer_trajectory",
    "in_call_sentiment_swing",
    "per_utterance_score_frame",
    "sentiment_by_call_type",
    "sentiment_by_theme",
    "sentiment_distribution_matrix",
    "weekly_sentiment_trend",
    # bonus insights
    "per_customer_churn_score",
    "actions_per_customer",
    "actions_per_owner",
    "build_action_frame",
    "parse_action",
    "narrative_summary_stats",
    "trace_narrative",
    "coaching_flags",
    "per_meeting_dynamics",
    # orchestration
    "run_pipeline",
    "render_all_figures",
]
