# Demo walkthrough script — Transcript Intelligence

> A 7-minute screen-recording script. Each section is timed and shows exactly what to display
> and what to say. Use this as a teleprompter; it's calibrated to fit comfortably inside the
> 5-10 minute window in the brief.

**Setup before recording:** terminal in `transcript-intelligence/`, slide deck open in
PowerPoint/Keynote, the `src/transcript_intelligence/` package open in VS Code, and the
`outputs/figures/` folder ready to browse.

---

## 0:00 – 0:30 · Intro (30 sec)

**Show:** title slide of the deck.

> "Hi — I'm walking you through Transcript Intelligence, my take-home submission. The brief
> asked for three things: classify and theme 100 transcripts, do sentiment analysis across
> call types, and add insights of my own. I'll show you the pipeline running, then walk through
> the four most interesting findings. Let's start with the data."

---

## 0:30 – 1:30 · Pipeline running (1 min)

**Show:** terminal, run `python scripts/run_pipeline.py --data dataset --out outputs/`.
Watch it tick through 8 stages.

> "One command, end-to-end. It loads the 100 transcript folders into per-meeting and
> per-utterance frames, classifies call types, categorizes themes, aggregates sentiment, runs
> all four bonus insights, and writes everything to CSVs.
>
> Total run time is under five seconds because the heavy lifting — sentiment labels and topics —
> was already done by the upstream pipeline that produced this dataset. My value-add is what
> happens *across* the 100 transcripts, not what happens *inside* one of them."

**Show:** `ls outputs/` — point out `meetings.csv`, `churn_risk.csv`, `narrative_*.csv`,
`insights.json`, the figures folder.

---

## 1:30 – 2:30 · Required task 1: call type + themes (1 min)

**Show:** terminal — run `python scripts/walkthrough.py --data dataset`. Scroll to the
"Call type classification" banner showing the value counts. Then the "Theme categorization"
banner.

> "First required task. Classify by call type — I went rule-based because the signal is clean.
> Title says 'Support Case' → support. Title starts 'Aegis / Customer-name' → external. Any
> non-Aegis email domain → external. Otherwise → internal. 43 external, 30 internal, 27
> support. Zero ambiguity, fully auditable.
>
> For themes I built an 8-bucket taxonomy mapped to who-cares-about-what. Reliability for SRE,
> Renewal & Churn for CS leaders, Compliance for product, and so on. Then — and this is the
> important part — I independently validated it with TF-IDF clustering."

**Show:** `cluster_sanity_check` output.

> "The clusters surface the same buckets *plus* distinct product lines — Aegis Identity, Aegis
> Protect, Comply v2, Aegis Detect each show up as a distinct conversational world. That's a
> future enhancement: add product-line as an orthogonal facet."

---

## 2:30 – 3:30 · Required task 2: sentiment + the outage signal (1 min)

**Show:** slide 8 — the weekly sentiment chart with the orange outage band.

> "Second required task. I trust the per-utterance sentiment labels and aggregate them. The
> obvious finding is support is most negative — 2.94 average — because by definition customers
> are calling about a problem. The more interesting finding is the variance: external calls have
> the *widest* spread, so a single very-negative external call is worth more attention than ten
> very-negative support tickets.
>
> But the headline is this chart. Mid-March, all three call types simultaneously crater to
> around 2.0. That's the Detect outage. You only see this signal because we're aggregating
> across call types — a single sentiment model on a single channel would never catch a
> system-wide event like this."

---

## 3:30 – 4:30 · Bonus #1: churn risk (1 min)

**Show:** slide 10. Then jump to `outputs/churn_risk.csv` in a viewer.

> "Bonus insight one — per-account churn risk. For every customer, I sum four explainable
> signals: sentiment trajectory, churn-signal key moments, competitor mentions, and reliability
> exposure. Each is zero to three points. Total zero to twelve, bucketed High / Medium / Low.
>
> Cobalt Software scores 10 out of 12. Northstar Pharma 9. Both have all four signals firing
> including SentinelShield engagement. The reasons column tells a CS lead exactly why each
> customer is flagged — sentiment dipped from 4.2 to 1.6, three churn-signal moments, two
> competitor mentions, three reliability hits. That's directly actionable, not a black-box score."

---

## 4:30 – 5:15 · Bonus #2: action items (45 sec)

**Show:** slide 11 + `outputs/action_items.csv`.

> "Bonus two. The dataset already has clean action items in summary.json. I parsed 397 of them,
> attributed 99% to a named owner, extracted explicit deadlines from 14%, and aggregated by
> both owner and customer.
>
> Two products fall straight out of this. Maria Santos owns 31 items, 30 of them
> customer-facing — that's a workload-concentration finding worth a manager's attention.
> And every customer-facing commitment we ever made is now indexable by customer — the
> account-manager-prepping-for-renewal use case is solved by data we already had."

---

## 5:15 – 6:30 · Bonus #3: narrative tracing (1 min 15 sec)

**Show:** slide 12 — the outage narrative chart. Then `outputs/narrative_detect_outage.csv` open.

> "Bonus three is the most novel piece. From a single seed phrase — 'Detect outage' — I trace
> every call across internal, external, and support that touched the event. Sorted
> chronologically, you see the V-shape recovery and the long tail.
>
> March tenth: internal war room, sentiment 1.8. March eleventh: support tickets at 1.4 — that's
> Trailhead Marketplace, customers feel it. March eighteenth: customer escalation with
> Northstar Pharma. April fourth: Comply v2 launches and sentiment recovers. But look at this —
> April twenty-fourth, the win/loss analysis call still cites the outage. The story doesn't
> end when the incident closes.
>
> Same template works for the Comply v2 launch — 51 calls, 25 customers — and the SentinelShield
> competitive threat — 22 calls, 8 accounts. This is the kind of insight that's expensive for a
> human to assemble manually and trivial to ship as a product feature."

---

## 6:30 – 7:00 · Bonus #4 + recommendations (30 sec)

**Show:** slide 13 (talktime) briefly, then slide 15 (recommendations).

> "Bonus four is conversation dynamics for call coaching. I'll skip the details — the team is
> healthy, Aegis-side averages 57% talk-time on external calls.
>
> Three Monday-morning recommendations. One: ship the churn-risk dashboard this sprint, the
> high-risk accounts won't wait. Two: surface customer-commitments by account in the CRM —
> single highest-leverage win. Three: use narrative tracing for post-incident customer comms.
> All three rest on logic that's already in the package."

---

## 7:00 · Close

**Show:** thank-you slide.

> "Source code, pipeline, raw outputs, and the deck are all in the repo. Happy to walk through
> any specific module in Q&A. Thanks."

---

## If asked in Q&A

**"Why didn't you re-run sentiment with your own model?"**
The upstream model has full conversational context and access to better data than I do. My
value is aggregation. If a sanity-check on a held-out sample showed bias I'd revisit.

**"How would the churn-risk score change with more data?"**
Today the four signals are equally weighted — that's a heuristic. Given churn outcomes as
labels, I'd train the weights with logistic regression or gradient boosting and add tenure +
account tier as features. The four signals stay; their weights stop being asserted.

**"What if the dataset is synthetic?"**
It looks generated to me — coherent story arcs, ~32 customers, clean labels. Findings are still
defensible because the *techniques* generalize: classify call type, aggregate sentiment, score
churn risk, trace narratives. On a real dataset the numbers shift but the pipeline doesn't.

**"What would break first at scale?"**
The keyword-based theme taxonomy. At ~10k+ transcripts/quarter you'd want LLM-driven theme
discovery on a quarterly cadence to catch emerging topics (AI-governance, data-residency)
before they become trends. The classifier and the bonus insights all scale fine.

**"Show me the code for [X]"**
Open `src/transcript_intelligence/[module].py`. Each module is single-purpose with a clear
public API. `scripts/walkthrough.py` shows every module being called in order.
