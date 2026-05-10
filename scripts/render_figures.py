#!/usr/bin/env python3
"""
render_figures.py — render all chart PNGs to <out>/figures/.

Usage:
    python scripts/render_figures.py --data /path/to/dataset --out outputs/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence import render_all_figures


def main() -> int:
    ap = argparse.ArgumentParser(description="Render all chart PNGs.")
    ap.add_argument("--data", required=True,
                    help="Directory containing the 100 transcript subfolders.")
    ap.add_argument("--out", default="outputs",
                    help="Output directory; charts go to <out>/figures/ (default: ./outputs).")
    args = ap.parse_args()
    render_all_figures(args.data, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
