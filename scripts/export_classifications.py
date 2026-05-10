#!/usr/bin/env python3
"""
export_classifications.py — write a per-sample classification CSV + TXT.

For every transcript folder in the dataset, this script applies the
rule-based call-type classifier and emits two complementary files:

    sample_classifications.csv   (machine-readable, one row per sample)
    sample_classifications.txt   (human-readable, one block per sample)

Both files include:
  - the folder id (the directory name, e.g. 01KQ0CAE7F064EC93F0540CA)
  - the meeting title
  - the resulting call_type (support / external / internal)
  - the classifier's confidence and the rule that fired
  - attendee context (count and customer email domains)
  - the meeting start time (UTC) and duration

Usage:
    python scripts/export_classifications.py --data /path/to/dataset --out outputs/

The output directory is created if it does not exist. Existing files with
the same names are overwritten.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import Counter
from pathlib import Path

# Make the package importable when running from a checkout (no install needed)
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from transcript_intelligence import load_all
from transcript_intelligence.call_type_classifier import classify

INTERNAL_DOMAIN = "aegiscloud.com"


def build_rows(meetings) -> list[dict]:
    """Apply the classifier to every loaded meeting and return per-sample rows.

    Sorted alphabetically by folder_id so the output is deterministic and
    easy to scan / diff between runs.
    """
    rows: list[dict] = []
    for m in meetings:
        folder_id = os.path.basename(str(m.folder))
        call_type, confidence, reason = classify(m.title, m.all_emails)
        domains = sorted({e.split("@")[-1] for e in m.all_emails})
        external_domains = ", ".join(d for d in domains if d != INTERNAL_DOMAIN)
        rows.append({
            "folder_id": folder_id,
            "meeting_id": m.meeting_id,
            "title": m.title,
            "call_type": call_type,
            "confidence": confidence,
            "reason": reason,
            "n_attendees": len(m.all_emails),
            "domains": ", ".join(domains),
            "external_customer_domains": external_domains or "(none — Aegis only)",
            "start_time_utc": m.start_time.isoformat(),
            "duration_min": round(m.duration_min, 1),
        })
    rows.sort(key=lambda r: r["folder_id"])
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to a UTF-8 CSV file (header row included)."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_txt(rows: list[dict], path: Path) -> None:
    """Write a human-readable text report.

    Layout:
      • Header explaining what the file is and how the classifier works
      • Summary count of samples per call_type
      • One labeled block per sample, with all of the same fields as the CSV
    """
    counts = Counter(r["call_type"] for r in rows)

    with path.open("w", encoding="utf-8") as f:
        f.write("=" * 78 + "\n")
        f.write("CALL-TYPE CLASSIFICATION — transcript samples\n")
        f.write("=" * 78 + "\n\n")
        f.write("Each transcript folder is classified into one of three call types:\n\n")
        f.write("    SUPPORT  — a customer reaching out about a specific issue / ticket\n")
        f.write("    EXTERNAL — Aegis account team in conversation with a customer\n")
        f.write("               (renewal, QBR, onboarding, planning, etc.)\n")
        f.write("    INTERNAL — Aegis-only meeting (standup, planning, postmortem, all-hands)\n\n")
        f.write("Classification rules (applied in priority order):\n\n")
        f.write("    1. Title contains 'Support Case' / 'Ticket'  → SUPPORT\n")
        f.write("    2. Title starts with 'Aegis / <Customer>'    → EXTERNAL\n")
        f.write("    3. Any non-aegiscloud.com attendee email     → EXTERNAL\n")
        f.write("    4. Internal-meeting keyword in title          → INTERNAL\n")
        f.write("    5. Otherwise (Aegis-only attendees)           → INTERNAL\n\n")

        f.write(f"Total samples: {len(rows)}\n")
        for ct in ("support", "external", "internal"):
            f.write(f"  {ct.upper():<8} : {counts.get(ct, 0):>3} samples\n")
        f.write("\n" + "=" * 78 + "\n\n")

        for i, r in enumerate(rows, 1):
            f.write(f"[{i:>3}/{len(rows)}]  {r['folder_id']}\n")
            f.write(f"          Title       : {r['title']}\n")
            f.write(f"          Call type   : {r['call_type'].upper()}\n")
            f.write(f"          Confidence  : {r['confidence']}\n")
            f.write(f"          Reason      : {r['reason']}\n")
            f.write(f"          Attendees   : {r['n_attendees']} "
                    f"(customer domains: {r['external_customer_domains']})\n")
            f.write(f"          Started UTC : {r['start_time_utc']}\n")
            f.write(f"          Duration    : {r['duration_min']} min\n\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export per-sample call-type classifications to CSV + TXT.",
    )
    parser.add_argument("--data", required=True,
                        help="Dataset directory containing the transcript subfolders.")
    parser.add_argument("--out", default="outputs",
                        help="Output directory (default: ./outputs). Will be created if missing.")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Loading transcripts from {args.data} …")
    meetings = load_all(args.data)
    print(f"  → {len(meetings)} meetings loaded")

    rows = build_rows(meetings)

    csv_path = out / "sample_classifications.csv"
    txt_path = out / "sample_classifications.txt"
    write_csv(rows, csv_path)
    write_txt(rows, txt_path)

    counts = Counter(r["call_type"] for r in rows)
    print(f"\n✓ Wrote {csv_path} ({len(rows)} rows)")
    print(f"✓ Wrote {txt_path}")
    print("\nSummary:")
    for ct in ("support", "external", "internal"):
        print(f"  {ct.upper():<8} : {counts.get(ct, 0):>3} samples")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
