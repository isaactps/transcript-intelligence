"""
data_loader.py
--------------
Loads all transcript folders into a single, queryable structure.

Each transcript folder contains 6 JSON files. We flatten the most useful
information into a per-meeting record and a per-utterance long-format frame.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

INTERNAL_DOMAIN = "aegiscloud.com"


@dataclass
class Meeting:
    """One transcript / meeting, fully loaded."""

    meeting_id: str
    title: str
    organizer_email: str
    start_time: datetime
    end_time: datetime
    duration_min: float
    all_emails: list[str]
    speakers: list[str]
    summary: str
    action_items: list[str]
    topics: list[str]
    overall_sentiment: str          # categorical label (e.g. "mixed-negative")
    sentiment_score: float          # 1..5 scale
    key_moments: list[dict]
    transcript: list[dict]          # list of utterance dicts
    folder: Path = field(repr=False)

    # ---------- Derived helpers ----------
    @property
    def external_domains(self) -> list[str]:
        return sorted({e.split("@")[-1] for e in self.all_emails
                       if e.split("@")[-1] != INTERNAL_DOMAIN})

    @property
    def has_external_attendees(self) -> bool:
        return len(self.external_domains) > 0

    @property
    def full_text(self) -> str:
        return " ".join(u.get("sentence", "") for u in self.transcript)


def load_meeting(folder: Path) -> Meeting:
    """Load one transcript folder into a Meeting object."""

    def _load(name: str) -> Any:
        with open(folder / name, "r", encoding="utf-8") as f:
            return json.load(f)

    info = _load("meeting-info.json")
    summ = _load("summary.json")
    transcript = _load("transcript.json").get("data", [])
    speakers_meta = _load("speaker-meta.json")

    return Meeting(
        meeting_id=info["meetingId"],
        title=info["title"],
        organizer_email=info.get("organizerEmail", ""),
        start_time=datetime.fromisoformat(info["startTime"].replace("Z", "+00:00")),
        end_time=datetime.fromisoformat(info["endTime"].replace("Z", "+00:00")),
        duration_min=float(info.get("duration", 0.0)),
        all_emails=info.get("allEmails", []),
        speakers=list(speakers_meta.values()),
        summary=summ.get("summary", ""),
        action_items=summ.get("actionItems", []),
        topics=summ.get("topics", []),
        overall_sentiment=summ.get("overallSentiment", "unknown"),
        sentiment_score=float(summ.get("sentimentScore", 3.0)),
        key_moments=summ.get("keyMoments", []),
        transcript=transcript,
        folder=folder,
    )


def load_all(dataset_dir: str | Path) -> list[Meeting]:
    """Load every transcript subfolder under `dataset_dir`."""
    dataset_dir = Path(dataset_dir)
    folders = [p for p in sorted(dataset_dir.iterdir()) if p.is_dir()]
    return [load_meeting(p) for p in folders]


# ---------- Frame builders for analysis ----------

def meetings_to_frame(meetings: list[Meeting]) -> pd.DataFrame:
    """Wide frame: one row per meeting."""
    rows = []
    for m in meetings:
        rows.append({
            "meeting_id": m.meeting_id,
            "title": m.title,
            "organizer_email": m.organizer_email,
            "start_time": m.start_time,
            "duration_min": m.duration_min,
            "n_attendees": len(m.all_emails),
            "n_speakers": len(m.speakers),
            "external_domains": ", ".join(m.external_domains),
            "has_external": m.has_external_attendees,
            "summary": m.summary,
            "action_items": m.action_items,
            "topics": m.topics,
            "overall_sentiment": m.overall_sentiment,
            "sentiment_score": m.sentiment_score,
            "n_utterances": len(m.transcript),
            "n_key_moments": len(m.key_moments),
            "key_moment_types": [k.get("type", "?") for k in m.key_moments],
            "folder": str(m.folder),
        })
    return pd.DataFrame(rows)


def utterances_to_frame(meetings: list[Meeting]) -> pd.DataFrame:
    """Long frame: one row per spoken utterance across all meetings."""
    rows = []
    for m in meetings:
        for u in m.transcript:
            rows.append({
                "meeting_id": m.meeting_id,
                "title": m.title,
                "speaker": u.get("speaker_name"),
                "sentence": u.get("sentence", ""),
                "sentiment": u.get("sentimentType", "neutral"),
                "time": u.get("time", 0.0),
                "endTime": u.get("endTime", 0.0),
                "duration_sec": (u.get("endTime", 0.0) or 0.0) - (u.get("time", 0.0) or 0.0),
                "confidence": u.get("averageConfidence"),
            })
    return pd.DataFrame(rows)
