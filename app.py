"""
TalentScout AI — Streamlit Application
AI-Powered Talent Scouting & Engagement Agent
Deccan.ai Catalyst Hackathon
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from agent import TalentScoutAgent

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .hero-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    .hero-box h1 { color: white; margin: 0; font-size: 2rem; }
    .hero-box p  { color: #c4b5fd; margin: 0.5rem 0 0; font-size: 1rem; }

    .score-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
    }
    .step-badge {
        display: inline-block;
        background: #ede9fe;
        color: #5b21b6;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .candidate-rank {
        font-size: 2rem;
        font-weight: 700;
        color: #7c3aed;
        line-height: 1;
    }
    .conversation-bubble-recruiter {
        background: #ede9fe;
        border-radius: 0 12px 12px 12px;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.9rem;
        color: #3b0764;
    }
    .conversation-bubble-candidate {
        background: #f0fdf4;
        border-radius: 12px 0 12px 12px;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.9rem;
        color: #14532d;
        margin-left: 2rem;
    }
    .summary-box {
        background: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

SAMPLE_JD = """Senior Backend Engineer — FinTech Scale-up

We are a fast-growing fintech startup building next-generation payment infrastructure for Southeast Asia. We're looking for a Senior Backend Engineer to join our core platform team.

Responsibilities:
- Design and build scalable microservices handling millions of transactions per day
- Own the payment processing pipeline end-to-end
- Collaborate with product and frontend teams in an agile environment
- Mentor junior engineers and conduct code reviews
- Contribute to system architecture decisions

Requirements:
- 4-7 years of backend engineering experience
- Strong proficiency in Python (FastAPI/Django) or Go
- Experience with distributed systems and message queues (Kafka, RabbitMQ)
- PostgreSQL and Redis expertise required
- Experience in fintech, payments, or banking domain preferred
- Strong understanding of REST APIs and microservices architecture
- Hands-on experience with AWS or GCP

Nice to have:
- Knowledge of compliance and regulatory requirements in fintech
- Kubernetes and Docker experience
- Prior experience at a high-growth startup

Location: Bangalore, India (Hybrid — 3 days/week in office)
Salary: ₹30–50 LPA + equity
Team size: 80 people, Series B stage"""

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 TalentScout AI")
    st.markdown("*Agentic Talent Scouting & Engagement*")
    st.divider()

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get free key at console.groq.com — no credit card needed!",
    )

    model_choice = st.selectbox(
        "Model",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ],
        index=0,
        help="70b = best quality. 8b = faster. mixtral = alternative."
    )

    n_candidates = st.slider(
        "Candidates to scout",
        min_value=4,
        max_value=12,
        value=6,
        step=1,
        help="More candidates = richer results but longer runtime (~30s per candidate)",
    )

    st.divider()

    with st.expander("📐 Scoring Formula"):
        st.markdown("""
**Match Score** _(60% of combined)_
| Dimension | Weight |
|---|---|
| Skills coverage | 40% |
| Experience fit | 30% |
| Domain relevance | 20% |
| Education | 10% |

**Interest Score** _(40% of combined)_
Derived from simulated outreach conversation:
- Enthusiasm of response
- Questions candidate asks
- Availability alignment
- Salary match signals

**Combined Score**
```
0.6 × Match + 0.4 × Interest
```
        """)

    with st.expander("🏗 Architecture"):
        st.markdown("""
```
  JD Text Input
       ↓
  [1] JD Parser Agent
  Extracts structured requirements
       ↓
  [2] Candidate Discovery
  Generates realistic talent pool
       ↓
  [3] Match Scorer Agent
  4-dimension scoring per candidate
       ↓
  [4] Outreach Simulator Agent
  Simulates LinkedIn conversation
       ↓
  [5] Ranker + Report Generator
  Combined score ranking + summary
       ↓
  Ranked Shortlist Output
```
Built with: Groq API (free) + Streamlit
        """)

    with st.expander("ℹ️ About"):
        st.markdown("""
**TalentScout AI**  
Built for Deccan.ai Catalyst Hackathon  

Solves the core recruiter problem:  
hours of manual sifting → seconds of AI-powered shortlisting with full explainability.

Each score is explained. Every conversation is shown.  
Recruiters can act immediately.
        """)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
  <h1>🎯 TalentScout AI</h1>
  <p>AI-Powered Talent Scouting & Engagement Agent — paste a JD, get a ranked shortlist in minutes.</p>
</div>
""", unsafe_allow_html=True)

# ── Input Section ─────────────────────────────────────────────────────────────
col_jd, col_settings = st.columns([3, 1], gap="large")

with col_jd:
    st.markdown("#### 📋 Job Description")

    if st.button("📄 Load Sample JD", type="secondary"):
        st.session_state["jd_text"] = SAMPLE_JD

    jd_text = st.text_area(
        "Job Description",
        value=st.session_state.get("jd_text", ""),
        height=320,
        placeholder="Paste the full job description here...\n\nInclude: role title, required skills, experience range, location, and any domain requirements.",
        label_visibility="collapsed",
    )

with col_settings:
    st.markdown("#### 🗂 Candidate Source")

    source_choice = st.radio(
        "Source",
        ["Auto-generate with AI", "Upload CSV"],
        label_visibility="collapsed",
        help="AI-generate creates realistic synthetic candidates. Upload CSV uses your own list.",
    )

    uploaded_file = None
    if source_choice == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Upload candidates CSV",
            type=["csv"],
            help="Required columns: name, current_title, current_company, years_experience, skills (comma-sep), education, location",
        )
        with st.expander("CSV format"):
            st.code(
                "name,current_title,current_company,years_experience,"
                "skills,education,location,bio,open_to_work,notice_period,expected_salary"
            )
    else:
        st.info(
            f"Will generate **{n_candidates}** realistic, diverse candidates using AI "
            "based on your JD requirements."
        )

    st.markdown("")

    # Validation
    can_run = bool(api_key) and bool(jd_text and jd_text.strip())

    run_btn = st.button(
        "🚀 Start Scouting",
        type="primary",
        use_container_width=True,
        disabled=not can_run,
    )

    if not api_key:
        st.warning("⬅ Enter API key in sidebar")
    elif not jd_text or not jd_text.strip():
        st.info("Paste a job description to begin")


# ── Run Agent ─────────────────────────────────────────────────────────────────
if run_btn and can_run:
    # Clear previous results
    if "results" in st.session_state:
        del st.session_state["results"]

    st.divider()
    st.markdown("### 🤖 Agent Pipeline Running")

    # Parse uploaded CSV if provided
    existing_candidates = None
    if source_choice == "Upload CSV" and uploaded_file is not None:
        try:
            csv_text = uploaded_file.read().decode("utf-8")
            agent_temp = TalentScoutAgent(api_key=api_key, model=model_choice)
            existing_candidates = agent_temp.parse_csv_candidates(csv_text)
            st.success(f"✅ Loaded {len(existing_candidates)} candidates from CSV")
        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")
            st.stop()

    # Progress tracking
    progress_bar = st.progress(0.0)
    status_display = st.empty()
    agent_log = st.empty()
    log_messages = []

    def on_step(step: int, total: int, message: str):
        progress_bar.progress((step - 1) / total)
        status_display.markdown(
            f"<div class='step-badge'>Step {step}/{total}</div> {message}",
            unsafe_allow_html=True,
        )
        log_messages.append(f"**Step {step}:** {message}")
        # Show last 4 log lines
        agent_log.markdown("\n\n".join(log_messages[-4:]))

    # Run the pipeline
    agent = TalentScoutAgent(api_key=api_key, model=model_choice)

    with st.spinner("Agent working..."):
        results = agent.run_pipeline(
            jd_text=jd_text,
            n_candidates=n_candidates,
            existing_candidates=existing_candidates,
            on_step=on_step,
        )

    progress_bar.progress(1.0)

    if results.get("error"):
        status_display.error(f"❌ {results['error']}")
        st.stop()
    else:
        status_display.success(
            f"✅ Scouting complete! Evaluated {len(results['final_ranked'])} candidates."
        )
        st.session_state["results"] = results


# ── Results ───────────────────────────────────────────────────────────────────
if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    final = results["final_ranked"]
    jd = results["jd_parsed"] or {}

    st.divider()
    st.markdown("## 📊 Scouting Results")

    # ── JD Summary strip ──
    if jd:
        with st.expander("📋 Parsed JD Requirements", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Role:** {jd.get('role_title', 'N/A')}")
                st.markdown(f"**Seniority:** {jd.get('seniority', 'N/A')}")
                st.markdown(
                    f"**Experience:** {jd.get('min_experience_years')}-{jd.get('max_experience_years')} yrs"
                )
            with c2:
                st.markdown(f"**Location:** {jd.get('location', 'N/A')}")
                st.markdown(f"**Remote policy:** {jd.get('remote_policy', 'N/A')}")
                st.markdown(f"**Domain:** {jd.get('domain', 'N/A')}")
            with c3:
                skills = jd.get("required_skills", [])
                st.markdown("**Required skills:**")
                st.markdown(", ".join(f"`{s}`" for s in skills[:8]))

    # ── Executive Summary ──
    st.markdown("### 🧠 Executive Summary")
    st.markdown(
        f"<div class='summary-box'>{results.get('executive_summary', '')}</div>",
        unsafe_allow_html=True,
    )

    # ── KPI metrics ──
    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Candidates Evaluated", len(final))
    with m2:
        best_match = max((c["match_score"] for c in final), default=0)
        st.metric("Best Match Score", f"{best_match}/100")
    with m3:
        high_interest = sum(1 for c in final if c["interest_score"] >= 70)
        st.metric("High Interest", f"{high_interest}/{len(final)}")
    with m4:
        avg_combined = sum(c["combined_score"] for c in final) / len(final) if final else 0
        st.metric("Avg Combined Score", f"{avg_combined:.0f}/100")
    with m5:
        ready = sum(1 for c in final if "Schedule" in c.get("next_action", ""))
        st.metric("Ready to Interview", ready)

    st.markdown("---")

    # ── Scatter Plot + Ranked Table ──
    col_plot, col_table = st.columns([1, 1], gap="large")

    with col_plot:
        st.markdown("#### Match vs Interest Matrix")
        st.caption("Top-right quadrant = ideal candidates. Size = Combined Score.")

        df_plot = pd.DataFrame(
            [
                {
                    "Name": c["name"],
                    "Match Score": c["match_score"],
                    "Interest Score": c["interest_score"],
                    "Combined Score": c["combined_score"],
                    "Interest Level": c.get("interest_level", "Unknown"),
                    "Role": c.get("current_title", ""),
                    "Rank": f"#{i}",
                }
                for i, c in enumerate(final, 1)
            ]
        )

        color_map = {
            "High": "#22c55e",
            "Medium": "#f59e0b",
            "Low": "#ef4444",
            "Not Interested": "#94a3b8",
        }

        fig = px.scatter(
            df_plot,
            x="Match Score",
            y="Interest Score",
            size="Combined Score",
            color="Interest Level",
            color_discrete_map=color_map,
            text="Name",
            hover_data=["Role", "Combined Score", "Rank"],
            range_x=[0, 105],
            range_y=[0, 105],
            size_max=30,
        )
        fig.update_traces(textposition="top center", textfont_size=9)
        fig.add_hline(
            y=70, line_dash="dot", line_color="#94a3b8", opacity=0.6,
            annotation_text="Interest threshold (70)"
        )
        fig.add_vline(
            x=70, line_dash="dot", line_color="#94a3b8", opacity=0.6,
            annotation_text="Match threshold (70)"
        )
        fig.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35),
            xaxis_title="Match Score →",
            yaxis_title="Interest Score →",
        )
        st.plotly_chart(fig, use_container_width=True, key="scatter_main_chart")

    with col_table:
        st.markdown("#### Ranked Shortlist")

        def score_color(score):
            if score >= 75:
                return "🟢"
            elif score >= 55:
                return "🟡"
            return "🔴"

        table_rows = [
            {
                "#": i,
                "Candidate": c["name"],
                "Match": c["match_score"],
                "Interest": c["interest_score"],
                "Combined": c["combined_score"],
                "Flag": score_color(c["combined_score"]),
                "Next Action": c.get("next_action", "TBD"),
            }
            for i, c in enumerate(final, 1)
        ]
        df_table = pd.DataFrame(table_rows)

        st.dataframe(
            df_table[["#", "Flag", "Candidate", "Match", "Interest", "Combined", "Next Action"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "Flag": st.column_config.TextColumn(width="small"),
                "Match": st.column_config.ProgressColumn(
                    "Match", min_value=0, max_value=100, format="%d"
                ),
                "Interest": st.column_config.ProgressColumn(
                    "Interest", min_value=0, max_value=100, format="%d"
                ),
                "Combined": st.column_config.ProgressColumn(
                    "Combined", min_value=0, max_value=100, format="%d"
                ),
            },
        )

        # ── Score breakdown chart ──
        st.markdown("#### Score Breakdown")
        df_bar = pd.DataFrame(
            [
                {"Name": c["name"][:16], "Match": c["match_score"], "Interest": c["interest_score"]}
                for c in final[:8]
            ]
        )
        fig2 = go.Figure(
            data=[
                go.Bar(name="Match Score", x=df_bar["Name"], y=df_bar["Match"],
                       marker_color="#7c3aed", opacity=0.85),
                go.Bar(name="Interest Score", x=df_bar["Name"], y=df_bar["Interest"],
                       marker_color="#22c55e", opacity=0.85),
            ]
        )
        fig2.update_layout(
            barmode="group",
            height=220,
            margin=dict(l=10, r=10, t=10, b=60),
            legend=dict(orientation="h", yanchor="bottom", y=-0.5),
            yaxis_range=[0, 100],
        )
        st.plotly_chart(fig2, use_container_width=True, key="bar_scores_chart")

        # ── Download CSV ──
        export_df = pd.DataFrame(
            [
                {
                    "Rank": i,
                    "Name": c["name"],
                    "Current Title": c.get("current_title", ""),
                    "Company": c.get("current_company", ""),
                    "Experience (yrs)": c.get("years_experience", ""),
                    "Match Score": c["match_score"],
                    "Interest Score": c["interest_score"],
                    "Combined Score": c["combined_score"],
                    "Interest Level": c.get("interest_level", ""),
                    "Matched Skills": ", ".join(
                        c.get("match_data", {}).get("matched_skills", [])
                    ),
                    "Missing Skills": ", ".join(
                        c.get("match_data", {}).get("missing_skills", [])
                    ),
                    "Next Action": c.get("next_action", ""),
                    "Timeline": c.get("outreach_data", {}).get("timeline_to_join", ""),
                    "LinkedIn": c.get("linkedin_url", ""),
                    "Location": c.get("location", ""),
                    "Expected Salary": c.get("expected_salary", ""),
                }
                for i, c in enumerate(final, 1)
            ]
        )
        buf = io.StringIO()
        export_df.to_csv(buf, index=False)
        st.download_button(
            "📥 Download Full Report (CSV)",
            data=buf.getvalue(),
            file_name="talentscout_results.csv",
            mime="text/csv",
            use_container_width=True,
            type="secondary",
        )

    # ── Individual Candidate Profiles ──
    st.markdown("---")
    st.markdown("### 👤 Candidate Deep Dives")
    st.caption("Expand each candidate for full match analysis, score breakdown, and simulated conversation.")

    for rank, c in enumerate(final, 1):
        ms = c["match_score"]
        ins = c["interest_score"]
        cs = c["combined_score"]
        md = c.get("match_data", {})
        od = c.get("outreach_data", {})

        flag = "🟢" if cs >= 75 else "🟡" if cs >= 55 else "🔴"
        interest_emoji = {"High": "🔥", "Medium": "👀", "Low": "😐", "Not Interested": "❌"}.get(
            c.get("interest_level", ""), "❓"
        )

        with st.expander(
            f"{flag} #{rank} {c.get('name')} — "
            f"{c.get('current_title')} @ {c.get('current_company')} | "
            f"Combined: {cs}/100 | "
            f"{interest_emoji} {c.get('interest_level', 'Unknown')} Interest",
            expanded=(rank <= 2),
        ):
            # Top metrics
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                st.metric("Match Score", f"{ms}/100",
                          delta=f"{'↑ Strong' if ms>=75 else '→ OK' if ms>=55 else '↓ Weak'}")
            with mc2:
                st.metric("Interest Score", f"{ins}/100",
                          delta=c.get("interest_level", ""))
            with mc3:
                st.metric("Combined Score", f"{cs}/100")
            with mc4:
                st.metric("Next Action", od.get("next_action", "TBD")[:20] + "...")

            st.markdown("---")
            left, right = st.columns(2, gap="large")

            # ── Left: Profile + Match ──
            with left:
                st.markdown("**🧑 Profile**")
                st.markdown(f"- **Experience:** {c.get('years_experience')} years")
                st.markdown(f"- **Location:** {c.get('location', 'N/A')}")
                st.markdown(f"- **Education:** {c.get('education', 'N/A')}")
                st.markdown(f"- **Notice period:** {c.get('notice_period', 'N/A')}")
                st.markdown(f"- **Expected salary:** {c.get('expected_salary', 'N/A')}")
                if c.get("linkedin_url"):
                    st.markdown(f"- **LinkedIn:** [View profile](https://{c['linkedin_url']})")
                if c.get("bio"):
                    st.caption(f"_{c['bio']}_")

                st.markdown("**🛠 Skills**")
                matched = md.get("matched_skills", [])
                missing = md.get("missing_skills", [])
                candidate_skills = c.get("skills", [])

                skill_tags = []
                for s in candidate_skills:
                    if s in matched:
                        skill_tags.append(f"✅ `{s}`")
                    else:
                        skill_tags.append(f"`{s}`")
                st.markdown("  ".join(skill_tags))
                if missing:
                    st.markdown(f"❌ **Missing:** {', '.join(missing)}")

                st.markdown("**📈 Match Breakdown**")
                score_dims = [
                    ("Skills", md.get("skills_score", 0), "#7c3aed"),
                    ("Experience", md.get("experience_score", 0), "#2563eb"),
                    ("Domain", md.get("domain_score", 0), "#0891b2"),
                    ("Education", md.get("education_score", 0), "#16a34a"),
                ]
                for label, val, color in score_dims:
                    fig_mini = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=val,
                            title={"text": label, "font": {"size": 12}},
                            number={"font": {"size": 14}},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": color},
                                "bgcolor": "#f1f5f9",
                            },
                        )
                    )
                    fig_mini.update_layout(height=100, margin=dict(l=10, r=10, t=30, b=0))
                    st.plotly_chart(fig_mini, use_container_width=True, key=f"gauge_{rank}_{label}_{val}")

                st.markdown("**💡 Match Analysis**")
                st.markdown(md.get("match_explanation", "_No analysis available_"))
                if md.get("strengths"):
                    st.markdown("**Strengths:** " + " · ".join(md["strengths"]))
                if md.get("gaps"):
                    st.markdown("**Gaps:** " + " · ".join(md["gaps"]))
                if md.get("recruiter_note"):
                    st.info(f"💡 **Recruiter note:** {md['recruiter_note']}")

            # ── Right: Conversation + Interest ──
            with right:
                st.markdown("**💬 Simulated Outreach Conversation**")

                if od.get("recruiter_message"):
                    st.markdown(
                        f"<div class='conversation-bubble-recruiter'>"
                        f"<b>🤝 Recruiter:</b><br>{od['recruiter_message']}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                if od.get("candidate_reply"):
                    st.markdown(
                        f"<div class='conversation-bubble-candidate'>"
                        f"<b>👤 {c.get('name', 'Candidate')}:</b><br>{od['candidate_reply']}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                if od.get("follow_up_question"):
                    st.markdown(
                        f"<div class='conversation-bubble-recruiter'>"
                        f"<b>🤝 Recruiter:</b><br>{od['follow_up_question']}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                if od.get("candidate_follow_up"):
                    st.markdown(
                        f"<div class='conversation-bubble-candidate'>"
                        f"<b>👤 {c.get('name', 'Candidate')}:</b><br>{od['candidate_follow_up']}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("**📊 Interest Analysis**")
                st.markdown(
                    f"**Level:** {interest_emoji} {od.get('interest_level', 'Unknown')} "
                    f"({ins}/100)"
                )
                st.markdown(od.get("interest_explanation", ""))

                if od.get("interest_indicators"):
                    st.markdown("**✅ Positive signals:**")
                    for sig in od["interest_indicators"]:
                        st.markdown(f"  - {sig}")

                if od.get("red_flags"):
                    st.markdown("**⚠️ Watch out for:**")
                    for flag_item in od["red_flags"]:
                        st.markdown(f"  - {flag_item}")

                st.markdown("---")
                col_action, col_timeline = st.columns(2)
                with col_action:
                    st.markdown(f"**Next Action**")
                    action = od.get("next_action", "TBD")
                    color = (
                        "green" if "Schedule" in action
                        else "orange" if "Send" in action or "Nurture" in action
                        else "red"
                    )
                    st.markdown(f":{color}[**{action}**]")
                with col_timeline:
                    st.markdown(f"**Timeline to join**")
                    st.markdown(f"`{od.get('timeline_to_join', 'Unknown')}`")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<p style='text-align:center;color:#94a3b8;font-size:12px;'>"
        "TalentScout AI · Built for Deccan.ai Catalyst Hackathon · "
        "Powered by Groq API (free) · "
        "Combined Score = 0.6 × Match + 0.4 × Interest"
        "</p>",
        unsafe_allow_html=True,
    )
