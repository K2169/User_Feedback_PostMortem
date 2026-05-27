print("APP1 IS RUNNING")
import streamlit as st
import pandas as pd
import json, re, os, time
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from groq import Groq


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


st.set_page_config(
    page_title="Feedback Postmortem",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #07090f;
    --surface:  #0f1117;
    --surface2: #161820;
    --border:   rgba(255,255,255,0.06);
    --border2:  rgba(255,255,255,0.10);
    --text:     #e8eaf0;
    --muted:    #5c607a;
    --accent:   #6e56ff;
    --green:    #34d399;
    --orange:   #fb923c;
    --red:      #f43f5e;
    --blue:     #38bdf8;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label { color: var(--muted) !important; font-size: 11px !important; }

/* ── file uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1px dashed rgba(110,86,255,0.4) !important;
    border-radius: 10px !important;
}

/* ── buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.6rem 1.6rem !important;
    letter-spacing: 0.01em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── download buttons ── */
[data-testid="stDownloadButton"] > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
}

/* ── dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 10px !important; }
[data-testid="stDataFrame"] * { font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }

/* ── tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 20px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--text) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── expanders ── */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* ── progress ── */
.stProgress > div > div { background: var(--accent) !important; }

/* ── custom components ── */
.page-header { padding: 2rem 0 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
.page-header-eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--accent); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px; }
.page-header-title { font-size: 32px; font-weight: 700; color: var(--text); line-height: 1.15; margin: 0; }
.page-header-sub { font-size: 14px; color: var(--muted); margin-top: 8px; font-weight: 400; }

.section-header { display: flex; align-items: center; gap: 10px; margin: 2.5rem 0 1.2rem; }
.section-header-line { flex: 1; height: 1px; background: var(--border); }
.section-header-text { font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; white-space: nowrap; }

.kpi-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 12px; margin-bottom: 2rem; }
.kpi-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 18px; }
.kpi-value { font-size: 28px; font-weight: 700; color: var(--text); line-height: 1; font-family: 'Space Grotesk', sans-serif; }
.kpi-label { font-size: 11px; color: var(--muted); margin-top: 6px; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.04em; }
.kpi-delta { font-size: 11px; margin-top: 4px; font-weight: 500; }

.exec-brief { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 24px 28px; margin-bottom: 2rem; }
.exec-brief-title { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--accent); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 16px; }
.exec-bullet { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.exec-bullet:last-child { border-bottom: none; padding-bottom: 0; }
.exec-bullet-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); flex-shrink: 0; margin-top: 7px; }
.exec-bullet-text { font-size: 14px; color: var(--text); line-height: 1.65; }
.exec-bullet-text b { color: var(--accent); font-weight: 600; }

.watchlist-item { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; margin-bottom: 10px; }
.watchlist-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.watchlist-name { font-size: 15px; font-weight: 600; color: var(--text); }
.watchlist-meta { font-size: 12px; color: var(--muted); margin-top: 2px; font-family: 'JetBrains Mono', monospace; }
.watchlist-risk { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; }
.watchlist-bar-track { height: 3px; background: var(--surface2); border-radius: 99px; margin: 8px 0; }
.watchlist-bar-fill { height: 3px; border-radius: 99px; }
.watchlist-feedback { font-size: 13px; color: #9099b5; line-height: 1.6; font-style: italic; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border); }
.watchlist-action { font-size: 12px; color: var(--accent); margin-top: 8px; font-weight: 500; }
.watchlist-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }

.tag-pill { font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 3px 9px; border-radius: 99px; border: 1px solid; display: inline-block; }
.tag-bug      { color: #f43f5e; border-color: rgba(244,63,94,0.3);  background: rgba(244,63,94,0.08); }
.tag-churn    { color: #fb923c; border-color: rgba(251,146,60,0.3); background: rgba(251,146,60,0.08); }
.tag-praise   { color: #34d399; border-color: rgba(52,211,153,0.3); background: rgba(52,211,153,0.08); }
.tag-feature  { color: #38bdf8; border-color: rgba(56,189,248,0.3); background: rgba(56,189,248,0.08); }
.tag-neutral  { color: #5c607a; border-color: rgba(92,96,122,0.3);  background: rgba(92,96,122,0.08); }

.bug-row { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 20px; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 16px; }
.bug-urgency-badge { font-family: 'JetBrains Mono', monospace; font-size: 11px; padding: 4px 10px; border-radius: 6px; white-space: nowrap; flex-shrink: 0; font-weight: 600; }
.bug-content { flex: 1; }
.bug-name { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.bug-summary { font-size: 13px; color: #9099b5; line-height: 1.55; font-style: italic; }
.bug-action { font-size: 12px; color: var(--accent); margin-top: 6px; font-weight: 500; }
.bug-root { font-size: 11px; color: var(--muted); font-family: 'JetBrains Mono', monospace; margin-top: 4px; }

.feat-row { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; margin-bottom: 8px; }
.feat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.feat-name { font-size: 14px; font-weight: 600; color: var(--text); }
.feat-demand { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--muted); }
.feat-why { font-size: 13px; color: #9099b5; line-height: 1.6; }
.feat-priority { font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 3px 10px; border-radius: 99px; font-weight: 600; }

.praise-row { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--green); border-radius: 12px; padding: 16px 20px; margin-bottom: 8px; }
.praise-meta { font-size: 11px; color: var(--green); font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; }
.praise-text { font-size: 13px; color: #9099b5; line-height: 1.65; font-style: italic; }

.empty-state { text-align: center; padding: 48px; color: var(--muted); font-size: 14px; }

.upload-zone { background: var(--surface); border: 1px dashed rgba(110,86,255,0.35); border-radius: 16px; padding: 64px 40px; text-align: center; margin-top: 32px; }
.upload-zone-icon { font-size: 48px; margin-bottom: 16px; }
.upload-zone-title { font-size: 22px; font-weight: 700; color: var(--text); margin-bottom: 8px; }
.upload-zone-sub { font-size: 13px; color: var(--muted); max-width: 380px; margin: 0 auto; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk", color="#9099b5", size=12),
    title_font=dict(family="Space Grotesk", color="#e8eaf0", size=14),
    legend=dict(font=dict(color="#9099b5", size=11)),
    margin=dict(t=44, b=16, l=16, r=16),
)
GRID = dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)")

TAG_COLORS = {
    "Bug": "#f43f5e",
    "Churn Risk": "#fb923c",
    "Feature Request": "#38bdf8",
    "Praise": "#34d399",
    "Neutral": "#5c607a",
}

def generate_ai_response(prompt, temperature=0.3, retries=3):
    """
    Universal Groq AI helper
    """
    print("========== GROQ FUNCTION CALLED ==========")

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=2048
            )
            print("========== GROQ RESPONSE RECEIVED ==========")

            return response.choices[0].message.content

        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")

    return "AI generation failed."

print(generate_ai_response("Say hello in one line"))

def safe_json(text: str):
    text = text.strip()
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None

def section(label: str):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-line"></div>
        <div class="section-header-text">{label}</div>
        <div class="section-header-line"></div>
    </div>""", unsafe_allow_html=True)

def tag_pill(tag: str) -> str:
    css = {"Bug":"tag-bug","Churn Risk":"tag-churn","Praise":"tag-praise",
           "Feature Request":"tag-feature","Neutral":"tag-neutral"}.get(tag,"tag-neutral")
    return f'<span class="tag-pill {css}">{tag}</span>'


# ─────────────────────────────────────────────────────────────────────────────
# AI FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def tag_row(row: dict) -> dict:
    prompt = f"""You are a senior product analyst, for any Indian tech startup.

Analyse this user feedback and return ONLY valid JSON — no markdown, no explanation.

Input:
- Raw Feedback: {row.get('Raw Feedback', '')}
- Existing Category: {row.get('Feedback Category', '')}
- Sentiment: {row.get('Sentiment', '')}
- Persona: {row.get('Persona Type', '')} | Age: {row.get('Age', '')} | Level: {row.get('English Level', '')}
- Lessons Done: {row.get('No. of Lessons Done', 0)} | Streak: {row.get('Streaks', 0)}
- Friction — Paywall: {row.get('Friction: Paywall','')}, UX: {row.get('Friction: UX','')}, Content: {row.get('Friction: Content','')}, Bug: {row.get('Friction: Tech Bug','')}
- Feature Complained About: {row.get('Feature Complained About','')}
- Drop-off Point: {row.get('Drop-off Point', '')}
- Competitor Mentioned: {row.get('Competitor Mentioned', '')}
- Action Taken: {row.get('Action Taken', '')}

Return ONLY this JSON:
{{
  "tag": "Bug" | "Feature Request" | "Praise" | "Churn Risk" | "Neutral",
  "sentiment_score": <1-10>,
  "urgency_score": <1-10, how fast PM must act>,
  "churn_probability": <0-100, % chance this user churns in next 7 days>,
  "root_cause": "UX" | "Performance" | "Content" | "Pricing" | "Engagement" | "AI Feature" | "Support" | "Habit Loop",
  "impact": "Critical" | "High" | "Medium" | "Low",
  "pm_action": "<one crisp actionable sentence for the PM>",
  "summary": "<one plain English sentence summarising this feedback>",
  "persona_insight": "<one sentence about what this tells us about this persona segment>",
  "retention_signal": "positive" | "negative" | "neutral"
}}"""
    try:
        resp = generate_ai_response(prompt)
        result = safe_json(resp)
        if isinstance(result, dict):
            return result
    except Exception as e:
        pass
    return {
        "tag": "Neutral", "sentiment_score": 5, "urgency_score": 5,
        "churn_probability": 30, "root_cause": "Content", "impact": "Medium",
        "pm_action": "Review manually", "summary": str(row.get("Raw Feedback",""))[:100],
        "persona_insight": "Insufficient data", "retention_signal": "neutral"
    }


def gen_executive_summary(df: pd.DataFrame, tagged: list) -> str:
    churn_ct = sum(1 for t in tagged if t.get("tag") == "Churn Risk")
    bug_ct   = sum(1 for t in tagged if t.get("tag") == "Bug")
    praise_ct= sum(1 for t in tagged if t.get("tag") == "Praise")
    feat_ct  = sum(1 for t in tagged if t.get("tag") == "Feature Request")
    avg_sent = round(sum(t.get("sentiment_score",5) for t in tagged)/len(tagged),1)
    avg_churn= round(sum(t.get("churn_probability",30) for t in tagged)/len(tagged))
    critical = sum(1 for t in tagged if t.get("impact") == "Critical")

    top_dropoff = df["Drop-off Point"].value_counts().head(2).to_dict() if "Drop-off Point" in df.columns else {}
    top_complaint = df["Feature Complained About"].value_counts().head(3).to_dict() if "Feature Complained About" in df.columns else {}
    competitors = df["Competitor Mentioned"].value_counts().to_dict() if "Competitor Mentioned" in df.columns else {}
    sample_fb = df["Raw Feedback"].dropna().sample(min(12,len(df))).tolist()

    prompt = f"""You are a senior PM writing an executive postmortem for the EnglishBhashi founding team.

Data:
- Total entries: {len(tagged)}
- Bugs: {bug_ct} | Churn Risk: {churn_ct} | Praise: {praise_ct} | Feature Requests: {feat_ct}
- Avg Sentiment: {avg_sent}/10 | Avg Churn Probability: {avg_churn}% | Critical Issues: {critical}
- Top drop-off points: {top_dropoff}
- Top complained features: {top_complaint}
- Competitors mentioned: {competitors}
- Sample raw feedback: {sample_fb[:8]}

Write exactly 5 bullets. Each bullet:
- Starts with **Category Label:** (e.g. **Critical Bug:**, **Retention Risk:**, **AI Experience:**, **Growth Signal:**, **Immediate Action Required:**)
- Is specific, data-backed, and actionable
- Max 2 sentences per bullet
- Written for a CPO/founder reading in 60 seconds

Return plain text, 5 bullets only, no headers, no intro."""
    try:
        return generate_ai_response(prompt).strip()
    except Exception as e:
        return f"Could not generate summary: {e}"


def gen_feature_insights(df: pd.DataFrame) -> str:
    feedbacks = df["Raw Feedback"].dropna().tolist()
    prompt = f"""You are a PM analysing feature requests for an Indian English-learning app (EnglishBhashi).

Analyse these {len(feedbacks)} feedback entries. Find the top 6 most impactful features or improvements requested.

For each return:
- feature: short name
- estimated_demand: "X% of users" or "~N users"
- why_it_matters: one sentence, specific to this app's user base (Tier 2-3 India, beginner English learners)
- priority: "Critical" | "High" | "Medium" | "Low"
- effort: "Low" | "Medium" | "High"
- quick_win: true | false (can this be shipped in <2 weeks?)

Return ONLY a JSON array. No markdown, no preamble.

Feedbacks sample:
{chr(10).join(f'- {f}' for f in feedbacks[:40])}"""
    try:
        return generate_ai_response(prompt).strip()
    except Exception:
        return "[]"


def gen_persona_insights(df: pd.DataFrame, tagged: list) -> str:
    enriched_sample = []
    for i, (_, row) in enumerate(df.head(30).iterrows()):
        t = tagged[i] if i < len(tagged) else {}
        enriched_sample.append({
            "persona": row.get("Persona Type",""),
            "age": row.get("Age",""),
            "level": row.get("English Level",""),
            "sentiment": t.get("sentiment_score",5),
            "churn": t.get("churn_probability",30),
            "tag": t.get("tag",""),
            "root_cause": t.get("root_cause",""),
            "insight": t.get("persona_insight","")
        })

    prompt = f"""You are a PM doing a persona segmentation analysis for EnglishBhashi.

Based on this enriched feedback data, write a PM-ready persona analysis. Cover:
1. Which persona has the highest churn risk and why
2. Which persona is most engaged and what drives them
3. Which persona needs the most product attention right now
4. One cross-persona pattern you noticed
5. One persona-specific recommendation that would move the retention needle

Data: {json.dumps(enriched_sample)}

Write in clean bullet points. Be specific. Reference persona names (Student, Working Professional, Homemaker, Job Seeker, Business). Max 5 bullets, 2 sentences each. Plain text only."""
    try:
        return generate_ai_response(prompt).strip()
    except Exception:
        return "Could not generate persona insights."


def gen_competitor_analysis(df: pd.DataFrame) -> str:
    if "Competitor Mentioned" not in df.columns:
        return ""
    competitor_feedback = []
    for _, row in df.iterrows():
        comp = str(row.get("Competitor Mentioned","")).strip()
        if comp and comp.lower() not in ["nan","none",""]:
            competitor_feedback.append({
                "competitor": comp,
                "feedback": row.get("Raw Feedback","")[:200],
                "sentiment": row.get("Sentiment","")
            })
    if not competitor_feedback:
        return ""
    prompt = f"""You are a PM doing competitive analysis for EnglishBhashi based on user feedback.

Users mentioned these competitors: {competitor_feedback}

Write a concise PM competitive brief:
1. Which competitor is mentioned most and what users prefer about it
2. What EnglishBhashi does better (from user feedback)
3. One immediate product change that would win users back from the top competitor
4. One long-term moat EnglishBhashi should build

Max 4 bullets, plain text, 1-2 sentences each."""
    try:
        return generate_ai_response(prompt).strip()
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 24px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6e56ff;
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">
            // Product Tool
        </div>
        <div style="font-size:20px;font-weight:700;color:#e8eaf0;line-height:1.2;">
            Feedback<br>Postmortem
        </div>
        <div style="font-size:11px;color:#5c607a;margin-top:6px;">
            EnglishBhashi · AI-Powered
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed",
                                 help="Upload your Daily Feedback Log CSV")
    st.caption("Upload your feedback CSV above")

    st.markdown("---")
    st.markdown("<div style='font-size:11px;color:#5c607a;font-family:JetBrains Mono,monospace;margin-bottom:8px;'>FILTERS</div>", unsafe_allow_html=True)
    filter_sentiment  = st.multiselect("Sentiment",   ["Positive","Negative","Neutral","Mixed"])
    filter_persona    = st.multiselect("Persona",     ["Student","Working Professional","Homemaker","Job Seeker","Business","Other"])
    filter_category   = st.multiselect("Category",   ["Content Quality","Technical Bug","Engagement/Retention","Subscription/Paywall"])
    filter_dropoff    = st.multiselect("Drop-off Point", ["No Habit loop","No Motivation","Streak Break","Pricing high","Content too hard","Technical Bug","Lessons Complex","Less Engaging","UI/UX issues"])

    st.markdown("---")
    max_rows = st.slider("Max rows to analyse", 10, 100, 25, 5)

    st.markdown("---")
    st.markdown("<div style='font-size:11px;color:#5c607a;'>Built by Krishnam Parasrampuria</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-header-eyebrow">// User Feedback Postmortem · EnglishBhashi</div>
    <div style="display:flex;align-items:baseline;gap:16px;">
        <div class="page-header-title">Postmortem Dashboard</div>
    </div>
    <div class="page-header-sub">
        Upload your feedback CSV · AI enriches every entry · Get PM-ready intelligence in minutes
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-zone-icon">📂</div>
        <div class="upload-zone-title">Upload your feedback CSV to begin</div>
        <div class="upload-zone-sub">
            Use the sidebar uploader. Works with your EnglishBhashi Daily Feedback Log format —
            expects columns like Raw Feedback, Feedback Category, Sentiment, Persona Type,
            Age, Streaks, No. of Lessons Done, Drop-off Point, and more.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# LOAD & FILTER
# ─────────────────────────────────────────────────────────────────────────────
df_raw = pd.read_csv(uploaded)
df_raw.columns = df_raw.columns.str.strip()
df = df_raw.copy()

if filter_sentiment:
    df = df[df["Sentiment"].isin(filter_sentiment)] if "Sentiment" in df.columns else df
if filter_persona:
    df = df[df["Persona Type"].isin(filter_persona)] if "Persona Type" in df.columns else df
if filter_category:
    df = df[df["Feedback Category"].isin(filter_category)] if "Feedback Category" in df.columns else df
if filter_dropoff:
    df = df[df["Drop-off Point"].isin(filter_dropoff)] if "Drop-off Point" in df.columns else df

if df.empty:
    st.warning("No entries match your filters. Adjust the sidebar filters.")
    st.stop()

st.markdown(f"<div style='font-size:12px;color:#5c607a;font-family:JetBrains Mono,monospace;margin-bottom:20px;'>{len(df)} of {len(df_raw)} entries after filters</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RUN ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([2,5])
with col_btn:
    run = st.button("🔬  Run Postmortem Analysis")
with col_info:
    st.markdown(f"<div style='font-size:12px;color:#5c607a;padding-top:10px;'>Will analyse up to {max_rows} rows · ~{max_rows*2}s</div>", unsafe_allow_html=True)

if "results" not in st.session_state:
    st.session_state.results = None

if run:
    total = min(len(df), max_rows)
    prog  = st.progress(0, "Starting AI enrichment...")
    tagged = []

    for i, (_, row) in enumerate(df.head(total).iterrows()):
        prog.progress((i+1)/total, f"Enriching entry {i+1} of {total}…")
        tagged.append(tag_row(row.to_dict()))
        time.sleep(0.1)

    prog.progress(1.0, "Generating executive summary…")
    exec_sum  = gen_executive_summary(df.head(total), tagged)

    prog.progress(1.0, "Analysing feature requests…")
    feat_raw  = gen_feature_insights(df.head(total))

    prog.progress(1.0, "Persona segmentation…")
    persona_insights = gen_persona_insights(df.head(total), tagged)

    prog.progress(1.0, "Competitive analysis…")
    comp_insights = gen_competitor_analysis(df.head(total))

    enriched = df.head(total).copy()
    for key, col in [
        ("tag","AI Tag"), ("sentiment_score","Sentiment Score"),
        ("urgency_score","Urgency Score"), ("churn_probability","Churn %"),
        ("root_cause","Root Cause"), ("impact","Impact"),
        ("pm_action","PM Action"), ("summary","AI Summary"),
        ("persona_insight","Persona Insight"), ("retention_signal","Retention Signal")
    ]:
        enriched[col] = [t.get(key,"") for t in tagged]

    st.session_state.results = dict(
        tagged=tagged, enriched=enriched,
        exec_sum=exec_sum, feat_raw=feat_raw,
        persona_insights=persona_insights,
        comp_insights=comp_insights
    )
    prog.empty()
    st.success(f"✓ Postmortem complete — {total} entries enriched across 4 AI modules")

if not st.session_state.results:
    st.markdown("<div class='empty-state'>Click <strong>Run Postmortem Analysis</strong> to begin.</div>", unsafe_allow_html=True)
    st.stop()

R       = st.session_state.results
enriched = R["enriched"]
tagged   = R["tagged"]


# ─────────────────────────────────────────────────────────────────────────────
# KPI BAR
# ─────────────────────────────────────────────────────────────────────────────
section("Overview")

total_n  = len(enriched)
avg_sent = round(enriched["Sentiment Score"].mean(), 1)
avg_churn= round(enriched["Churn %"].mean())
hi_churn = int((enriched["Churn %"] >= 65).sum())
critical = int((enriched["Impact"] == "Critical").sum())
urgent   = int((enriched["Urgency Score"] >= 8).sum())

sent_color  = "#34d399" if avg_sent >= 7 else "#fb923c" if avg_sent >= 5 else "#f43f5e"
churn_color = "#f43f5e" if avg_churn >= 50 else "#fb923c" if avg_churn >= 35 else "#34d399"

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-value">{total_n}</div>
    <div class="kpi-label">Entries Analysed</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:{sent_color}">{avg_sent}/10</div>
    <div class="kpi-label">Avg Sentiment Score</div>
    <div class="kpi-delta" style="color:{sent_color}">{"↑ Good" if avg_sent>=7 else "↓ Needs attention"}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:{churn_color}">{avg_churn}%</div>
    <div class="kpi-label">Avg Churn Probability</div>
    <div class="kpi-delta" style="color:{churn_color}">{"⚠ High" if avg_churn>=50 else "Moderate"}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#f43f5e">{hi_churn}</div>
    <div class="kpi-label">High-Risk Users (≥65%)</div>
    <div class="kpi-delta" style="color:#5c607a">{round(hi_churn/total_n*100)}% of batch</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#f43f5e">{critical}</div>
    <div class="kpi-label">Critical Issues</div>
    <div class="kpi-delta" style="color:#5c607a">{urgent} urgent actions</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📋  Executive Brief",
    "📊  Distribution",
    "🚨  Churn Watchlist",
    "🐛  Bug Matrix",
    "💡  Feature Map",
    "✅  Praise",
    "👥  Personas",
    "🏁  Competitors",
    "🗂  Full Table",
    "⬇  Export"
])


# ── TAB 1: EXECUTIVE BRIEF ───────────────────────────────────────────────────
with tabs[0]:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    lines = [l.strip() for l in R["exec_sum"].split("\n") if l.strip()]
    st.markdown("<div class='exec-brief'><div class='exec-brief-title'>PM Executive Brief · AI Generated</div>", unsafe_allow_html=True)
    for line in lines:
        clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line).lstrip("-• ").strip()
        if clean:
            st.markdown(f"""
            <div class="exec-bullet">
                <div class="exec-bullet-dot"></div>
                <div class="exec-bullet-text">{clean}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # quick tag summary under brief
    tag_counts = enriched["AI Tag"].value_counts()
    c1,c2,c3,c4,c5 = st.columns(5)
    for col, tag, css in [
        (c1,"Bug","tag-bug"), (c2,"Churn Risk","tag-churn"),
        (c3,"Feature Request","tag-feature"), (c4,"Praise","tag-praise"), (c5,"Neutral","tag-neutral")
    ]:
        count = tag_counts.get(tag, 0)
        with col:
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;
                        padding:16px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:#e8eaf0;">{count}</div>
                <div class="tag-pill {css}" style="margin-top:6px;">{tag}</div>
            </div>""", unsafe_allow_html=True)


# ── TAB 2: DISTRIBUTION ──────────────────────────────────────────────────────
with tabs[1]:
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        tag_df = enriched["AI Tag"].value_counts().reset_index()
        tag_df.columns = ["Tag","Count"]
        fig = px.donut = go.Figure(go.Pie(
            labels=tag_df["Tag"], values=tag_df["Count"],
            hole=0.55,
            marker=dict(colors=[TAG_COLORS.get(t,"#5c607a") for t in tag_df["Tag"]],
                        line=dict(color="#07090f", width=2))
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Tag Distribution")
        fig.update_traces(textfont_color="#e8eaf0", textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        rc_df = enriched["Root Cause"].value_counts().reset_index()
        rc_df.columns = ["Root Cause","Count"]
        fig2 = px.bar(rc_df, x="Count", y="Root Cause", orientation="h",
                      color="Count", color_continuous_scale=["#1a1a2e","#6e56ff"])
        fig2.update_layout(**PLOT_LAYOUT, title="Root Cause Breakdown",
                           yaxis=dict(**GRID), xaxis=dict(**GRID),
                           coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    r2c1, r2c2 = st.columns(2)

    with r2c1:
        fig3 = px.scatter(enriched, x="Urgency Score", y="Churn %",
                          color="AI Tag", size="Sentiment Score",
                          hover_data=["Name","AI Summary"] if "Name" in enriched.columns else ["AI Summary"],
                          color_discrete_map=TAG_COLORS)
        fig3.update_layout(**PLOT_LAYOUT, title="Urgency vs Churn Risk",
                           xaxis=dict(**GRID, title="Urgency Score"),
                           yaxis=dict(**GRID, title="Churn Probability %"))
        st.plotly_chart(fig3, use_container_width=True)

    with r2c2:
        if "Persona Type" in enriched.columns:
            pdata = enriched.groupby("Persona Type").agg(
                avg_sent=("Sentiment Score","mean"),
                avg_churn=("Churn %","mean"),
                count=("AI Tag","count")
            ).reset_index()
            fig4 = px.scatter(pdata, x="avg_sent", y="avg_churn",
                              size="count", color="avg_churn", text="Persona Type",
                              color_continuous_scale=["#34d399","#fb923c","#f43f5e"])
            fig4.update_traces(textposition="top center", textfont_color="#e8eaf0", textfont_size=11)
            fig4.update_layout(**PLOT_LAYOUT, title="Persona: Sentiment vs Churn",
                               coloraxis_showscale=False,
                               xaxis=dict(**GRID, title="Avg Sentiment"),
                               yaxis=dict(**GRID, title="Avg Churn %"))
            st.plotly_chart(fig4, use_container_width=True)

    r3c1, r3c2 = st.columns(2)

    with r3c1:
        if "Drop-off Point" in enriched.columns:
            drop_df = enriched["Drop-off Point"].dropna()
            drop_df = drop_df[drop_df.str.strip().str.lower().isin(["none as such","nan","none"]) == False]
            if len(drop_df) > 0:
                drop_counts = drop_df.value_counts().reset_index()
                drop_counts.columns = ["Drop-off","Count"]
                fig5 = px.bar(drop_counts, x="Drop-off", y="Count",
                              color="Count", color_continuous_scale=["#1a1a2e","#fb923c"])
                fig5.update_layout(**PLOT_LAYOUT, title="Drop-off Points",
                                   xaxis=dict(**GRID, tickangle=-35),
                                   yaxis=dict(**GRID), coloraxis_showscale=False)
                st.plotly_chart(fig5, use_container_width=True)

    with r3c2:
        if "Retention Signal" in enriched.columns:
            ret_df = enriched["Retention Signal"].value_counts().reset_index()
            ret_df.columns = ["Signal","Count"]
            colors_map = {"positive":"#34d399","negative":"#f43f5e","neutral":"#5c607a"}
            fig6 = go.Figure(go.Bar(
                x=ret_df["Signal"], y=ret_df["Count"],
                marker_color=[colors_map.get(s,"#5c607a") for s in ret_df["Signal"]],
                marker_line_color="#07090f", marker_line_width=2
            ))
            fig6.update_layout(**PLOT_LAYOUT, title="Retention Signal Distribution",
                               xaxis=dict(**GRID), yaxis=dict(**GRID))
            st.plotly_chart(fig6, use_container_width=True)


# ── TAB 3: CHURN WATCHLIST ───────────────────────────────────────────────────
with tabs[2]:
    churn_df = enriched[enriched["Churn %"] >= 55].sort_values("Churn %", ascending=False)

    if churn_df.empty:
        st.markdown("<div class='empty-state'>No high-risk churn users in this batch.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:13px;color:#5c607a;margin-bottom:16px;font-family:JetBrains Mono,monospace;'>{len(churn_df)} users at ≥55% churn risk</div>", unsafe_allow_html=True)
        for _, row in churn_df.iterrows():
            cp = row.get("Churn %", 0)
            bar_color = "#f43f5e" if cp >= 80 else "#fb923c" if cp >= 65 else "#facc15"
            lessons = row.get("No. of Lessons Done", "—")
            streak  = row.get("Streaks", "—")
            persona = row.get("Persona Type","")
            age     = row.get("Age","")
            urgency = row.get("Urgency Score",5)
            root    = row.get("Root Cause","")
            name    = row.get("Name", "Anonymous")
            feedback_text = row.get("AI Summary") or row.get("Raw Feedback","")
            action  = row.get("PM Action","Review manually")
            tag     = row.get("AI Tag","Churn Risk")

            st.markdown(f"""
            <div class="watchlist-item">
                <div class="watchlist-header">
                    <div>
                        <div class="watchlist-name">{name}</div>
                        <div class="watchlist-meta">{persona} · {age} · {lessons} lessons · Streak {streak}</div>
                    </div>
                    <div>
                        <div class="watchlist-risk" style="color:{bar_color};">{cp:.0f}% churn risk</div>
                        <div style="font-size:10px;color:#5c607a;text-align:right;margin-top:2px;font-family:JetBrains Mono,monospace;">Urgency {urgency}/10</div>
                    </div>
                </div>
                <div class="watchlist-bar-track">
                    <div class="watchlist-bar-fill" style="width:{cp}%;background:{bar_color};"></div>
                </div>
                <div class="watchlist-tags">
                    {tag_pill(tag)}
                    <span class="tag-pill" style="color:#9099b5;border-color:rgba(144,153,181,0.2);background:rgba(144,153,181,0.05);">{root}</span>
                </div>
                <div class="watchlist-feedback">"{str(feedback_text)[:200]}"</div>
                <div class="watchlist-action">→ {action}</div>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 4: BUG MATRIX ────────────────────────────────────────────────────────
with tabs[3]:
    bugs_df = enriched[enriched["AI Tag"] == "Bug"].sort_values("Urgency Score", ascending=False)

    if bugs_df.empty:
        st.markdown("<div class='empty-state'>No bugs flagged in this batch.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:13px;color:#5c607a;margin-bottom:16px;font-family:JetBrains Mono,monospace;'>{len(bugs_df)} bugs detected · sorted by urgency</div>", unsafe_allow_html=True)

        for _, row in bugs_df.iterrows():
            urgency = row.get("Urgency Score", 5)
            impact  = row.get("Impact","Medium")
            if urgency >= 8:
                badge_bg, badge_color = "rgba(244,63,94,0.12)", "#f43f5e"
                badge_text = f"CRITICAL · U{urgency}"
            elif urgency >= 6:
                badge_bg, badge_color = "rgba(251,146,60,0.12)", "#fb923c"
                badge_text = f"HIGH · U{urgency}"
            else:
                badge_bg, badge_color = "rgba(92,96,122,0.12)", "#5c607a"
                badge_text = f"MEDIUM · U{urgency}"

            name    = row.get("Name","")
            persona = row.get("Persona Type","")
            age     = row.get("Age","")
            root    = row.get("Root Cause","")
            summary = row.get("AI Summary") or row.get("Raw Feedback","")
            action  = row.get("PM Action","")
            friction_flags = []
            for fkey, flabel in [("Friction: Tech Bug","Tech Bug"),("Friction: UX","UX"),
                                  ("Friction: Content","Content"),("Friction: Paywall","Paywall")]:
                if row.get(fkey,"") and str(row.get(fkey,"")).strip() not in ["","nan"]:
                    friction_flags.append(flabel)
            friction_str = " · ".join(friction_flags) if friction_flags else root

            st.markdown(f"""
            <div class="bug-row">
                <div>
                    <div class="bug-urgency-badge"
                         style="background:{badge_bg};color:{badge_color};">{badge_text}</div>
                    <div style="font-size:10px;color:#5c607a;font-family:JetBrains Mono,monospace;
                                margin-top:6px;text-align:center;">{impact}</div>
                </div>
                <div class="bug-content">
                    <div class="bug-name">{name} <span style="font-weight:400;color:#5c607a;">— {persona} · {age}</span></div>
                    <div class="bug-root">{friction_str}</div>
                    <div class="bug-summary">"{str(summary)[:200]}"</div>
                    <div class="bug-action">→ {action}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 5: FEATURE MAP ───────────────────────────────────────────────────────
with tabs[4]:
    feat_data = safe_json(R["feat_raw"])

    if feat_data and isinstance(feat_data, list) and len(feat_data) > 0:
        st.markdown(f"<div style='font-size:13px;color:#5c607a;margin-bottom:16px;font-family:JetBrains Mono,monospace;'>{len(feat_data)} feature opportunities identified by AI</div>", unsafe_allow_html=True)

        for feat in feat_data:
            priority = feat.get("priority","Medium")
            effort   = feat.get("effort","Medium")
            qw       = feat.get("quick_win", False)
            p_color  = {"Critical":"#f43f5e","High":"#fb923c","Medium":"#38bdf8","Low":"#34d399"}.get(priority,"#5c607a")
            e_color  = {"Low":"#34d399","Medium":"#fb923c","High":"#f43f5e"}.get(effort,"#5c607a")

            st.markdown(f"""
            <div class="feat-row">
                <div class="feat-header">
                    <div class="feat-name">{feat.get('feature','')}</div>
                    <div style="display:flex;gap:8px;align-items:center;">
                        {"<span class='tag-pill tag-praise' style='font-size:10px;'>⚡ Quick Win</span>" if qw else ""}
                        <span class="feat-priority" style="background:{p_color}20;color:{p_color};border:1px solid {p_color}40;">{priority} Priority</span>
                        <span class="feat-priority" style="background:{e_color}20;color:{e_color};border:1px solid {e_color}40;">{effort} Effort</span>
                    </div>
                </div>
                <div style="font-size:12px;color:#5c607a;font-family:JetBrains Mono,monospace;margin-bottom:6px;">{feat.get('estimated_demand','')}</div>
                <div class="feat-why">{feat.get('why_it_matters','')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fallback from raw data
        if "Feature Complained About" in enriched.columns:
            complaints = enriched["Feature Complained About"].value_counts()
            for feat, cnt in complaints.items():
                if feat and str(feat).strip().lower() not in ["none","nan",""]:
                    st.markdown(f"""
                    <div class="feat-row">
                        <div class="feat-header">
                            <div class="feat-name">{feat}</div>
                            <div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#5c607a;">{cnt} mentions</div>
                        </div>
                    </div>""", unsafe_allow_html=True)


# ── TAB 6: PRAISE ────────────────────────────────────────────────────────────
with tabs[5]:
    praise_df = enriched[enriched["AI Tag"] == "Praise"].sort_values("Sentiment Score", ascending=False)

    if praise_df.empty:
        st.markdown("<div class='empty-state'>No praise entries in this filtered batch.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:var(--surface);border:1px solid rgba(52,211,153,0.15);border-radius:12px;
                    padding:16px 20px;margin-bottom:20px;font-size:13px;color:#9099b5;line-height:1.65;">
            <strong style="color:#34d399;">What's working — don't break it.</strong>
            These are your retention anchors. Reference them before every feature change.
        </div>
        """, unsafe_allow_html=True)

        pc1, pc2 = st.columns(2)
        cols = [pc1, pc2]
        for i, (_, row) in enumerate(praise_df.iterrows()):
            name    = row.get("Name","")
            persona = row.get("Persona Type","")
            age     = row.get("Age","")
            score   = row.get("Sentiment Score",0)
            summary = row.get("AI Summary") or row.get("Raw Feedback","")
            liked   = row.get("Most Liked Feature","")
            insight = row.get("Persona Insight","")

            with cols[i % 2]:
                st.markdown(f"""
                <div class="praise-row">
                    <div class="praise-meta">{name} · {persona} · {age} · Sentiment {score}/10
                        {"· " + liked if liked and str(liked).lower() not in ["none","nan",""] else ""}
                    </div>
                    <div class="praise-text">"{str(summary)[:220]}"</div>
                    {f'<div style="font-size:11px;color:#34d399;margin-top:8px;font-style:normal;">💡 {insight}</div>' if insight and str(insight).lower() not in ["insufficient data","nan",""] else ""}
                </div>
                """, unsafe_allow_html=True)


# ── TAB 7: PERSONAS ──────────────────────────────────────────────────────────
with tabs[6]:
    persona_lines = [l.strip() for l in R["persona_insights"].split("\n") if l.strip()]

    st.markdown("<div style='background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px 28px;margin-bottom:24px;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px;font-family:JetBrains Mono,monospace;color:#6e56ff;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:16px;'>AI Persona Analysis</div>", unsafe_allow_html=True)
    for line in persona_lines:
        clean = re.sub(r"\*\*(.*?)\*\*", r"<b style='color:#6e56ff;'>\1</b>", line).lstrip("-•1234567890. ").strip()
        if clean:
            st.markdown(f"""
            <div class="exec-bullet">
                <div class="exec-bullet-dot"></div>
                <div class="exec-bullet-text">{clean}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Persona breakdown chart
    if "Persona Type" in enriched.columns:
        pa1, pa2 = st.columns(2)
        with pa1:
            p_churn = enriched.groupby("Persona Type")["Churn %"].mean().sort_values().reset_index()
            p_churn.columns = ["Persona","Avg Churn %"]
            fig_pc = px.bar(p_churn, x="Avg Churn %", y="Persona", orientation="h",
                            color="Avg Churn %", color_continuous_scale=["#34d399","#fb923c","#f43f5e"])
            fig_pc.update_layout(**PLOT_LAYOUT, title="Avg Churn Risk by Persona",
                                  xaxis=dict(**GRID), yaxis=dict(**GRID), coloraxis_showscale=False)
            st.plotly_chart(fig_pc, use_container_width=True)

        with pa2:
            p_sent = enriched.groupby("Persona Type")["Sentiment Score"].mean().sort_values(ascending=False).reset_index()
            p_sent.columns = ["Persona","Avg Sentiment"]
            fig_ps = px.bar(p_sent, x="Persona", y="Avg Sentiment",
                            color="Avg Sentiment", color_continuous_scale=["#f43f5e","#fb923c","#34d399"])
            fig_ps.update_layout(**PLOT_LAYOUT, title="Avg Sentiment by Persona",
                                  xaxis=dict(**GRID, tickangle=-30),
                                  yaxis=dict(**GRID), coloraxis_showscale=False)
            st.plotly_chart(fig_ps, use_container_width=True)


# ── TAB 8: COMPETITORS ───────────────────────────────────────────────────────
with tabs[7]:
    comp_text = R.get("comp_insights","")
    if comp_text:
        comp_lines = [l.strip() for l in comp_text.split("\n") if l.strip()]
        st.markdown("<div style='background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px 28px;margin-bottom:24px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:11px;font-family:JetBrains Mono,monospace;color:#6e56ff;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:16px;'>Competitive Intelligence · AI Generated</div>", unsafe_allow_html=True)
        for line in comp_lines:
            clean = re.sub(r"\*\*(.*?)\*\*", r"<b style='color:#38bdf8;'>\1</b>", line).lstrip("-•1234567890. ").strip()
            if clean:
                st.markdown(f"""
                <div class="exec-bullet">
                    <div class="exec-bullet-dot" style="background:#38bdf8;"></div>
                    <div class="exec-bullet-text">{clean}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Competitor mention chart
    if "Competitor Mentioned" in enriched.columns:
        comp_df = enriched["Competitor Mentioned"].dropna()
        comp_df = comp_df[comp_df.str.strip().str.lower().isin(["","nan","none"]) == False]
        if len(comp_df) > 0:
            comp_counts = comp_df.value_counts().reset_index()
            comp_counts.columns = ["Competitor","Mentions"]
            fig_comp = px.bar(comp_counts, x="Competitor", y="Mentions",
                              color="Mentions", color_continuous_scale=["#1a1a2e","#38bdf8"])
            fig_comp.update_layout(**PLOT_LAYOUT, title="Competitor Mentions",
                                    xaxis=dict(**GRID), yaxis=dict(**GRID), coloraxis_showscale=False)
            st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.markdown("<div class='empty-state'>No competitor data found in this batch.</div>", unsafe_allow_html=True)


# ── TAB 9: FULL TABLE ────────────────────────────────────────────────────────
with tabs[8]:
    show_cols = [c for c in [
        "Name","Persona Type","Age","AI Tag","Sentiment Score","Urgency Score",
        "Churn %","Impact","Root Cause","Retention Signal","AI Summary","PM Action"
    ] if c in enriched.columns]

    # Search
    search = st.text_input("Search feedback", placeholder="Search by name, summary, tag…", label_visibility="collapsed")
    disp = enriched[show_cols]
    if search:
        mask = disp.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
        disp = disp[mask]

    st.markdown(f"<div style='font-size:11px;color:#5c607a;font-family:JetBrains Mono,monospace;margin-bottom:8px;'>{len(disp)} rows</div>", unsafe_allow_html=True)
    st.dataframe(disp, use_container_width=True, height=480)


# ── TAB 10: EXPORT ───────────────────────────────────────────────────────────
with tabs[9]:
    st.markdown("<div style='font-size:14px;color:#9099b5;margin-bottom:20px;'>Download your enriched data and PM reports.</div>", unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)

    with e1:
        csv_bytes = enriched.to_csv(index=False).encode("utf-8")
        st.download_button("⬇  Enriched CSV", csv_bytes, "postmortem_enriched.csv", "text/csv", use_container_width=True)
        st.caption("Full dataset with all AI tags, scores, and PM actions")

    with e2:
        churn_only = enriched[enriched["Churn %"] >= 55]
        churn_csv  = churn_only.to_csv(index=False).encode("utf-8")
        st.download_button("⬇  Churn Watchlist CSV", churn_csv, "churn_watchlist.csv", "text/csv", use_container_width=True)
        st.caption(f"{len(churn_only)} high-risk users exported")

    with e3:
        bugs_only = enriched[enriched["AI Tag"] == "Bug"]
        bugs_csv  = bugs_only.to_csv(index=False).encode("utf-8")
        st.download_button("⬇  Bug Report CSV", bugs_csv, "bugs_report.csv", "text/csv", use_container_width=True)
        st.caption(f"{len(bugs_only)} bug entries exported")

    st.markdown("---")

    # Markdown PM report
    report = [
        "# User Feedback Postmortem — EnglishBhashi\n\n",
        f"**Entries Analysed:** {total_n}  \n",
        f"**Avg Sentiment:** {avg_sent}/10  \n",
        f"**Avg Churn Probability:** {avg_churn}%  \n",
        f"**High-Risk Users:** {hi_churn}  \n",
        f"**Critical Issues:** {critical}  \n\n",
        "---\n\n## Executive Brief\n\n",
        R["exec_sum"] + "\n\n",
        "---\n\n## Churn Watchlist\n\n",
    ]
    for _, row in enriched[enriched["Churn %"] >= 55].sort_values("Churn %", ascending=False).head(10).iterrows():
        report.append(f"- **{row.get('Name','')}** ({row.get('Churn %',0):.0f}%): {row.get('AI Summary','')}\n")

    report.append("\n---\n\n## Persona Insights\n\n")
    report.append(R["persona_insights"] + "\n\n")

    if R.get("comp_insights"):
        report.append("---\n\n## Competitive Intelligence\n\n")
        report.append(R["comp_insights"] + "\n\n")

    report_md = "".join(report)
    st.download_button("⬇  Full PM Report (Markdown)", report_md.encode("utf-8"),
                       "postmortem_report.md", "text/markdown", use_container_width=False)
    st.caption("Complete postmortem — paste into Notion or send to founders")