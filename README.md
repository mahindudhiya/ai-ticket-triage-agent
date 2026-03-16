# AI Ticket Triage Agent
https://triage-dashboard.replit.app/

**An AI-powered support operations pipeline that classifies, prioritizes, and routes Zendesk support tickets at scale.**

Built to simulate the exact workflow that support ops teams run manually today — and show what happens when you automate it.

---

## What It Does

Takes a CSV export of support tickets (Zendesk format) and runs each one through an LLM. For every ticket, the agent outputs:

- **Issue type** — Account Access, Billing, Technical Bug, KYC/Compliance, Portfolio/Trading, Product Education, Feature Request, Security
- **Urgency** — Critical / High / Medium / Low
- **Sentiment** — Angry / Frustrated / Neutral / Positive
- **Automatable?** — Yes/No: can a macro or bot flow fully resolve this without a human?
- **Recommended macro** — the exact next step (e.g. "Trigger Password Reset Email")
- **One-line summary** — for the agent dashboard
- **Estimated handle time** — in minutes

Then it builds a formatted **Excel dashboard** with 4 tabs:
- Executive Summary with KPI cards (containment rate, time saved, critical ticket count)
- All 60 tickets with color-coded urgency and sentiment
- Critical & High priority queue
- Automation candidates with estimated time savings

---

## Key Metrics (from 60-ticket sample batch)

| Metric | Result |
|---|---|
| Total tickets analyzed | 60 |
| Containment rate (automatable) | 33% |
| Estimated time saved per batch | 46 mins |
| Critical tickets surfaced | 8 |
| Avg handle time | ~7.6 min |
| API cost for full batch | < $0.50 |

---

## Why This Matters

In a manual triage workflow, an agent reads each ticket, decides the category, writes a summary, and picks the next step. That takes 5–10 minutes per ticket.

This pipeline does it in under 1 second per ticket, for under a cent each.

The 33% containment rate means 1 in 3 tickets never needs a human agent — it gets a macro response automatically. At scale, that's thousands of hours saved per quarter.

---

## Tech Stack

| Tool | Role |
|---|---|
| Python 3 | Orchestration |
| Anthropic Claude API (Haiku) | Ticket classification |
| pandas | Data handling |
| openpyxl | Excel dashboard generation |
| CSV (mock Zendesk export) | Input data |

---

## Project Structure

```
ticket-triage/
├── mock_tickets.csv        # 60 realistic Zendesk-style support tickets
├── triage_agent.py         # Main agent — reads CSV, calls Claude API, outputs Excel
├── generate_demo.py        # Pre-generates demo output without needing API key
├── triage_output.csv       # Classified ticket data (output)
├── triage_dashboard.xlsx   # Formatted Excel dashboard (output)
└── README.md
```

---

## How to Run

### Option A: Run the live agent (calls Claude API)

```bash
# 1. Install dependencies
pip install anthropic pandas openpyxl

# 2. Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# 3. Run
python triage_agent.py
```

Cost estimate: ~$0.30–$0.50 for 60 tickets using Claude Haiku.

### Option B: Generate the demo dashboard (no API key needed)

```bash
pip install pandas openpyxl
python generate_demo.py
```

This produces the full Excel dashboard using pre-generated classifications — identical output to the live agent.

---

## Design Decisions

**Why Claude Haiku?**
It's the cheapest model in the Claude family that still produces reliable structured JSON. For classification tasks like this, quality doesn't require the most powerful model — consistency and speed matter more. Under $1 for a full batch makes this viable as a daily automation.

**Why Excel output instead of a web dashboard?**
Support ops teams live in Excel and Google Sheets. A file they can open, filter, and share immediately is more useful than a web app that requires a server. The dashboard is designed to be dropped directly into a weekly ops review.

**Why a containment rate metric?**
Containment rate — the percentage of tickets that can be fully resolved without human intervention — is the KPI that matters most in support operations. It directly translates to cost savings and faster resolution times. Every point of containment improvement is measurable.

**Why flag urgency separately from the original Zendesk priority?**
Users self-report priority when submitting tickets. AI-assessed urgency is more consistent — it's based on the actual content of the description, not how the user perceived their own issue. A user saying "low priority" about an unauthorized charge should be escalated regardless.

---

## Guardrails and Edge Cases

- If the API returns malformed JSON, the agent catches the error and writes a fallback classification with "Manual Review Required" as the macro — so no ticket is silently skipped
- Rate limiting is handled with a 300ms pause between API calls
- The prompt is designed to produce **consistent category strings** — the system message defines the exact allowed values so downstream filtering works reliably

---

## What I'd Build Next

1. **Slack integration** — post Critical tickets to a dedicated Slack channel in real time
2. **Auto-send macros** — connect to Zendesk API to actually apply the recommended macro on automatable tickets
3. **Trend dashboard** — track issue type distribution week-over-week to catch emerging product bugs early
4. **CSAT prediction** — add a second LLM call to predict CSAT score based on ticket content and resolution type

---

## Context

Built as part of a workflow optimization portfolio for a support operations role. The ticket data is synthetic but modeled on real Wealthsimple support categories including TFSA/RRSP/FHSA questions, KYC verification flows, billing disputes, and platform bugs.

The goal wasn't to build the most complex system. It was to build the most useful one — something a real ops team could run on Monday morning and immediately get value from.
