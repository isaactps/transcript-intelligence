/**
 * build_deck.js
 * -------------
 * Build the Transcript Intelligence slide deck.
 *
 * Structure:
 *   1. Title
 *   2. The Ask & The Dataset
 *   3. TL;DR (3 headline insights)
 *   4. Approach overview
 *   5. Call type classification (required task #1, part 1)
 *   6. Topic / theme categorization (required task #1, part 2)
 *   7. Sentiment by call type (required task #2)
 *   8. Sentiment over time → the outage signal
 *   9. Sentiment by theme
 *   10. Bonus 1: Churn risk early warning
 *   11. Bonus 2: Action item / commitment tracker
 *   12. Bonus 3: Cross-call narrative tracing (the outage story)
 *   13. Bonus 4: Conversation dynamics / coaching
 *   14. Stakeholder mapping
 *   15. Recommendations
 *   16. What I'd build next
 *   17. Appendix: data caveats & assumptions
 */

const pptxgen = require("pptxgenjs");
const path = require("path");

// ---------- Visual style ----------
const NAVY     = "1E2761";
const NAVY_DK  = "151A4D";
const CORAL    = "E6754F";
const TEAL     = "3CA39A";
const SLATE    = "4B5563";
const LIGHT    = "F4F5F7";
const WHITE    = "FFFFFF";
const MUTED    = "9CA3AF";
const TEXT_BODY= "1F2937";

const FONT_HEAD = "Calibri";
const FONT_BODY = "Calibri";

const FIG = path.resolve(__dirname, "../docs/figures");
const fig = (n) => path.join(FIG, n);

// ---------- Helpers ----------
function pres() {
  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
  p.author = "Transcript Intelligence";
  p.title = "Transcript Intelligence — findings & recommendations";
  return p;
}

function slideHeader(slide, eyebrow, title, opts = {}) {
  // small eyebrow tag
  if (eyebrow) {
    slide.addText(eyebrow.toUpperCase(), {
      x: 0.6, y: 0.45, w: 12, h: 0.3,
      fontFace: FONT_HEAD, fontSize: 11, bold: true,
      color: CORAL, charSpacing: 4, margin: 0,
    });
  }
  slide.addText(title, {
    x: 0.6, y: 0.75, w: 12, h: 0.7,
    fontFace: FONT_HEAD, fontSize: 28, bold: true,
    color: NAVY, margin: 0, valign: "top",
  });
}

function footer(slide, n) {
  slide.addText("Transcript Intelligence  •  Take-home findings", {
    x: 0.6, y: 7.05, w: 8, h: 0.3,
    fontFace: FONT_BODY, fontSize: 9, color: MUTED, margin: 0,
  });
  slide.addText(String(n), {
    x: 12.4, y: 7.05, w: 0.4, h: 0.3,
    fontFace: FONT_BODY, fontSize: 9, color: MUTED, align: "right", margin: 0,
  });
}

function statCard(slide, x, y, w, h, value, label, color = NAVY, valueSize = 32) {
  slide.addShape("rect", {
    x, y, w, h, fill: { color: WHITE }, line: { color: "E5E7EB", width: 1 },
  });
  // colored accent stripe on left
  slide.addShape("rect", {
    x, y, w: 0.08, h, fill: { color }, line: { color, width: 0 },
  });
  slide.addText(value, {
    x: x + 0.2, y: y + 0.15, w: w - 0.3, h: h * 0.55,
    fontFace: FONT_HEAD, fontSize: valueSize, bold: true, color, margin: 0, valign: "middle",
  });
  slide.addText(label, {
    x: x + 0.2, y: y + h * 0.55, w: w - 0.3, h: h * 0.4,
    fontFace: FONT_BODY, fontSize: 11, color: SLATE, margin: 0, valign: "top",
  });
}

function bullets(slide, x, y, w, h, items, opts = {}) {
  const arr = items.map((t, i) => ({
    text: t,
    options: { bullet: { code: "25A0" }, breakLine: i < items.length - 1,
               paraSpaceAfter: opts.spaceAfter || 6 },
  }));
  slide.addText(arr, {
    x, y, w, h, fontFace: FONT_BODY, fontSize: opts.fontSize || 13,
    color: opts.color || TEXT_BODY, valign: "top",
  });
}

// ---------- The deck ----------
async function build() {
  const p = pres();

  // ---------- SLIDE 1: TITLE ----------
  {
    const s = p.addSlide();
    s.background = { color: NAVY_DK };
    s.addText("TRANSCRIPT INTELLIGENCE", {
      x: 0.8, y: 1.6, w: 11, h: 0.5,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: CORAL,
      charSpacing: 8, margin: 0,
    });
    s.addText("What 100 conversations told us\nabout our customers, our product, and our team.", {
      x: 0.8, y: 2.15, w: 11, h: 2.2,
      fontFace: FONT_HEAD, fontSize: 44, bold: true, color: WHITE,
      margin: 0, valign: "top",
    });
    // Accent line motif
    s.addShape("rect", {
      x: 0.8, y: 4.55, w: 0.7, h: 0.06,
      fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText("Findings & recommendations  •  Product & engineering leadership review", {
      x: 0.8, y: 4.75, w: 11, h: 0.4,
      fontFace: FONT_BODY, fontSize: 14, color: "CADCFC", margin: 0,
    });
    s.addText("Senior Software Engineer take-home  •  May 2026", {
      x: 0.8, y: 6.7, w: 11, h: 0.3,
      fontFace: FONT_BODY, fontSize: 11, color: MUTED, italic: true, margin: 0,
    });
  }

  // ---------- SLIDE 2: THE ASK + DATASET ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Context", "We have 100 conversations. Three audiences. One question.");

    // Left side: text
    s.addText("The brief", {
      x: 0.6, y: 1.7, w: 5.6, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 0.6, 2.1, 5.6, 2.2, [
      "Process the transcripts and categorize by theme",
      "Generate sentiment trends across call types",
      "Show what other insights this data unlocks",
    ], { fontSize: 13 });

    s.addText("My read of the brief", {
      x: 0.6, y: 4.4, w: 5.6, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, margin: 0,
    });
    s.addText(
      "The required tasks are table stakes. The differentiator is showing how transcripts " +
      "become a leadership tool — surfacing things scattered across hundreds of calls that " +
      "no human can read in time.",
      { x: 0.6, y: 4.8, w: 5.6, h: 1.6,
        fontFace: FONT_BODY, fontSize: 13, color: TEXT_BODY, italic: true, margin: 0 });

    // Right side: stat cards
    statCard(s, 7.0, 1.7, 2.85, 1.2, "100", "transcripts", NAVY);
    statCard(s, 9.95, 1.7, 2.85, 1.2, "4,313", "utterances", TEAL);
    statCard(s, 7.0, 3.0, 2.85, 1.2, "32", "customer accounts", CORAL);
    statCard(s, 9.95, 3.0, 2.85, 1.2, "397", "action items", NAVY);
    statCard(s, 7.0, 4.3, 2.85, 1.2, "Feb–Apr", "data window (2026)", TEAL, 26);
    statCard(s, 9.95, 4.3, 2.85, 1.2, "30 min", "avg call duration", CORAL, 26);

    s.addText("Each transcript ships with: full sentence-level transcript, per-utterance sentiment, " +
      "speaker timing, meeting metadata, and an upstream-LLM summary with topics, action items, key moments.",
      { x: 7.0, y: 5.65, w: 5.8, h: 0.9,
        fontFace: FONT_BODY, fontSize: 10, color: SLATE, italic: true, margin: 0 });

    footer(s, 2);
  }

  // ---------- SLIDE 3: TL;DR ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Headlines", "Three things leadership should walk out knowing.");

    // Three big cards across the slide
    const cards = [
      { i: 1, t: "An outage you can SEE in the data",
            d: "The mid-March Detect outage shows up as a sentiment crater across all three call types — " +
               "internal sentiment 1.8, support 1.4, external 2.1 in that week. The signature is unmistakable.",
            m: "Fig. 5 (weekly sentiment) + 34-call narrative",
            color: CORAL },
      { i: 2, t: "Four accounts at HIGH churn risk — today",
            d: "Cobalt Software, Northstar Pharma, Ridgeline Logistics, Meridian Capital have all four risk " +
               "signals firing: dropping sentiment, churn-signal moments, competitor mentions, reliability hits.",
            m: "Bonus insight: per-account risk score 0–12",
            color: NAVY },
      { i: 3, t: "The recovery is real and on the data",
            d: "Comply v2 launched April 4 — sentiment on launch-related calls jumps to 4.7. " +
               "April external-call sentiment recovered to 4.1, above the pre-outage baseline of 4.0.",
            m: "Comply v2 narrative: 51 calls, avg sentiment 3.81",
            color: TEAL },
    ];

    cards.forEach((c, idx) => {
      const x = 0.6 + idx * 4.18;
      // Card
      s.addShape("rect", {
        x, y: 1.7, w: 3.95, h: 4.9,
        fill: { color: WHITE }, line: { color: "E5E7EB", width: 1 },
      });
      s.addShape("rect", {
        x, y: 1.7, w: 3.95, h: 0.08,
        fill: { color: c.color }, line: { color: c.color, width: 0 },
      });
      // Big number
      s.addText(`#${c.i}`, {
        x: x + 0.25, y: 1.95, w: 1.5, h: 0.9,
        fontFace: FONT_HEAD, fontSize: 56, bold: true, color: c.color, margin: 0, valign: "top",
      });
      // Title
      s.addText(c.t, {
        x: x + 0.25, y: 2.85, w: 3.5, h: 1.0,
        fontFace: FONT_HEAD, fontSize: 17, bold: true, color: NAVY, margin: 0, valign: "top",
      });
      // Description
      s.addText(c.d, {
        x: x + 0.25, y: 3.95, w: 3.5, h: 1.7,
        fontFace: FONT_BODY, fontSize: 12, color: TEXT_BODY, margin: 0, valign: "top",
      });
      // Metric tag
      s.addShape("rect", {
        x: x + 0.25, y: 5.95, w: 3.5, h: 0.45,
        fill: { color: LIGHT }, line: { color: "E5E7EB", width: 0 },
      });
      s.addText(c.m, {
        x: x + 0.35, y: 5.97, w: 3.3, h: 0.4,
        fontFace: FONT_BODY, fontSize: 10, color: SLATE, italic: true, margin: 0, valign: "middle",
      });
    });

    footer(s, 3);
  }

  // ---------- SLIDE 4: APPROACH ----------
  {
    const s = p.addSlide();
    slideHeader(s, "How I built it", "A pipeline you can audit, not a black box.");

    const stages = [
      { n: 1, h: "Ingest", b: "Flatten 6-file folders into per-meeting + per-utterance frames. 100 meetings × 4,313 utterances." },
      { n: 2, h: "Classify call type", b: "Hybrid rules on title patterns + email domains. 100% deterministic, auditable." },
      { n: 3, h: "Categorize themes", b: "Fixed 8-theme taxonomy with keyword map; cross-validated with TF-IDF + KMeans." },
      { n: 4, h: "Aggregate sentiment", b: "Trust upstream per-utterance labels and meeting scores. Add: trends over time, in-call swings." },
      { n: 5, h: "Bonus insights", b: "Churn risk score, action-item tracker, narrative tracing, conversation dynamics." },
    ];

    stages.forEach((st, idx) => {
      const y = 1.85 + idx * 0.95;
      // Numbered circle
      s.addShape("ellipse", {
        x: 0.6, y, w: 0.7, h: 0.7,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
      s.addText(String(st.n), {
        x: 0.6, y, w: 0.7, h: 0.7,
        fontFace: FONT_HEAD, fontSize: 20, bold: true, color: WHITE,
        align: "center", valign: "middle", margin: 0,
      });
      // Heading + body
      s.addText(st.h, {
        x: 1.55, y: y + 0.02, w: 11, h: 0.4,
        fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, margin: 0,
      });
      s.addText(st.b, {
        x: 1.55, y: y + 0.42, w: 11, h: 0.5,
        fontFace: FONT_BODY, fontSize: 12, color: TEXT_BODY, margin: 0,
      });
    });

    s.addText("Why hybrid? Rules are auditable for the things that have a clean signal (call type). " +
      "ML and LLMs earn their keep on the messy stuff (themes, narratives). Both views must agree.",
      { x: 0.6, y: 6.55, w: 12.2, h: 0.5,
        fontFace: FONT_BODY, fontSize: 12, color: SLATE, italic: true, margin: 0 });

    footer(s, 4);
  }

  // ---------- SLIDE 5: Code → function mapping ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Code map", "Each source file does one job — here's the map.");

    // Three groups stacked vertically. Each row: filename | one-line purpose | tag pill.
    const rows = [
      { group: "Required tasks",
        items: [
          { file: "data_loader.py",          purpose: "Ingest 100 transcript folders → per-meeting + per-utterance frames",
            tag: "Foundation", color: SLATE },
          { file: "call_type_classifier.py", purpose: "Classify each call as support / external / internal (rule-based hybrid)",
            tag: "Required 1a", color: NAVY },
          { file: "topic_categorizer.py",    purpose: "Map each call to one of 8 stakeholder themes; cross-validate with TF-IDF + KMeans",
            tag: "Required 1b", color: NAVY },
          { file: "sentiment_analyzer.py",   purpose: "Aggregate sentiment by call type, theme, week, customer; detect in-call swings",
            tag: "Required 2",  color: NAVY },
        ]
      },
      { group: "Bonus insights",
        items: [
          { file: "churn_risk.py",           purpose: "Score each customer 0-12 across four churn signals; explain every flag",
            tag: "Bonus #1", color: CORAL },
          { file: "action_item_tracker.py",  purpose: "Parse 397 action items, attribute owner + deadline, aggregate by person and customer",
            tag: "Bonus #2", color: CORAL },
          { file: "narrative_tracer.py",     purpose: "Stitch together cross-call stories from a seed phrase (the Detect outage arc)",
            tag: "Bonus #3", color: CORAL },
          { file: "conversation_dynamics.py",purpose: "Talk-time per speaker, customer-voice share, calibrated coaching flags",
            tag: "Bonus #4", color: CORAL },
        ]
      },
      { group: "Pipeline & output",
        items: [
          { file: "pipeline.py",             purpose: "Orchestrator: runs every module in order, persists CSVs + insights.json",
            tag: "Glue", color: TEAL },
          { file: "visualizations.py",       purpose: "Render the 9 chart PNGs the slide deck uses",
            tag: "Glue", color: TEAL },
          { file: "build_deck.js",           purpose: "Generate this PowerPoint from the chart PNGs and insights.json",
            tag: "Glue", color: TEAL },
        ]
      },
    ];

    let y = 1.55;
    rows.forEach((g) => {
      // Group header bar
      s.addShape("rect", {
        x: 0.6, y, w: 12.2, h: 0.30,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
      s.addText(g.group, {
        x: 0.8, y, w: 11.8, h: 0.30,
        fontFace: FONT_HEAD, fontSize: 12, bold: true, color: WHITE,
        valign: "middle", margin: 0,
      });
      y += 0.30;

      g.items.forEach((it, idx) => {
        const rowH = 0.36;
        const fill = idx % 2 === 0 ? WHITE : LIGHT;
        s.addShape("rect", {
          x: 0.6, y, w: 12.2, h: rowH,
          fill: { color: fill }, line: { color: "E5E7EB", width: 0 },
        });
        s.addText(it.file, {
          x: 0.8, y, w: 2.7, h: rowH,
          fontFace: "Consolas", fontSize: 11, bold: true, color: NAVY,
          valign: "middle", margin: 0,
        });
        s.addText(it.purpose, {
          x: 3.55, y, w: 7.3, h: rowH,
          fontFace: FONT_BODY, fontSize: 11, color: TEXT_BODY,
          valign: "middle", margin: 0,
        });
        s.addShape("rect", {
          x: 10.95, y: y + 0.06, w: 1.7, h: rowH - 0.12,
          fill: { color: it.color }, line: { color: it.color, width: 0 },
          rectRadius: 0.08,
        });
        s.addText(it.tag, {
          x: 10.95, y: y + 0.06, w: 1.7, h: rowH - 0.12,
          fontFace: FONT_HEAD, fontSize: 9, bold: true, color: WHITE,
          align: "center", valign: "middle", margin: 0,
        });
        y += rowH;
      });
      y += 0.10;
    });

    s.addText("Each module has a public function and a single responsibility. " +
      "The pipeline is `run_pipeline(data, out)` — one call regenerates every CSV in the package.",
      { x: 0.6, y: 6.85, w: 12.2, h: 0.25,
        fontFace: FONT_BODY, fontSize: 10.5, color: SLATE, italic: true, margin: 0 });

    footer(s, 5);
  }

  // ---------- SLIDE 5: Call type classification ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Required task 1a", "Call type classification — three audiences cleanly separated.");

    s.addImage({ path: fig("01_call_type_distribution.png"),
                 x: 0.6, y: 1.65, w: 7.2, h: 4.1 });

    // Right column: rules summary
    s.addText("Rules used (in priority order)", {
      x: 8.1, y: 1.65, w: 4.7, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 8.1, 2.1, 4.7, 3.6, [
      "Title says 'Support Case' → support",
      "Title starts 'Aegis / Customer' → external",
      "Any non-aegiscloud.com attendee → external",
      "Internal-meeting keyword in title → internal",
      "Otherwise (Aegis-only attendees) → internal",
    ], { fontSize: 12 });

    // Why rules
    s.addShape("rect", {
      x: 0.6, y: 6.0, w: 12.2, h: 0.85,
      fill: { color: LIGHT }, line: { color: "E5E7EB", width: 1 },
    });
    s.addText("Why rules, not an LLM? The signal is clean — every email has a domain, titles follow conventions. " +
      "Rules cost zero, are deterministic, and a PM can read them and push back. " +
      "If we ever see a meeting where rules fail, that's the moment to fall back to an LLM classifier.",
      { x: 0.8, y: 6.05, w: 11.8, h: 0.75,
        fontFace: FONT_BODY, fontSize: 11, color: SLATE, italic: true, margin: 0, valign: "middle" });

    footer(s, 6);
  }

  // ---------- SLIDE 6: Topic / theme categorization ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Required task 1b", "Themes — built around stakeholders, not topic vocabulary.");

    s.addImage({ path: fig("02_theme_distribution.png"),
                 x: 0.6, y: 1.65, w: 7.2, h: 4.6 });

    s.addText("8 themes, mapped to who cares", {
      x: 8.1, y: 1.65, w: 4.7, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 8.1, 2.1, 4.85, 4.5, [
      "Reliability & Incidents → SRE, eng leadership",
      "Renewal & Churn Risk → CS, sales leadership",
      "Compliance & Audit → product, security",
      "Product Launch & Adoption → PM, growth",
      "Roadmap & Planning → eng leadership, PM",
      "Support & Bug Resolution → support leadership",
      "Pricing & Commercial → sales, finance",
      "Competitive Intelligence → PM, marketing",
    ], { fontSize: 11.5, spaceAfter: 4 });

    s.addText("Validated independently with TF-IDF + KMeans (k=8). Clusters surfaced same buckets " +
      "PLUS distinct product lines (Aegis Identity, Aegis Protect) — a future enhancement.",
      { x: 0.6, y: 6.4, w: 12.2, h: 0.5,
        fontFace: FONT_BODY, fontSize: 11, color: SLATE, italic: true, margin: 0 });

    footer(s, 7);
  }

  // ---------- SLIDE 7: Sentiment by call type ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Required task 2", "Sentiment by call type — the obvious finding has a non-obvious twist.");

    s.addImage({ path: fig("03_sentiment_by_call_type.png"),
                 x: 0.6, y: 1.65, w: 7.6, h: 4.0 });

    s.addText("What it tells us", {
      x: 8.4, y: 1.65, w: 4.4, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 8.4, 2.1, 4.5, 4.2, [
      "Support is most negative (2.94) — by definition customers are calling about a problem.",
      "External calls are most positive (3.71) — these are relationship-management.",
      "But std-dev is highest on EXTERNAL (1.03) — when external goes wrong, it really goes wrong.",
      "Lowest external = 1.6 (Blackridge URGENT). Highest support call still 4.8 (a granular-restore success).",
    ], { fontSize: 11.5, spaceAfter: 6 });

    s.addText("So-what", {
      x: 0.6, y: 5.85, w: 12.2, h: 0.35,
      fontFace: FONT_HEAD, fontSize: 12, bold: true, color: CORAL, margin: 0,
    });
    s.addText("Don't track 'support sentiment' as a metric — it'll always be lowest. Track support sentiment TRENDS " +
      "and outliers. And watch the external-call variance: a single very-negative external call is worth more " +
      "attention than ten very-negative support tickets.",
      { x: 0.6, y: 6.2, w: 12.2, h: 0.85,
        fontFace: FONT_BODY, fontSize: 12, color: TEXT_BODY, margin: 0 });

    footer(s, 8);
  }

  // ---------- SLIDE 8: Weekly trend / the outage signal ----------
  {
    const s = p.addSlide();
    slideHeader(s, "The signal we found", "Sentiment over time — the outage is visible in the data.");

    s.addImage({ path: fig("05_weekly_sentiment.png"),
                 x: 0.6, y: 1.6, w: 12.2, h: 4.4 });

    s.addText("ALL THREE call types crater in the week of March 9-15. Internal hits 1.95 (war room). Support hits 2.6 " +
      "(customers feel it). External hits 2.4 (account managers in damage-control). They recover together by April. " +
      "This is exactly the kind of system-wide signal a single sentiment model on a single channel would miss.",
      { x: 0.6, y: 6.15, w: 12.2, h: 0.85,
        fontFace: FONT_BODY, fontSize: 13, color: TEXT_BODY, margin: 0 });

    footer(s, 9);
  }

  // ---------- SLIDE 9: Sentiment by theme ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Required task 2", "Sentiment by theme — Reliability is the wound, Compliance is the strength.");

    s.addImage({ path: fig("04_sentiment_by_theme.png"),
                 x: 0.6, y: 1.65, w: 7.6, h: 4.6 });

    s.addText("Implications by stakeholder", {
      x: 8.4, y: 1.65, w: 4.4, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 8.4, 2.1, 4.5, 4.5, [
      "ENG LEADERSHIP: every Reliability conversation is below the neutral line (mean 2.53). Reliability investment isn't optional.",
      "PRODUCT: Compliance is your customer's love language right now (mean 4.18). Lead with Comply v2 in renewals.",
      "GTM: Renewal & Churn Risk (3.74) is healthier than expected — the team is recovering accounts well.",
      "MARKETING: Competitive Intelligence calls all skew negative (mean 2.90) — competitors are showing up at painful moments, not strong ones.",
    ], { fontSize: 11, spaceAfter: 6 });

    footer(s, 10);
  }

  // ---------- SLIDE 10: Bonus #1 — Churn risk ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Bonus insight 1 of 4", "Churn risk early-warning — explainable, actionable, ranked.");

    s.addImage({ path: fig("07_churn_risk.png"),
                 x: 0.6, y: 1.65, w: 8.0, h: 4.5 });

    s.addText("How the score works", {
      x: 8.8, y: 1.65, w: 4.0, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 8.8, 2.1, 4.0, 3.9, [
      "Sentiment trajectory (0-3)",
      "Churn-signal key moments (0-3)",
      "Competitor mentions (0-3)",
      "Reliability/SLA exposure (0-3)",
      "Total 0–12; bucketed High / Med / Low",
    ], { fontSize: 11, spaceAfter: 4 });

    s.addText("EVERY flag is auditable: a CS lead can drill into Cobalt and see " +
      "exactly which calls drove the score and why.",
      { x: 8.8, y: 4.95, w: 4.0, h: 1.2,
        fontFace: FONT_BODY, fontSize: 11, italic: true, color: SLATE, margin: 0 });

    s.addShape("rect", {
      x: 0.6, y: 6.25, w: 12.2, h: 0.75,
      fill: { color: "FEF3F0" }, line: { color: CORAL, width: 1 },
    });
    s.addText("Action: assign a named exec sponsor to each High-risk account by Friday. " +
      "Cobalt and Northstar both have competitor (SentinelShield) engagement — the clock is on.",
      { x: 0.8, y: 6.3, w: 12.0, h: 0.65,
        fontFace: FONT_BODY, fontSize: 12, bold: true, color: CORAL, margin: 0, valign: "middle" });

    footer(s, 11);
  }

  // ---------- SLIDE 11: Bonus #2 — Action items ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Bonus insight 2 of 4", "Action-item tracker — 397 commitments, fully attributed.");

    s.addImage({ path: fig("08_actions_per_owner.png"),
                 x: 0.6, y: 1.65, w: 7.6, h: 4.6 });

    s.addText("What we extracted", {
      x: 8.4, y: 1.65, w: 4.4, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 8.4, 2.1, 4.5, 4.4, [
      "397 action items across 100 meetings",
      "394 (99%) parsed to a named owner",
      "56 (14%) carry an explicit deadline phrase",
      "Maria Santos: 31 items, 30 customer-facing — burnout risk",
      "16 customer accounts have ≥12 open commitments",
    ], { fontSize: 11.5, spaceAfter: 6 });

    s.addText("So-what", {
      x: 0.6, y: 5.95, w: 12.2, h: 0.35,
      fontFace: FONT_HEAD, fontSize: 12, bold: true, color: CORAL, margin: 0,
    });
    s.addText("Two products fall out of this: (1) a per-owner workload dashboard, (2) a per-customer commitment ledger " +
      "so account managers can see every promise made to a customer across calls. The data is already here — it just isn't visible.",
      { x: 0.6, y: 6.3, w: 12.2, h: 0.7,
        fontFace: FONT_BODY, fontSize: 12, color: TEXT_BODY, margin: 0 });

    footer(s, 12);
  }

  // ---------- SLIDE 12: Bonus #3 — Narrative tracing ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Bonus insight 3 of 4", "Cross-call narrative tracing — the outage as one story.");

    s.addImage({ path: fig("06_outage_narrative.png"),
                 x: 0.6, y: 1.6, w: 12.2, h: 4.6 });

    bullets(s, 0.6, 6.25, 12.2, 0.85, [
      "From a single seed phrase ('Detect outage') we trace 34 calls across 71 days, spanning all three call types and 14 customers.",
      "This view answers questions a leader actually asks: 'How did we handle the outage?' 'Which customers are still bringing it up?'",
      "Same template works for Comply v2 launch (51 calls, 25 customers) and SentinelShield competitive pressure (8 customer accounts).",
    ], { fontSize: 11, spaceAfter: 2 });

    footer(s, 13);
  }

  // ---------- SLIDE 13: Bonus #4 — Conversation dynamics ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Bonus insight 4 of 4", "Conversation dynamics — call coaching, not surveillance.");

    s.addImage({ path: fig("09_talktime_distribution.png"),
                 x: 0.6, y: 1.65, w: 7.4, h: 4.4 });

    s.addText("What we measure", {
      x: 8.2, y: 1.65, w: 4.6, h: 0.4,
      fontFace: FONT_HEAD, fontSize: 14, bold: true, color: NAVY, margin: 0,
    });
    bullets(s, 8.2, 2.1, 4.7, 4.0, [
      "Aegis vs customer talk-time (mapped via email-domain → speaker name)",
      "Per-speaker turns and longest-speaker dominance",
      "Calibrated coaching flags using THIS dataset's distribution, not arbitrary thresholds",
      "9 of 70 customer calls flagged — actionable not noisy",
    ], { fontSize: 11.5, spaceAfter: 6 });

    s.addText("Healthy baseline. Aegis-side averages 57% talk-time on external calls — close to ideal. " +
      "Calls where customers spoke MORE were renewals and competitive evals — exactly when listening matters most.",
      { x: 0.6, y: 6.25, w: 12.2, h: 0.75,
        fontFace: FONT_BODY, fontSize: 12, color: TEXT_BODY, italic: true, margin: 0 });

    footer(s, 14);
  }

  // ---------- SLIDE 14: Stakeholder map ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Putting it together", "Different leaders need different views of the same data.");

    const rows = [
      { who: "Support leader", q: "Which customers keep coming back?",
        u: "Recurring-issue heatmap, support sentiment trend, time-to-resolution by theme" },
      { who: "Sales / CS leader", q: "Which accounts are at risk?",
        u: "Churn risk dashboard (bonus #1), competitor watch, customer-commitment ledger (bonus #2)" },
      { who: "Product manager", q: "What are customers asking for?",
        u: "Feature-request mining from key moments, theme-vs-sentiment matrix, adoption call tracking" },
      { who: "Engineering lead", q: "Where are we hurt and healing?",
        u: "Reliability narrative tracing (bonus #3), incident-to-recovery sentiment arc, RCA action-item follow-through" },
      { who: "Exec / GM", q: "What's the company's story this quarter?",
        u: "Cross-call narratives (bonus #3), aggregate sentiment, win/loss themes pulled from transcripts" },
    ];

    // Header row
    s.addShape("rect", { x: 0.6, y: 1.7, w: 12.2, h: 0.5,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    ["Stakeholder", "Their question", "What we'd ship for them"].forEach((h, i) => {
      const xs = [0.7, 3.0, 7.0][i];
      const w = [2.2, 3.85, 5.6][i];
      s.addText(h, { x: xs, y: 1.7, w, h: 0.5,
        fontFace: FONT_HEAD, fontSize: 13, bold: true, color: WHITE,
        valign: "middle", margin: 0 });
    });

    rows.forEach((r, idx) => {
      const y = 2.2 + idx * 0.8;
      const fill = idx % 2 === 0 ? WHITE : LIGHT;
      s.addShape("rect", { x: 0.6, y, w: 12.2, h: 0.8,
        fill: { color: fill }, line: { color: "E5E7EB", width: 0 } });
      s.addText(r.who, { x: 0.7, y, w: 2.2, h: 0.8,
        fontFace: FONT_HEAD, fontSize: 12.5, bold: true, color: NAVY, valign: "middle", margin: 0 });
      s.addText(r.q, { x: 3.0, y, w: 3.85, h: 0.8,
        fontFace: FONT_BODY, fontSize: 12, color: TEXT_BODY, italic: true, valign: "middle", margin: 0 });
      s.addText(r.u, { x: 7.0, y, w: 5.6, h: 0.8,
        fontFace: FONT_BODY, fontSize: 11.5, color: TEXT_BODY, valign: "middle", margin: 0 });
    });

    footer(s, 15);
  }

  // ---------- SLIDE 15: Recommendations ----------
  {
    const s = p.addSlide();
    slideHeader(s, "What I'd do Monday", "Three concrete moves the data justifies.");

    const recs = [
      { n: 1, color: CORAL,
        h: "Stand up a churn-risk dashboard this sprint",
        b: "The four high-risk accounts won't wait for a perfect product. Ship the per-account risk score with " +
           "drill-down to the source calls. CS leaders can act on it day one.",
        cost: "1 sprint (the model is in this notebook)" },
      { n: 2, color: NAVY,
        h: "Make the action-item ledger a renewal asset",
        b: "Account managers walk into renewals not knowing every promise we ever made. Surface those by customer in " +
           "their CRM. Single highest-leverage win in this dataset.",
        cost: "1-2 sprints + Salesforce integration" },
      { n: 3, color: TEAL,
        h: "Use narrative tracing for post-incident comms",
        b: "Today PMs hand-write incident retros. Auto-generate the timeline with sentiment arc and customer impact " +
           "list. Share with customers as part of the trust-rebuilding loop.",
        cost: "Spike — most logic exists; needs UI" },
    ];

    recs.forEach((r, idx) => {
      const x = 0.6 + idx * 4.18;
      s.addShape("rect", { x, y: 1.7, w: 3.95, h: 4.7,
        fill: { color: WHITE }, line: { color: "E5E7EB", width: 1 } });
      s.addShape("rect", { x, y: 1.7, w: 3.95, h: 0.55,
        fill: { color: r.color }, line: { color: r.color, width: 0 } });
      s.addText(`#${r.n}`, { x: x + 0.2, y: 1.74, w: 1, h: 0.5,
        fontFace: FONT_HEAD, fontSize: 18, bold: true, color: WHITE, margin: 0, valign: "middle" });
      s.addText(r.h, { x: x + 0.25, y: 2.4, w: 3.5, h: 1.0,
        fontFace: FONT_HEAD, fontSize: 15, bold: true, color: NAVY, margin: 0, valign: "top" });
      s.addText(r.b, { x: x + 0.25, y: 3.55, w: 3.5, h: 2.2,
        fontFace: FONT_BODY, fontSize: 11.5, color: TEXT_BODY, margin: 0, valign: "top" });
      s.addShape("rect", { x: x + 0.25, y: 5.85, w: 3.5, h: 0.4,
        fill: { color: LIGHT }, line: { color: "E5E7EB", width: 0 } });
      s.addText("Effort: " + r.cost, { x: x + 0.35, y: 5.87, w: 3.3, h: 0.4,
        fontFace: FONT_BODY, fontSize: 10, italic: true, color: SLATE, margin: 0, valign: "middle" });
    });

    footer(s, 16);
  }

  // ---------- SLIDE 16: What I'd build next ----------
  {
    const s = p.addSlide();
    slideHeader(s, "If I had another week", "Where the next dollar goes.");

    const next = [
      { h: "Product-line dimension", b: "TF-IDF clustering surfaced Aegis Identity, Aegis Protect, Comply v2, Aegis Detect as distinct conversational worlds. Add product-line as a first-class facet." },
      { h: "True LLM-driven theme discovery", b: "Today themes are a fixed taxonomy. With 1k+ transcripts I'd run an LLM-driven theme discovery pass quarterly to catch emerging topics (data-residency, AI-governance) before they become trends." },
      { h: "Real-time alerting", b: "Hook the churn-risk + narrative-tracing into a Slack alert: 'A new call just landed in the SentinelShield narrative — sentiment 2.1 — recommend exec touch.'" },
      { h: "Speaker fingerprinting", b: "Connect speakers across calls (today only inferable via email matching). Enables 'rep coaching' that compares the same rep across multiple meetings." },
      { h: "Trend significance testing", b: "The weekly drop is visible by eye but I haven't proven it's significant. Bootstrap confidence bands on sentiment-by-week, and flag breakouts." },
      { h: "Feature-request mining", b: "key_moments contains feature-request signals. With slightly more parsing, this becomes the PM's quarterly voice-of-customer summary, generated automatically." },
    ];

    next.forEach((it, idx) => {
      const col = idx % 2;
      const row = Math.floor(idx / 2);
      const x = 0.6 + col * 6.25;
      const y = 1.75 + row * 1.7;
      s.addShape("rect", { x, y, w: 6.0, h: 1.55,
        fill: { color: WHITE }, line: { color: "E5E7EB", width: 1 } });
      s.addShape("rect", { x, y, w: 0.08, h: 1.55,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
      s.addText(it.h, { x: x + 0.25, y: y + 0.1, w: 5.65, h: 0.4,
        fontFace: FONT_HEAD, fontSize: 13, bold: true, color: NAVY, margin: 0 });
      s.addText(it.b, { x: x + 0.25, y: y + 0.5, w: 5.65, h: 1.0,
        fontFace: FONT_BODY, fontSize: 11, color: TEXT_BODY, margin: 0, valign: "top" });
    });

    footer(s, 17);
  }

  // ---------- SLIDE 17: Caveats & assumptions ----------
  {
    const s = p.addSlide();
    slideHeader(s, "Appendix", "Caveats, assumptions, and what to push back on.");

    const items = [
      ["Sample size", "100 transcripts is small. Specific account-level claims (e.g. Cobalt at risk) are evidence not proof. With 1k+ I'd add significance testing."],
      ["Pre-computed labels", "I trust upstream sentiment + topic labels. If those are systemically biased, my aggregates inherit the bias. We should sanity-check on a held-out sample."],
      ["Synthetic-feeling data", "The dataset reads like coherent generated content (a few story arcs, ~32 customers). Findings are still defensible — I treat it as a realistic simulation."],
      ["Speaker-to-domain mapping", "Best-effort match between speakerName and email local-part. I tested it; on this dataset talk-time splits look right (~57/43 on customer calls)."],
      ["Churn risk weights", "Equal weighting on the four signals is a heuristic. With churn outcomes as labels, we'd train weights instead of asserting them."],
      ["Privacy", "Transcripts contain PII (names, customers, emails). Any production version needs proper access controls, redaction options, and audit logs from day one."],
    ];
    items.forEach((it, idx) => {
      const y = 1.75 + idx * 0.82;
      s.addShape("rect", { x: 0.6, y, w: 12.2, h: 0.76,
        fill: { color: idx % 2 === 0 ? WHITE : LIGHT }, line: { color: "E5E7EB", width: 0 } });
      s.addText(it[0], { x: 0.7, y, w: 2.5, h: 0.76,
        fontFace: FONT_HEAD, fontSize: 12, bold: true, color: NAVY, valign: "middle", margin: 0 });
      s.addText(it[1], { x: 3.3, y, w: 9.4, h: 0.76,
        fontFace: FONT_BODY, fontSize: 11, color: TEXT_BODY, valign: "middle", margin: 0 });
    });

    footer(s, 18);
  }

  // ---------- SLIDE 18: closing ----------
  {
    const s = p.addSlide();
    s.background = { color: NAVY_DK };
    s.addText("Thank you.", {
      x: 0.8, y: 2.6, w: 11, h: 1.4,
      fontFace: FONT_HEAD, fontSize: 64, bold: true, color: WHITE, margin: 0,
    });
    s.addShape("rect", { x: 0.8, y: 3.95, w: 0.7, h: 0.06,
      fill: { color: CORAL }, line: { color: CORAL, width: 0 } });
    s.addText("Happy to walk through any of the code in Q&A.\n" +
              "Notebook + pipeline + raw outputs are in the package.", {
      x: 0.8, y: 4.15, w: 11, h: 1.5,
      fontFace: FONT_BODY, fontSize: 18, color: "CADCFC", margin: 0,
    });
  }

  await p.writeFile({ fileName: path.resolve(__dirname,
    "../docs/Transcript_Intelligence_Findings.pptx") });
  console.log("✓ Deck written");
}

build().catch((e) => { console.error(e); process.exit(1); });
