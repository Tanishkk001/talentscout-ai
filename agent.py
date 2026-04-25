"""
TalentScout AI — Core Agent Pipeline
AI-Powered Talent Scouting & Engagement Agent
Deccan.ai Catalyst Hackathon
Powered by: Groq API (free tier — 30 RPM, no credit card needed)

API call budget per run (4 candidates):
  Call 1 : JD Parser
  Call 2 : Candidate Discovery
  Calls 3-6 : Score + Outreach COMBINED (1 call per candidate)
  Call 7 : Executive Summary
  TOTAL  : 7 calls — well within Groq free tier limits
"""

from groq import Groq
import json
import time
import re
from typing import Optional, Callable


class TalentScoutAgent:

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model_name = model
        self.steps_log: list[dict] = []

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _call(self, system: str, user: str) -> str:
        """
        Groq API call with auto-retry on rate limit.
        Groq free tier = 30 RPM — we sleep 3s between calls to stay safe.
        Auto-retries up to 3x with 65s wait on rate limit errors.
        """
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                )
                time.sleep(3)  # 3s gap = max 20 calls/min, safely under 30 RPM
                return response.choices[0].message.content
            except Exception as e:
                err = str(e)
                if "429" in err or "rate" in err.lower() or "limit" in err.lower():
                    if attempt < 2:
                        time.sleep(65)  # wait 65s then retry automatically
                        continue
                raise

    def _call_json(self, system: str, user: str):
        """Groq call returning parsed JSON. Strips markdown fences robustly."""
        json_system = (
            system
            + "\n\nCRITICAL: Your entire response must be valid JSON only. "
            "No markdown fences, no backticks, no explanation. "
            "Start directly with { or [."
        )
        raw = self._call(json_system, user).strip()

        # Strip fences if model wraps anyway
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
            raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Could not parse JSON. Raw:\n{raw[:400]}")

    def _log(self, step: str, detail: str = ""):
        self.steps_log.append({"step": step, "detail": detail})

    # ── Step 1: JD Parser ────────────────────────────────────────────────────

    def parse_jd(self, jd_text: str) -> dict:
        """Extract structured requirements from raw job description."""
        system = (
            "You are an expert technical recruiter with 15 years of experience "
            "analyzing job descriptions across engineering, product, and design roles."
        )
        user = f"""Analyze this job description and extract structured information:

{jd_text}

Return this exact JSON (fill every field, use null if unknown):
{{
  "role_title": "exact job title",
  "company_type": "startup / scale-up / enterprise",
  "required_skills": ["skill1", "skill2"],
  "nice_to_have_skills": ["skill1"],
  "min_experience_years": 3,
  "max_experience_years": 7,
  "education_requirement": "Bachelor's / Master's / PhD / Any",
  "location": "city or remote",
  "remote_policy": "remote / hybrid / onsite",
  "domain": "fintech / SaaS / healthtech etc",
  "seniority": "junior / mid / senior / lead / principal",
  "key_responsibilities": ["responsibility 1", "responsibility 2"],
  "culture_signals": ["fast-paced", "data-driven"],
  "salary_range": "salary range or null"
}}"""
        result = self._call_json(system, user)
        self._log(
            "JD Parsed",
            f"Role: {result.get('role_title')} | "
            f"Skills: {len(result.get('required_skills', []))} required | "
            f"Exp: {result.get('min_experience_years')}-{result.get('max_experience_years')} yrs",
        )
        return result

    # ── Step 2: Candidate Discovery ──────────────────────────────────────────

    def generate_candidates(self, jd_parsed: dict, n: int = 4) -> list:
        """Generate a diverse realistic candidate pool for the JD."""
        system = (
            "You are a talent intelligence API returning realistic diverse candidate "
            "profiles. Use real-sounding names, companies, and career paths."
        )
        user = f"""Generate exactly {n} diverse candidate profiles for this role:

Role: {jd_parsed.get('role_title')}
Required skills: {', '.join(jd_parsed.get('required_skills', []))}
Nice to have: {', '.join(jd_parsed.get('nice_to_have_skills', []))}
Experience: {jd_parsed.get('min_experience_years')}-{jd_parsed.get('max_experience_years')} years
Seniority: {jd_parsed.get('seniority')}
Domain: {jd_parsed.get('domain')}
Location: {jd_parsed.get('location')}

Make them diverse:
- {max(1, n//2)} excellent matches (80-95% skill overlap)
- {max(1, n//3)} partial matches (50-70% skill overlap)
- 1 overqualified or underqualified
- Mix of open_to_work true/false
- Mix of Indian and international names and companies

Return a JSON array of exactly {n} objects:
[
  {{
    "id": 1,
    "name": "Full Name",
    "current_title": "Job Title",
    "current_company": "Company Name",
    "years_experience": 5,
    "skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "education": "Degree, University",
    "location": "City, Country",
    "linkedin_url": "linkedin.com/in/firstname-lastname",
    "bio": "One sentence professional summary.",
    "open_to_work": true,
    "notice_period": "30 days",
    "expected_salary": "25-30 LPA"
  }}
]"""
        result = self._call_json(system, user)
        if isinstance(result, dict):
            result = result.get("candidates", list(result.values())[0] if result else [])
        self._log("Candidates Discovered", f"{len(result)} profiles generated")
        return result

    def parse_csv_candidates(self, csv_data: str) -> list:
        """Parse recruiter-uploaded CSV into candidate dicts."""
        import csv, io
        reader = csv.DictReader(io.StringIO(csv_data))
        candidates = []
        for i, row in enumerate(reader, 1):
            skills_raw = row.get("skills", "")
            skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
            candidates.append({
                "id": i,
                "name": row.get("name", f"Candidate {i}"),
                "current_title": row.get("current_title", ""),
                "current_company": row.get("current_company", ""),
                "years_experience": int(row.get("years_experience", 0) or 0),
                "skills": skills,
                "education": row.get("education", ""),
                "location": row.get("location", ""),
                "linkedin_url": row.get("linkedin_url", ""),
                "bio": row.get("bio", ""),
                "open_to_work": str(row.get("open_to_work", "true")).lower()
                in ("true", "yes", "1"),
                "notice_period": row.get("notice_period", "30 days"),
                "expected_salary": row.get("expected_salary", ""),
            })
        return candidates

    # ── Steps 3+4 COMBINED: Score AND Simulate in ONE API call ───────────────

    def score_and_simulate(self, candidate: dict, jd_parsed: dict) -> tuple:
        """
        COMBINED: scores candidate match AND simulates outreach in ONE API call.
        Returns (match_data, outreach_data) tuple.
        """
        system = (
            "You are a senior technical recruiter with two tasks: "
            "(1) score a candidate's fit for a job across 4 dimensions, "
            "(2) simulate a realistic LinkedIn outreach conversation. "
            "Return both results in one combined JSON."
        )
        user = f"""Complete TWO tasks for this candidate and return ONE combined JSON.

JOB:
Role: {jd_parsed.get('role_title')}
Required skills: {', '.join(jd_parsed.get('required_skills', []))}
Nice to have: {', '.join(jd_parsed.get('nice_to_have_skills', []))}
Experience: {jd_parsed.get('min_experience_years')}-{jd_parsed.get('max_experience_years')} years
Seniority: {jd_parsed.get('seniority')}
Domain: {jd_parsed.get('domain')}
Location: {jd_parsed.get('remote_policy')} in {jd_parsed.get('location')}
Salary: {jd_parsed.get('salary_range', 'competitive')}

CANDIDATE:
Name: {candidate.get('name')}
Title: {candidate.get('current_title')} at {candidate.get('current_company')}
Experience: {candidate.get('years_experience')} years
Skills: {', '.join(candidate.get('skills', []))}
Education: {candidate.get('education')}
Open to work: {candidate.get('open_to_work')}
Notice: {candidate.get('notice_period')}
Expected salary: {candidate.get('expected_salary')}

TASK 1 - SCORING (use full 0-100 range):
skills_score (40%): % of required skills candidate has x 100
experience_score (30%): perfect=100, +-1yr=85, +-2yr=65, 3+yr off=40
domain_score (20%): same=90-100, adjacent=60-75, different=20-40
education_score (10%): meets=80-100, close=60-79, fails=20-50
overall = skills*0.4 + experience*0.3 + domain*0.2 + education*0.1

TASK 2 - OUTREACH SIMULATION:
open_to_work=true AND match>75: enthusiastic, asks questions
open_to_work=true AND match 50-75: interested but cautious
open_to_work=false OR match<50: politely declines
interest_score: High=70-100, Medium=40-69, Low=15-39, Not Interested=0-14

RETURN THIS JSON:
{{
  "match": {{
    "skills_score": 85,
    "experience_score": 75,
    "domain_score": 90,
    "education_score": 80,
    "overall_match_score": 83,
    "matched_skills": ["skills candidate has from required list"],
    "missing_skills": ["required skills candidate lacks"],
    "match_explanation": "2-3 specific sentences explaining the score",
    "strengths": ["strength 1", "strength 2"],
    "gaps": ["gap 1", "gap 2"],
    "recruiter_note": "One actionable insight for the recruiter"
  }},
  "outreach": {{
    "recruiter_message": "Hi [Name], your work at [company] caught my attention. We are building [pitch] and your background in [X] is a strong fit for our [Role]. Would you have 15 minutes this week?",
    "candidate_reply": "Realistic 2-4 sentence response matching their situation",
    "follow_up_question": "One specific recruiter follow-up",
    "candidate_follow_up": "Candidate response to follow-up",
    "interest_indicators": ["positive signal 1", "positive signal 2"],
    "red_flags": ["concern if any, else empty list"],
    "interest_score": 75,
    "interest_level": "High",
    "interest_explanation": "2 sentences explaining this interest score",
    "next_action": "Schedule screening call",
    "timeline_to_join": "30 days"
  }}
}}

interest_level must be exactly: High / Medium / Low / Not Interested
next_action must be exactly one of: Schedule screening call / Send detailed JD / Nurture for 30 days / Archive"""

        result = self._call_json(system, user)
        match_data    = result.get("match", {})
        outreach_data = result.get("outreach", {})

        self._log(
            f"Scored + Simulated: {candidate.get('name')}",
            f"Match: {match_data.get('overall_match_score')}/100 | "
            f"Interest: {outreach_data.get('interest_level')} "
            f"({outreach_data.get('interest_score')}/100)",
        )
        return match_data, outreach_data

    # ── Step 5: Executive Summary ─────────────────────────────────────────────

    def generate_executive_summary(self, candidates_final: list, jd_parsed: dict) -> str:
        total         = len(candidates_final)
        high_interest = sum(1 for c in candidates_final if c.get("interest_score", 0) >= 70)
        avg_match     = sum(c.get("match_score", 0) for c in candidates_final) / total if total else 0
        top3          = [c.get("name", "") for c in candidates_final[:3]]
        ready         = sum(1 for c in candidates_final if "Schedule" in c.get("next_action", ""))

        system = (
            "You are a senior talent acquisition director writing a crisp executive briefing. "
            "Be direct. Speak to a busy hiring manager. No fluff."
        )
        user = f"""Write a 4-sentence executive summary.

Role: {jd_parsed.get('role_title')}
Candidates evaluated: {total}
Average match score: {avg_match:.0f}/100
High-interest candidates: {high_interest}
Ready to interview now: {ready}
Top 3 picks: {', '.join(top3)}

Cover: (1) pool quality, (2) top picks with reasons, (3) next steps."""

        return self._call(system, user)

    # ── Full Pipeline ─────────────────────────────────────────────────────────

    def run_pipeline(
        self,
        jd_text: str,
        n_candidates: int = 4,
        existing_candidates: Optional[list] = None,
        on_step: Optional[Callable] = None,
    ) -> dict:
        """
        Full 5-step pipeline.
        Combined Score = 0.6 x match_score + 0.4 x interest_score
        Total API calls = 7 for 4 candidates (well within Groq free tier).
        """
        results = {
            "jd_parsed": None,
            "candidates": [],
            "final_ranked": [],
            "executive_summary": "",
            "steps_log": [],
            "error": None,
        }

        try:
            # Step 1 — Parse JD
            if on_step:
                on_step(1, 5, "Parsing job description & extracting requirements...")
            results["jd_parsed"] = self.parse_jd(jd_text)

            # Step 2 — Discover candidates
            if on_step:
                on_step(2, 5, f"Discovering {n_candidates} candidate profiles...")
            if existing_candidates:
                candidates = existing_candidates
                self._log("Candidates Loaded", f"{len(candidates)} from CSV")
            else:
                candidates = self.generate_candidates(results["jd_parsed"], n_candidates)
            results["candidates"] = candidates

            # Steps 3+4 — Combined score + outreach per candidate
            scored = []
            total = len(candidates)
            for i, candidate in enumerate(candidates):
                if on_step:
                    on_step(
                        3, 5,
                        f"Scoring & simulating outreach for "
                        f"{candidate.get('name', 'Candidate')} ({i+1}/{total})..."
                    )
                match_data, outreach_data = self.score_and_simulate(
                    candidate, results["jd_parsed"]
                )
                match_score    = int(match_data.get("overall_match_score", 0))
                interest_score = int(outreach_data.get("interest_score", 0))
                combined_score = round(0.6 * match_score + 0.4 * interest_score)

                scored.append({
                    **candidate,
                    "match_score":    match_score,
                    "interest_score": interest_score,
                    "combined_score": combined_score,
                    "interest_level": outreach_data.get("interest_level", "Unknown"),
                    "next_action":    outreach_data.get("next_action", "TBD"),
                    "match_data":     match_data,
                    "outreach_data":  outreach_data,
                })

            # Step 5 — Rank + Summary
            if on_step:
                on_step(5, 5, "Ranking candidates & generating executive summary...")
            results["final_ranked"] = sorted(
                scored, key=lambda x: x["combined_score"], reverse=True
            )
            results["executive_summary"] = self.generate_executive_summary(
                results["final_ranked"], results["jd_parsed"]
            )
            results["steps_log"] = self.steps_log

        except Exception as e:
            err = str(e)
            if "invalid_api_key" in err.lower() or "auth" in err.lower():
                results["error"] = (
                    "Invalid API key. Please check your Groq API key in the sidebar."
                )
            elif "429" in err or "rate" in err.lower() or "limit" in err.lower():
                results["error"] = (
                    "Rate limit hit after 3 auto-retries. "
                    "Please wait 2 minutes then try again."
                )
            else:
                results["error"] = f"Unexpected error: {err}"

        return results
