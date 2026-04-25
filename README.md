# 🎯 TalentScout AI
### AI-Powered Talent Scouting & Engagement Agent
**Deccan.ai Catalyst Hackathon Submission**

---

## What It Does

Recruiters spend hours manually reviewing profiles and chasing candidate interest. **TalentScout AI** eliminates that.

Paste a Job Description → get a fully ranked, scored, and explained candidate shortlist in minutes — with simulated engagement conversations showing exactly how interested each candidate is.

**Input:** Any raw job description text  
**Output:** Ranked shortlist with Match Score, Interest Score, explainability, and simulated conversations

---

## Live Demo

🔗 **[Deployed App — Click to try](https://talentscout-ai-gvr7ss2cwwwyq7dmybrkkm.streamlit.app/)**

Demo video: [Watch 4-min walkthrough](https://www.loom.com/share/2b979b768b3d4631a599604b7cd9a078)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER: Paste JD Text                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: JD Parser Agent                                     │
│  • Extracts: role title, required skills, experience range   │
│  • Identifies: domain, seniority, location, culture signals  │
│  Output: Structured JSON requirements object                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Candidate Discovery Agent                           │
│  • Mode A: AI-generates diverse realistic candidate pool     │
│  • Mode B: Processes recruiter-uploaded CSV                  │
│  Output: List of candidate profile objects                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
               ┌──────────┴──────────┐
               ▼                     ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│  STEP 3: Match Scorer│  │  STEP 4: Outreach Simulator       │
│  Per candidate:      │  │  Per candidate:                   │
│  • Skills coverage   │  │  • Generates recruiter message    │
│  • Experience fit    │  │  • Simulates candidate reply      │
│  • Domain relevance  │  │  • Analyzes interest signals      │
│  • Education match   │  │  • Derives Interest Score         │
│  Output: Match Score │  │  Output: Interest Score + convo   │
│          0-100       │  │          0-100                    │
└──────────┬───────────┘  └──────────────────┬───────────────┘
           └──────────────┬──────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Ranker + Report Generator                           │
│  • Combined Score = 0.6 × Match + 0.4 × Interest            │
│  • Ranks all candidates by Combined Score                    │
│  • Generates executive summary for recruiter                 │
│  Output: Ranked shortlist + full report                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Scoring Logic

### Match Score (0–100)

Evaluates how well the candidate's profile fits the job requirements.

| Dimension | Weight | How it's calculated |
|---|---|---|
| **Skills coverage** | 40% | % of required skills the candidate has |
| **Experience fit** | 30% | Closeness to the required experience range |
| **Domain relevance** | 20% | How relevant the candidate's industry/domain background is |
| **Education match** | 10% | Whether education meets stated requirements |

Formula: `Match = skills×0.4 + experience×0.3 + domain×0.2 + education×0.1`

### Interest Score (0–100)

Derived from analyzing a simulated recruiter → candidate LinkedIn conversation.

| Score Range | Interest Level | What it means |
|---|---|---|
| 70–100 | 🔥 High | Enthusiastic, asks follow-ups, available quickly |
| 40–69 | 👀 Medium | Mildly interested, needs nurturing |
| 15–39 | 😐 Low | Passive, misaligned expectations |
| 0–14 | ❌ Not Interested | Declined or no response |

Factors analyzed: enthusiasm of response, questions the candidate asks, availability, salary alignment, counter-offers mentioned.

### Combined Score (0–100)

```
Combined = 0.6 × Match Score + 0.4 × Interest Score
```

**Why this weighting?**  
Match is weighted higher (60%) because technical fit is a hard constraint — a highly interested poor-fit candidate is a bad hire. Interest (40%) ensures we prioritize candidates who will actually respond, but acknowledges that passive candidates can be nurtured if the fit is strong.

---

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| LLM Brain | Google Gemini API (free) | Best-in-class instruction following + JSON output |
| UI | Streamlit | Fastest path to a polished, deployable UI |
| Charts | Plotly | Interactive scatter plot + bar charts |
| Data | Pandas | Clean data handling + CSV export |
| Language | Python 3.11 | |

**All free/trial tier.** No paid dependencies beyond Anthropic API credits.

---

## Setup & Run Locally

### Prerequisites
- Python 3.11+
- Gemini API key ([get one free at Google AI Studio](https://aistudio.google.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/talentscout-ai
cd talentscout-ai

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### Usage
1. Enter your Anthropic API key in the sidebar
2. Paste a job description (or click "Load Sample JD")
3. Choose candidate source: AI-generate or upload CSV
4. Click **🚀 Start Scouting**
5. View ranked shortlist, download CSV report

---

## Sample Inputs & Outputs

### Sample Input JD
See [`sample_data/sample_jd.txt`](sample_data/sample_jd.txt)

### Sample Candidate CSV (for upload mode)
See [`sample_data/sample_candidates.csv`](sample_data/sample_candidates.csv)

Required CSV columns:
```
name, current_title, current_company, years_experience,
skills (comma-separated), education, location, bio,
open_to_work (true/false), notice_period, expected_salary
```

### Sample Output

```json
{
  "rank": 1,
  "name": "Kavya Reddy",
  "match_score": 91,
  "interest_score": 82,
  "combined_score": 88,
  "interest_level": "High",
  "matched_skills": ["Python", "Go", "PostgreSQL", "Kafka", "AWS", "Redis"],
  "missing_skills": [],
  "match_explanation": "Kavya has 6 of 6 required skills with direct fintech payment experience at Stripe...",
  "next_action": "Schedule screening call",
  "timeline_to_join": "60 days"
}
```

---

## Project Structure

```
talentscout-ai/
├── app.py                    # Streamlit UI — all pages and visualizations
├── agent.py                  # TalentScoutAgent — 5-step pipeline logic
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── README.md                 # This file
├── writeup.md                # One-page approach & architecture write-up
└── sample_data/
    ├── sample_jd.txt         # Example job description
    └── sample_candidates.csv # Example candidate data for CSV upload
```

---

## APIs & Tools Used

| Tool | Usage | Tier |
|---|---|---|
| Google Gemini API (free) | All LLM calls (JD parsing, scoring, simulation) | Free/paid |
| Streamlit | Web UI + deployment | Free |
| Plotly | Interactive visualizations | Free (open source) |

---

## Deployment

### Deploy to Streamlit Cloud (recommended, free)

1. Push this repo to GitHub (public)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub → select this repo → set main file: `app.py`
4. Deploy (takes ~2 minutes)
5. Share the live URL

No secrets needed in the repo — users enter their own API key in the sidebar.

---

## Built By

Tanishk Agarwal  
Deccan.ai Catalyst Hackathon — April 2026
