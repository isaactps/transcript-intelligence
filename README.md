# Transcript Intelligence

Turn 100 call transcripts into leadership-ready insights.

[![ci](https://img.shields.io/badge/ci-passing-brightgreen)](#)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Take-home submission.** A pipeline that ingests call transcripts, classifies them by call type
> and theme, surfaces sentiment trends, scores customers for churn risk, tracks commitments,
> traces cross-call narratives, and renders the lot into a leadership-ready slide deck.

---

## TL;DR — three findings from the dataset

1. **The mid-March Detect outage is visible in the data.** All three call types — internal war
   rooms, support tickets, external customer escalations — sentiment-cratered to ~2.0 in the
   week of March 9-15, then recovered together. A single-channel sentiment model would have
   missed this; you only see it by aggregating across call types.
2. **Four customer accounts are at HIGH churn risk today** — Cobalt Software, Northstar Pharma,
   Ridgeline Logistics, Meridian Capital. All four have *every* risk signal firing: dropping
   sentiment, churn-signal moments, competitor (SentinelShield) mentions, reliability/SLA
   exposure.
3. **The Comply v2 launch is the recovery story.** April external sentiment recovered to 4.1,
   above the pre-outage baseline of 4.0. The launch threaded through 51 calls and 25 customers.

The full narrative is in [`docs/Transcript_Intelligence_Findings.pdf`](docs/Transcript_Intelligence_Findings.pdf).

---

## Repository layout

```
transcript-intelligence/
├── .github/workflows/ci.yml       ← lint + tests on push
├── docs/
│   ├── Transcript_Intelligence_Findings.pptx
│   ├── Transcript_Intelligence_Findings.pdf
│   └── figures/                   ← chart PNGs used in the deck
├── outputs/                       ← runtime artifacts (gitignored)
├── scripts/
│   ├── run_pipeline.py            ← end-to-end CSVs + insights.json
│   ├── render_figures.py          ← chart PNGs
│   ├── walkthrough.py             ← prints every analysis step
│   └── build_deck.js              ← regenerate the PowerPoint
├── src/
│   └── transcript_intelligence/   ← importable Python package
│       ├── __init__.py
│       ├── data_loader.py
│       ├── call_type_classifier.py        ← REQUIRED TASK 1a
│       ├── topic_categorizer.py           ← REQUIRED TASK 1b
│       ├── sentiment_analyzer.py          ← REQUIRED TASK 2
│       ├── churn_risk.py                  ← BONUS #1
│       ├── action_item_tracker.py         ← BONUS #2
│       ├── narrative_tracer.py            ← BONUS #3
│       ├── conversation_dynamics.py       ← BONUS #4
│       ├── visualizations.py
│       ├── pipeline.py                    ← orchestrator
│       └── _cli.py                        ← console-script glue
├── tests/                         ← pytest unit tests + smoke test
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
└── README.md
```

---

## Install

```bash
git clone <this-repo>
cd transcript-intelligence

# Either editable install …
python -m pip install -e ".[dev]"

# … or a plain venv with requirements
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

`pip install -e .` registers three console scripts: `ti-pipeline`, `ti-figures`,
`ti-walkthrough`.

---

## Run

The dataset is included inside the repo. Point the scripts at it via `--data`.

### End-to-end pipeline → CSVs + insights.json

```bash
ti-pipeline --data dataset --out outputs/
# or, equivalently
python scripts/run_pipeline.py --data dataset --out outputs/
```

That writes:

| file                                  | what it is                                    |
| ------------------------------------- | --------------------------------------------- |
| `outputs/insights.json`               | top-line summary stats (used by the deck)     |
| `outputs/meetings.csv`                | wide frame: one row per call, fully enriched  |
| `outputs/utterances.csv`              | long frame: one row per spoken utterance      |
| `outputs/churn_risk.csv`              | per-customer 0-12 risk score + reasons        |
| `outputs/action_items.csv`            | parsed action items with owner + deadline     |
| `outputs/conversation_dynamics.csv`   | talk-time + coaching flags                    |
| `outputs/narrative_*.csv`             | cross-call timelines (outage / launch / comp) |
| `outputs/customer_trajectories.csv`   | sentiment per customer over time              |
| `outputs/in_call_swings.csv`          | start-vs-end sentiment swing per call         |
| `outputs/sentiment_*.csv`             | aggregations (by call type, theme, week)      |
| `outputs/weekly_sentiment.csv`        | weekly-trend frame for the headline chart     |

### Render figures → PNGs

```bash
ti-figures --data dataset --out outputs/
# writes outputs/figures/01_*.png … 09_*.png
```

### Console walkthrough → no files, just the story in your terminal

```bash
ti-walkthrough --data dataset
```

This is the closest equivalent to "run the notebook top-to-bottom" — every analysis module
prints a representative DataFrame, in order, with banners.

### Regenerate the csv and text files that provides the classification to each of the data samples in the data set

```bash
python scripts/export_classifications.py --data dataset --out outputs/
```

---

## Test

```bash
pytest                            # fast unit tests (no dataset needed)
TI_DATA=dataset pytest            # adds end-to-end smoke test
ruff check src tests              # lint
```

---

## Approach in one paragraph

The dataset already has rich upstream-LLM annotations: per-meeting `topics`, `actionItems`,
`keyMoments`, `sentimentScore`; per-utterance `sentimentType`. So I trust those labels and
focus my value-add on what they *don't* give you: **classification** (call type),
**a stakeholder-relevant taxonomy** (themes), and **aggregations across calls**
(trends, churn, narratives, coaching). For the call-type classifier I use rules — the signal is
clean and rules are auditable. For themes I use a transparent keyword taxonomy and validate
independently with TF-IDF + KMeans. For the bonus insights I lean into what becomes possible
*only* when you connect calls to each other — narrative tracing across all three call types is
the most novel piece, and the most leadership-shaped output.

## What's where in the code

| Required brief item                       | Module                          |
| ----------------------------------------- | ------------------------------- |
| Pipeline that processes transcripts       | `pipeline.py` + `data_loader.py`|
| Categorize by topic / theme               | `topic_categorizer.py`          |
| Sentiment analysis across call types      | `sentiment_analyzer.py`         |
| Trends over time                          | `sentiment_analyzer.py` (`weekly_sentiment_trend`) |
| **Bonus** — churn risk early warning      | `churn_risk.py`                 |
| **Bonus** — commitment tracker            | `action_item_tracker.py`        |
| **Bonus** — cross-call narrative tracing  | `narrative_tracer.py`           |
| **Bonus** — call coaching dynamics        | `conversation_dynamics.py`      |

## Caveats

- 100 transcripts is small. Specific account-level claims are *evidence* not *proof*.
- I trust upstream sentiment + topic labels. If they're systemically biased, my aggregates inherit the bias.
- Speaker→domain mapping is best-effort. Tested OK on this dataset (~57/43 split on customer calls).
- Churn-risk weights are equal across the four signals (heuristic). With churn outcomes as labels, train weights instead.
- Privacy: any production version needs proper access controls, redaction, and audit logs from day one.

## License

[MIT](LICENSE).
