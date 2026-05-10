"""
End-to-end smoke test.

Skipped unless the TI_DATA env var points to a real dataset directory. Used in
CI to guarantee that pipeline.run() doesn't blow up on the full sample data.

Run:
    TI_DATA=/path/to/dataset python -m pytest tests/test_pipeline_smoke.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence import run_pipeline

DATA = os.environ.get("TI_DATA")


@pytest.mark.skipif(not DATA, reason="TI_DATA env var not set; skipping smoke test")
def test_pipeline_runs_end_to_end() -> None:
    with tempfile.TemporaryDirectory() as out:
        insights = run_pipeline(DATA, out)

    # Top-line invariants we expect from the 100-meeting sample
    assert insights["n_meetings"] == 100
    assert insights["n_utterances"] > 4_000
    assert insights["n_action_items"] > 300
    # All three call types should be represented
    assert set(insights["call_type_counts"]) == {"support", "external", "internal"}
    # At least one customer in the High risk bucket given the dataset
    high_risk = [c for c in insights["high_risk_accounts"] if c["risk_bucket"] == "High"]
    assert len(high_risk) >= 1
    # All three narrative summaries populated
    for k in ("narrative_outage", "narrative_launch", "narrative_compete"):
        assert insights[k]["n_calls"] >= 1
