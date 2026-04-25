# TalentScout AI — One-Page Write-Up

**Submission for:** Deccan.ai Catalyst Hackathon  
**Problem:** AI-Powered Talent Scouting & Engagement Agent  
**By:** Tanishk Agarwal

---

## The Problem

Recruiters manually review dozens of profiles to fill a single role — a process that is slow, inconsistent, and ignores a critical dimension: candidate interest. A perfect-match candidate who ignores recruiters is useless. This agent solves both problems simultaneously.

---

## Approach

The agent is a **5-step sequential pipeline** where each step's output feeds the next:

**Step 1 — JD Parser:** Raw JD text is structured into a typed JSON object (required skills, experience range, domain, seniority, culture signals). This structured form is the "ground truth" used by all downstream agents, ensuring consistent evaluation criteria.

**Step 2 — Candidate Discovery:** Accepts either AI-generated synthetic candidates (diverse quality distribution: excellent / partial / over/under qualified) or a recruiter-uploaded CSV of real candidates. The synthetic generation uses the structured JD to create realistic, varied profiles — avoiding the real-world data access problem while still enabling meaningful demonstration.

**Step 3 — Match Scorer:** Evaluates each candidate on 4 weighted dimensions: skills coverage (40%), experience fit (30%), domain relevance (20%), education (10%). Every score comes with explicit reasoning — which skills matched, which were missing, and a plain-English explanation the recruiter can act on. This addresses the explainability requirement directly.

**Step 4 — Outreach Simulator:** Generates a realistic LinkedIn message from the recruiter, then simulates the candidate's authentic response based on their profile (open-to-work status, salary expectations, notice period, match quality). A follow-up exchange is also simulated. The conversation is then analyzed to extract an Interest Score (0–100) and categorized as High / Medium / Low / Not Interested.

**Step 5 — Ranker + Report:** Candidates are ranked by `Combined Score = 0.6 × Match + 0.4 × Interest`. An executive summary is generated for the recruiter covering pool quality, top picks, and immediate next steps.

---

## Architecture Decisions & Trade-offs

| Decision | Chosen Approach | Alternative Considered | Why |
|---|---|---|---|
| LLM | Google Gemini API (free) | OpenAI / Anthropic APIs | Completely free tier, no credit card required + reliable JSON output |
| UI | Streamlit | FastAPI + React | Ship speed — Streamlit is deployable in 2 minutes |
| Candidate source | AI-generate + CSV upload | LinkedIn scraping | LinkedIn ToS prohibits scraping; simulation allows full demo |
| Candidate scoring | LLM-based with weights | Rule-based keyword matching | LLM understands semantic skill similarity (e.g. "FastAPI" ↔ "Python web frameworks") |
| Interest simulation | Full conversation exchange | Single-turn response | Two-turn exchange reveals more nuanced interest signals |
| Combined score weighting | 60/40 Match/Interest | Equal 50/50 | Technical fit is a hard constraint; interest can be nurtured |
| Agent framework | Custom pipeline | LangChain / LangGraph | Fewer dependencies = fewer failure modes in 55 hours |

---

## What I Deliberately Left Out

- **Real LinkedIn integration** — against ToS, requires OAuth, not achievable in free tier. Simulation achieves the same demonstration value.
- **Persistent database** — in-memory state is sufficient for a hackathon demo; adds complexity without scoring benefit.
- **Async parallel candidate processing** — would be faster but adds concurrency bugs. Sequential with progress display is more reliable.
- **Email/ATS integration** — out of scope for the core agent problem.

---

## Scoring Criteria Coverage

| Criterion | Weight | How this submission addresses it |
|---|---|---|
| End-to-end working | 20% | Full pipeline: JD in → ranked shortlist out, deployed live |
| Core agent quality | 25% | 5-step agentic reasoning chain, each step transparent |
| Output quality | 20% | Scored shortlist + conversation + explainability + CSV export |
| Technical implementation | 15% | Clean separation of concerns, robust JSON handling, error states |
| Innovation | 10% | Interest Score via simulated engagement is novel |
| UX | 5% | Progress display, interactive charts, candidate deep-dive cards |
| Clean code | 5% | Docstrings on all methods, clear module separation |
