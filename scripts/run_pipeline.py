#!/usr/bin/env python3
"""
run_pipeline.py — CLI entry point for the full Transcript Intelligence pipeline.

Usage:
    python scripts/run_pipeline.py --data /path/to/dataset --out outputs/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make sure src/ is importable when running from the repo root without install
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence import run_pipeline


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run the Transcript Intelligence pipeline end-to-end.",
    )
    ap.add_argument("--data", required=True,
                    help="Directory containing the 100 transcript subfolders.")
    ap.add_argument("--out", default="outputs",
                    help="Output directory for CSVs and insights.json (default: ./outputs).")
    args = ap.parse_args()

    insights = run_pipeline(args.data, args.out)
    print("\n=== Top-line insights ===")
    print(json.dumps(insights, indent=2, default=str)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
