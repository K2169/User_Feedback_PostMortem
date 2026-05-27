print("FEEDBACK POSTMORTEM v2 RUNNING")
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
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="Postmortem · Feedback Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  — Refined dark editorial with Neue Montreal feel
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

:root {
  --bg:        #080910;
  --bg2:       #0d0f18;
  --surface:   #111320;
  --surface2:  #181b2a;
  --surface3:  #1e2133;
  --border:    rgba(255,255,255,0.055);
  --border2:   rgba(255,255,255,0.10);
  --text:      #eceef5;
  --text2:     #9da3be;
  --muted:     #4e5370;
  --accent:    #7b5ea7;
  --accent2:   #a78bfa;
  --green:     #2dd4a0;
  --orange:    #f97316;
  --red:       #f43f5e;
  --blue:      #38bdf8;
  --yellow:    #fbbf24;
  --r:         14px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 99px; }

/* streamlit chrome removal */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 2.5rem 5rem !important; max-width: 1380px; }
[data-testid="stDecoration"] { display: none; }

/* ── SIDEBAR ─────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem 2rem !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] label { font-size: 11px !important; color: var(--muted) !important; font-family: 'IBM Plex Mono', monospace !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; }
[data-testid="stSidebar"] p { font-size: 12px !important; color: var(--text2) !important; }

/* ── INPUTS ──────────────────────────────────────── */
[data-testid="stFileUploader"] {
  background: var(--surface) !important;
  border: 1px dashed rgba(123,94,167,0.45) !important;
  border-radius: 10px !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: rgba(167,139,250,0.7) !important;
}
.stTextInput input, .stSelectbox select {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 13px !important;
}
.stTextInput input:focus { border-color: var(--accent2) !important; }
.stMultiSelect [data-baseweb="select"] {
  background: var(--surface) !important;
  border-color: var(--border2) !important;
}

/* ── BUTTONS ─────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, #7b5ea7 0%, #a78bfa 100%) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 0.65rem 2rem !important;
  letter-spacing: 0.01em !important;
  box-shadow: 0 4px 24px rgba(123,94,167,0.35) !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 32px rgba(123,94,167,0.5) !important;
}

[data-testid="stDownloadButton"] > button {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 500 !important;
  box-shadow: none !important;
}
[data-testid="stDownloadButton"] > button:hover {
  border-color: var(--accent2) !important;
  transform: translateY(-1px) !important;
}

/* ── TABS ────────────────────────────────────────── */
[data-testid="stTabs"] {
  border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTabs"] [role="tablist"] {
  gap: 0 !important;
  background: transparent !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: 'Outfit', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--muted) !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  padding: 10px 18px !important;
  background: transparent !important;
  transition: all 0.15s !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--text2) !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--text) !important;
  border-bottom-color: var(--accent2) !important;
  font-weight: 600 !important;
}

/* ── PROGRESS ────────────────────────────────────── */
.stProgress > div > div {
  background: linear-gradient(90deg, #7b5ea7, #a78bfa) !important;
  border-radius: 99px !important;
}
.stProgress > div {
  background: var(--surface2) !important;
  border-radius: 99px !important;
}

/* ── DATAFRAME ───────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] * {
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 11.5px !important;
}

/* ── SLIDER ──────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: var(--accent2) !important;
}

/* ── ALERTS ──────────────────────────────────────── */
.stSuccess {
  background: rgba(45,212,160,0.08) !important;
  border: 1px solid rgba(45,212,160,0.25) !important;
  border-radius: 10px !important;
  color: var(--green) !important;
}

/* ─────────────────────────────────────────────────
   CUSTOM COMPONENTS
───────────────────────────────────────────────── */

/* LANDING HERO */
.hero {
  min-height: 72vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 24px 60px;
  position: relative;
}
.hero-glow {
  position: absolute;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 300px;
  background: radial-gradient(ellipse at center, rgba(123,94,167,0.18) 0%, transparent 70%);
  pointer-events: none;
}
.hero-eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: var(--accent2);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-bottom: 20px;
  opacity: 0.9;
}
.hero-title {
  font-size: clamp(38px, 6vw, 68px);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: var(--text);
  margin-bottom: 20px;
}
.hero-title em {
  font-style: normal;
  background: linear-gradient(135deg, #a78bfa 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 17px;
  color: var(--text2);
  max-width: 540px;
  line-height: 1.7;
  margin: 0 auto 40px;
  font-weight: 400;
}
.hero-steps {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 48px;
}
.hero-step {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 10px;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text2);
  font-weight: 500;
  min-width: 180px;
}
.hero-step-num {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: var(--accent2);
  background: rgba(167,139,250,0.1);
  border: 1px solid rgba(167,139,250,0.2);
  border-radius: 6px;
  padding: 2px 7px;
  flex-shrink: 0;
}
.hero-outputs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 48px;
}
.hero-output-pill {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  padding: 5px 12px;
  border-radius: 99px;
  border: 1px solid;
}

/* PAGE HEADER (post-upload) */
.pg-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 28px 0 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}
.pg-header-left {}
.pg-header-eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--accent2);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.pg-header-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.pg-header-sub {
  font-size: 13px;
  color: var(--text2);
  margin-top: 4px;
}
.pg-header-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.pg-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  padding: 4px 12px;
  border-radius: 99px;
  border: 1px solid var(--border2);
  color: var(--text2);
  background: var(--surface);
}

/* DIVIDER */
.div-label {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 32px 0 20px;
}
.div-label-line { flex: 1; height: 1px; background: var(--border); }
.div-label-text {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  white-space: nowrap;
}

/* KPI CARDS */
.kpi-row { display: grid; grid-template-columns: repeat(5,1fr); gap: 12px; margin-bottom: 28px; }
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 18px 16px 16px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  opacity: 0;
  transition: opacity 0.2s;
}
.kpi-card:hover { border-color: var(--border2); }
.kpi-card:hover::before { opacity: 1; }
.kpi-val {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--text);
}
.kpi-lbl {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  margin-top: 7px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.kpi-sub {
  font-size: 11px;
  margin-top: 5px;
  font-weight: 500;
  color: var(--text2);
}

/* EXEC BRIEF */
.brief-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 28px 32px;
  margin-bottom: 24px;
}
.brief-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--accent2);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.brief-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.brief-bullet {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  align-items: flex-start;
}
.brief-bullet:last-child { border-bottom: none; padding-bottom: 0; }
.brief-bullet-num {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--accent2);
  background: rgba(167,139,250,0.1);
  border: 1px solid rgba(167,139,250,0.2);
  border-radius: 6px;
  padding: 3px 8px;
  flex-shrink: 0;
  margin-top: 2px;
}
.brief-bullet-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
}
.brief-bullet-text b { color: var(--accent2); font-weight: 600; }

/* TAG SUMMARY ROW */
.tag-summary {
  display: grid;
  grid-template-columns: repeat(5,1fr);
  gap: 10px;
  margin-top: 20px;
}
.tag-sum-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 12px;
  text-align: center;
  transition: border-color 0.2s;
}
.tag-sum-card:hover { border-color: var(--border2); }
.tag-sum-num {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1;
}
.tag-sum-lbl {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  margin-top: 8px;
  letter-spacing: 0.06em;
}

/* PILLS */
.pill {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  padding: 3px 9px;
  border-radius: 99px;
  border: 1px solid;
  display: inline-block;
  font-weight: 500;
}
.pill-bug     { color: #f43f5e; border-color: rgba(244,63,94,0.3);   background: rgba(244,63,94,0.07); }
.pill-churn   { color: #f97316; border-color: rgba(249,115,22,0.3);  background: rgba(249,115,22,0.07); }
.pill-praise  { color: #2dd4a0; border-color: rgba(45,212,160,0.3);  background: rgba(45,212,160,0.07); }
.pill-feature { color: #38bdf8; border-color: rgba(56,189,248,0.3);  background: rgba(56,189,248,0.07); }
.pill-neutral { color: #4e5370; border-color: rgba(78,83,112,0.4);   background: rgba(78,83,112,0.06); }
.pill-green   { color: #2dd4a0; border-color: rgba(45,212,160,0.3);  background: rgba(45,212,160,0.07); }
.pill-blue    { color: #38bdf8; border-color: rgba(56,189,248,0.3);  background: rgba(56,189,248,0.07); }
.pill-orange  { color: #f97316; border-color: rgba(249,115,22,0.3);  background: rgba(249,115,22,0.07); }
.pill-red     { color: #f43f5e; border-color: rgba(244,63,94,0.3);   background: rgba(244,63,94,0.07); }

/* WATCHLIST CARDS */
.wl-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 20px 22px;
  margin-bottom: 10px;
  transition: border-color 0.2s;
}
.wl-card:hover { border-color: var(--border2); }
.wl-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.wl-name { font-size: 15px; font-weight: 600; color: var(--text); }
.wl-meta { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--muted); margin-top: 3px; }
.wl-risk-num { font-family: 'IBM Plex Mono', monospace; font-size: 15px; font-weight: 700; }
.wl-urg { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--muted); margin-top: 2px; text-align: right; }
.wl-bar-bg { height: 3px; background: var(--surface3); border-radius: 99px; margin: 10px 0; }
.wl-bar-fg { height: 3px; border-radius: 99px; }
.wl-pills { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.wl-quote { font-family: 'Lora', serif; font-style: italic; font-size: 13px; color: var(--text2); line-height: 1.65; padding: 10px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin: 8px 0; }
.wl-action { font-size: 12px; color: var(--accent2); font-weight: 600; margin-top: 8px; }
.wl-action::before { content: '→ '; }

/* BUG CARDS */
.bug-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 18px 20px;
  margin-bottom: 8px;
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 18px;
  align-items: start;
  transition: border-color 0.2s;
}
.bug-card:hover { border-color: var(--border2); }
.bug-badge-col { display: flex; flex-direction: column; align-items: center; gap: 8px; padding-top: 2px; }
.bug-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 7px;
  text-align: center;
  width: 100%;
  letter-spacing: 0.05em;
}
.bug-impact { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: var(--muted); text-align: center; letter-spacing: 0.06em; }
.bug-name { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.bug-persona { font-size: 12px; color: var(--muted); font-family: 'IBM Plex Mono', monospace; margin-bottom: 6px; }
.bug-quote { font-family: 'Lora', serif; font-style: italic; font-size: 13px; color: var(--text2); line-height: 1.6; margin-bottom: 8px; }
.bug-action { font-size: 12px; color: var(--accent2); font-weight: 600; }
.bug-action::before { content: '→ '; }

/* FEATURE CARDS */
.feat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 20px 22px;
  margin-bottom: 8px;
  transition: border-color 0.2s;
}
.feat-card:hover { border-color: var(--border2); }
.feat-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }
.feat-name { font-size: 15px; font-weight: 600; color: var(--text); }
.feat-badges { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.feat-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 99px;
}
.feat-demand { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--muted); margin-bottom: 8px; }
.feat-why { font-size: 13px; color: var(--text2); line-height: 1.65; }

/* PRAISE CARDS */
.praise-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--green);
  border-radius: var(--r);
  padding: 18px 20px;
  margin-bottom: 8px;
}
.praise-meta { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--green); margin-bottom: 8px; letter-spacing: 0.04em; }
.praise-quote { font-family: 'Lora', serif; font-style: italic; font-size: 14px; color: var(--text2); line-height: 1.7; margin-bottom: 8px; }
.praise-insight { font-size: 12px; color: var(--green); margin-top: 8px; font-weight: 500; }
.praise-insight::before { content: '💡 '; }

/* INSIGHT CARD (persona / competitor) */
.insight-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 28px 32px;
  margin-bottom: 20px;
}
.insight-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--accent2);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.insight-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }
.insight-bullet {
  display: flex;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  align-items: flex-start;
}
.insight-bullet:last-child { border-bottom: none; padding-bottom: 0; }
.insight-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 8px;
}
.insight-text { font-size: 14px; line-height: 1.7; color: var(--text); }
.insight-text b { font-weight: 600; }

/* EMPTY STATE */
.empty {
  text-align: center;
  padding: 64px 24px;
  color: var(--muted);
}
.empty-icon { font-size: 36px; margin-bottom: 12px; }
.empty-text { font-size: 14px; color: var(--text2); }

/* CHART WRAPPER */
.chart-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 8px 4px 4px;
  margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Outfit", color="#9da3be", size=12),
    title_font=dict(family="Outfit", color="#eceef5", size=13, weight=600),
    legend=dict(font=dict(color="#9da3be", size=11), bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=44, b=20, l=16, r=16),
)
GRID = dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.04)")
TAG_COLORS = {
    "Bug":             "#f43f5e",
    "Churn Risk":      "#f97316",
    "Feature Request": "#38bdf8",
    "Praise":          "#2dd4a0",
    "Neutral":         "#4e5370",
}
PILL_CSS = {
    "Bug": "pill-bug", "Churn Risk": "pill-churn",
    "Praise": "pill-praise", "Feature Request": "pill-feature", "Neutral": "pill-neutral"
}

def safe_json(text):
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

def ai(prompt, temp=0.3, retries=3):
    for attempt in range(retries):
        try:
            r = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=temp, max_tokens=2048
            )
            return r.choices[0].message.content
        except Exception as e:
            time.sleep(1.5)
    return "AI generation failed."

def divider(label):
    st.markdown(f"""
    <div class="div-label">
        <div class="div-label-line"></div>
        <div class="div-label-text">{label}</div>
        <div class="div-label-line"></div>
    </div>""", unsafe_allow_html=True)

def pill(tag):
    css = PILL_CSS.get(tag, "pill-neutral")
    return f'<span class="pill {css}">{tag}</span>'

def chart_wrap(fig):
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AI FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def tag_row(row):
    prompt = f"""You are a senior product analyst for a mobile app startup.

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
  "urgency_score": <1-10>,
  "churn_probability": <0-100>,
  "root_cause": "UX" | "Performance" | "Content" | "Pricing" | "Engagement" | "AI Feature" | "Support" | "Habit Loop",
  "impact": "Critical" | "High" | "Medium" | "Low",
  "pm_action": "<one crisp actionable sentence>",
  "summary": "<one plain English sentence summarising this feedback>",
  "persona_insight": "<one sentence about what this tells us about this persona>",
  "retention_signal": "positive" | "negative" | "neutral"
}}"""
    try:
        result = safe_json(ai(prompt))
        if isinstance(result, dict):
            return result
    except Exception:
        pass
    return {
        "tag": "Neutral", "sentiment_score": 5, "urgency_score": 5,
        "churn_probability": 30, "root_cause": "Content", "impact": "Medium",
        "pm_action": "Review manually",
        "summary": str(row.get("Raw Feedback",""))[:100],
        "persona_insight": "Insufficient data",
        "retention_signal": "neutral"
    }

def gen_exec_summary(df, tagged):
    churn_ct  = sum(1 for t in tagged if t.get("tag") == "Churn Risk")
    bug_ct    = sum(1 for t in tagged if t.get("tag") == "Bug")
    praise_ct = sum(1 for t in tagged if t.get("tag") == "Praise")
    feat_ct   = sum(1 for t in tagged if t.get("tag") == "Feature Request")
    avg_sent  = round(sum(t.get("sentiment_score",5) for t in tagged)/max(len(tagged),1),1)
    avg_churn = round(sum(t.get("churn_probability",30) for t in tagged)/max(len(tagged),1))
    critical  = sum(1 for t in tagged if t.get("impact") == "Critical")
    top_dropoff   = df["Drop-off Point"].value_counts().head(2).to_dict() if "Drop-off Point" in df.columns else {}
    top_complaint = df["Feature Complained About"].value_counts().head(3).to_dict() if "Feature Complained About" in df.columns else {}
    competitors   = df["Competitor Mentioned"].value_counts().to_dict() if "Competitor Mentioned" in df.columns else {}
    sample_fb     = df["Raw Feedback"].dropna().sample(min(10,len(df))).tolist()
    prompt = f"""You are a senior PM writing an executive postmortem for a startup founding team.

Data:
- Total entries analysed: {len(tagged)}
- Bugs: {bug_ct} | Churn Risk: {churn_ct} | Praise: {praise_ct} | Feature Requests: {feat_ct}
- Avg Sentiment: {avg_sent}/10 | Avg Churn Probability: {avg_churn}% | Critical Issues: {critical}
- Top drop-off points: {top_dropoff}
- Top complained features: {top_complaint}
- Competitors mentioned: {competitors}
- Sample raw feedback: {sample_fb[:8]}

Write exactly 5 executive bullets. Rules:
- Each starts with **Label:** in bold (e.g. **Critical Bug:**, **Retention Risk:**, **AI Experience:**, **Growth Signal:**, **Immediate Action:**)
- Specific, data-backed, and actionable — not vague
- Max 2 sentences each
- For a CPO/founder who has 60 seconds to read this

Return plain text, 5 bullets only. No headers, no preamble."""
    try:
        return ai(prompt).strip()
    except Exception as e:
        return f"Summary unavailable: {e}"

def gen_features(df):
    feedbacks = df["Raw Feedback"].dropna().tolist()
    prompt = f"""You are a PM analysing feature requests from user feedback for a mobile app.

Analyse these {min(len(feedbacks),40)} feedback entries and surface the top 6 most impactful improvements requested.

For each, return:
- feature: short descriptive name
- estimated_demand: "~X% of users" or "~N users"  
- why_it_matters: one specific sentence tied to the actual user base and pain
- priority: "Critical" | "High" | "Medium" | "Low"
- effort: "Low" | "Medium" | "High"
- quick_win: true | false (shippable in under 2 weeks?)

Return ONLY a JSON array. No markdown, no preamble.

Feedbacks:
{chr(10).join(f'- {f}' for f in feedbacks[:40])}"""
    try:
        return ai(prompt).strip()
    except Exception:
        return "[]"

def gen_personas(df, tagged):
    sample = []
    for i, (_, row) in enumerate(df.head(30).iterrows()):
        t = tagged[i] if i < len(tagged) else {}
        sample.append({
            "persona": row.get("Persona Type",""),
            "age": row.get("Age",""),
            "sentiment": t.get("sentiment_score",5),
            "churn": t.get("churn_probability",30),
            "tag": t.get("tag",""),
            "root_cause": t.get("root_cause",""),
        })
    prompt = f"""You are a PM doing persona segmentation analysis.

Enriched data: {json.dumps(sample)}

Write a PM-ready persona brief:
1. Which persona has the highest churn risk and the specific reason
2. Which persona is most engaged and the primary driver
3. Which persona needs the most product attention right now and why
4. One cross-persona pattern that surprised you
5. One persona-specific product change that would most move retention

Max 5 bullets. Be specific — use actual persona names. 2 sentences max per bullet. Plain text only."""
    try:
        return ai(prompt).strip()
    except Exception:
        return "Persona analysis unavailable."

def gen_competitors(df):
    if "Competitor Mentioned" not in df.columns:
        return ""
    comp_data = []
    for _, row in df.iterrows():
        comp = str(row.get("Competitor Mentioned","")).strip()
        if comp and comp.lower() not in ["nan","none",""]:
            comp_data.append({
                "competitor": comp,
                "feedback": str(row.get("Raw Feedback",""))[:200],
                "sentiment": row.get("Sentiment","")
            })
    if not comp_data:
        return ""
    prompt = f"""You are a PM building a competitive brief from user feedback.

Users mentioned these competitors: {json.dumps(comp_data[:20])}

Write a tight competitive brief:
1. Which competitor is most mentioned and what users specifically prefer about it
2. Where this product clearly wins (from user feedback)
3. One immediate product change that would recapture users from the top competitor
4. One long-term moat to build against all mentioned competitors

Max 4 bullets. 1-2 sentences each. Plain text only."""
    try:
        return ai(prompt).strip()
    except Exception:
        return ""

# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# MOCK DATA — bundled CSV sitting next to app.py
# ─────────────────────────────────────────────────────────────────────────────
MOCK_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "englishbhashi_feedback_100.csv")

@st.cache_data
def load_mock_data():
    if os.path.exists(MOCK_CSV_PATH):
        df = pd.read_csv(MOCK_CSV_PATH)
        df.columns = df.columns.str.strip()
        return df
    return None

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — always rendered first
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#7b5ea7;
                    letter-spacing:0.14em;text-transform:uppercase;margin-bottom:10px;">
            // AI PRODUCT TOOL
        </div>
        <div style="font-size:18px;font-weight:700;color:#eceef5;
                    line-height:1.25;letter-spacing:-0.01em;">
            Feedback<br>Postmortem
        </div>
        <div style="font-size:11px;color:#4e5370;margin-top:6px;">
            Upload · Enrich · Decide
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Data source ──
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
        color:#4e5370;letter-spacing:0.08em;text-transform:uppercase;
        margin-bottom:10px;">Data Source</div>""", unsafe_allow_html=True)

    data_mode = st.radio(
        "datasrc",
        options=["📁  Upload my CSV", "🧪  Try with mock data"],
        label_visibility="collapsed"
    )

    uploaded  = None
    use_mock  = False

    if data_mode == "📁  Upload my CSV":
        uploaded = st.file_uploader(
            "upload_csv", type=["csv"],
            label_visibility="collapsed",
            help="Upload a feedback CSV — only 'Raw Feedback' column is required"
        )
        if uploaded is None:
            st.markdown("""<div style="font-size:11px;color:#4e5370;
                margin-top:6px;line-height:1.65;">Drop any feedback CSV here.<br>
                Only <strong style="color:#9da3be;">Raw Feedback</strong> column
                is required.</div>""", unsafe_allow_html=True)
    else:
        use_mock = True
        st.markdown("""
        <div style="background:rgba(167,139,250,0.08);
                    border:1px solid rgba(167,139,250,0.25);
                    border-radius:8px;padding:12px 14px;margin-top:4px;">
            <div style="font-size:12px;color:#a78bfa;font-weight:600;margin-bottom:5px;">
                ✓ Mock dataset ready
            </div>
            <div style="font-size:11px;color:#4e5370;line-height:1.65;">
                100 realistic entries · Indian EdTech app ·
                bugs, churn signals, feature requests &amp; praise.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="font-size:10px;color:#4e5370;font-family:'IBM Plex Mono',
        monospace;margin-bottom:10px;letter-spacing:0.08em;
        text-transform:uppercase;">Filters</div>""", unsafe_allow_html=True)

    f_sentiment = st.multiselect("Sentiment",  ["Positive","Negative","Neutral","Mixed"])
    f_persona   = st.multiselect("Persona",    ["Student","Working Professional",
                                                "Homemaker","Job Seeker","Business","Other"])
    f_category  = st.multiselect("Category",   ["Content Quality","Technical Bug",
                                                "Engagement/Retention","Subscription/Paywall"])
    f_dropoff   = st.multiselect("Drop-off",   ["No Habit loop","No Motivation","Streak Break",
                                                "Pricing high","Content too hard","Technical Bug",
                                                "Less Engaging","UI/UX issues"])

    st.markdown("---")
    max_rows = st.slider("Rows to analyse", 10, 100, 25, 5,
                         help="More rows = richer insights but slower")
    st.markdown(f"""<div style="font-size:11px;color:#4e5370;margin-top:4px;">
        ~{max_rows*2}s at {max_rows} rows</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="font-size:10px;color:#4e5370;">
        Built by Krishnam Parasrampuria</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DECIDE: show landing OR proceed to dashboard
# ─────────────────────────────────────────────────────────────────────────────
show_landing = (not use_mock) and (uploaded is None)

if show_landing:
    # ── glow + eyebrow ──
    st.markdown("""
    <div style="position:relative;text-align:center;padding:56px 24px 0;">
        <div style="position:absolute;top:0;left:50%;transform:translateX(-50%);
                    width:640px;height:280px;
                    background:radial-gradient(ellipse at center,
                    rgba(123,94,167,0.18) 0%,transparent 70%);
                    pointer-events:none;z-index:0;"></div>
        <div style="position:relative;z-index:1;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                        color:#a78bfa;letter-spacing:0.16em;
                        text-transform:uppercase;margin-bottom:20px;">
                AI-Powered · Product Intelligence
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── headline ──
    st.markdown("""
    <div style="text-align:center;padding:0 24px;">
        <div style="font-size:clamp(36px,5.5vw,64px);font-weight:800;line-height:1.08;
                    letter-spacing:-0.03em;color:#eceef5;margin-bottom:20px;">
            Turn raw user feedback<br>
            into <span style="background:linear-gradient(135deg,#a78bfa 0%,#38bdf8 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;">PM decisions</span>
        </div>
        <div style="font-size:17px;color:#9da3be;max-width:520px;margin:0 auto 40px;
                    line-height:1.72;font-weight:400;">
            Upload any user feedback CSV. The AI enriches every entry — tagging, scoring,
            and surfacing the exact insights your product team needs to act fast.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3 steps ──
    st.markdown("""
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;
                margin-bottom:40px;padding:0 24px;">
        <div style="background:#111320;border:1px solid rgba(255,255,255,0.10);
                    border-radius:10px;padding:14px 20px;display:flex;align-items:center;
                    gap:10px;font-size:13px;color:#9da3be;font-weight:500;min-width:190px;">
            <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#a78bfa;
                background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);
                border-radius:6px;padding:2px 7px;flex-shrink:0;">01</span>
            Upload your feedback CSV
        </div>
        <div style="background:#111320;border:1px solid rgba(255,255,255,0.10);
                    border-radius:10px;padding:14px 20px;display:flex;align-items:center;
                    gap:10px;font-size:13px;color:#9da3be;font-weight:500;min-width:190px;">
            <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#a78bfa;
                background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);
                border-radius:6px;padding:2px 7px;flex-shrink:0;">02</span>
            AI enriches every entry
        </div>
        <div style="background:#111320;border:1px solid rgba(255,255,255,0.10);
                    border-radius:10px;padding:14px 20px;display:flex;align-items:center;
                    gap:10px;font-size:13px;color:#9da3be;font-weight:500;min-width:190px;">
            <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#a78bfa;
                background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);
                border-radius:6px;padding:2px 7px;flex-shrink:0;">03</span>
            Get PM-ready intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── what you'll get ──
    st.markdown("""
    <div style="text-align:center;margin-bottom:32px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4e5370;
                    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">
            What you'll get
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(244,63,94,0.3);
                background:rgba(244,63,94,0.07);color:#f43f5e;">🐛 Bug Severity Matrix</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(249,115,22,0.3);
                background:rgba(249,115,22,0.07);color:#f97316;">🚨 Churn Watchlist</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(56,189,248,0.3);
                background:rgba(56,189,248,0.07);color:#38bdf8;">💡 Feature Request Map</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(45,212,160,0.3);
                background:rgba(45,212,160,0.07);color:#2dd4a0;">✅ Praise &amp; Retention Anchors</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(167,139,250,0.3);
                background:rgba(167,139,250,0.07);color:#a78bfa;">📋 Executive PM Brief</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(251,191,36,0.3);
                background:rgba(251,191,36,0.07);color:#fbbf24;">👥 Persona Segmentation</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(157,163,190,0.25);
                background:rgba(157,163,190,0.06);color:#9da3be;">🏁 Competitive Intel</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 13px;
                border-radius:99px;border:1px solid rgba(157,163,190,0.25);
                background:rgba(157,163,190,0.06);color:#9da3be;">📊 Distribution Charts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── two CTA cards ──
    st.markdown("""
    <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;
                margin:0 auto 60px;max-width:500px;">
        <div style="flex:1;min-width:180px;background:#111320;
                    border:1px solid rgba(167,139,250,0.3);border-radius:12px;
                    padding:20px;text-align:center;">
            <div style="font-size:26px;margin-bottom:8px;">📁</div>
            <div style="font-size:13px;font-weight:600;color:#eceef5;margin-bottom:6px;">
                Upload your CSV
            </div>
            <div style="font-size:11px;color:#4e5370;line-height:1.6;">
                Switch to <strong style="color:#9da3be;">"Upload my CSV"</strong>
                in the sidebar
            </div>
        </div>
        <div style="flex:1;min-width:180px;background:#111320;
                    border:1px solid rgba(167,139,250,0.3);border-radius:12px;
                    padding:20px;text-align:center;">
            <div style="font-size:26px;margin-bottom:8px;">🧪</div>
            <div style="font-size:13px;font-weight:600;color:#eceef5;margin-bottom:6px;">
                Try mock data
            </div>
            <div style="font-size:11px;color:#4e5370;line-height:1.6;">
                Switch to <strong style="color:#9da3be;">"Try with mock data"</strong>
                in the sidebar
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# LOAD & FILTER DATA
# ─────────────────────────────────────────────────────────────────────────────
if use_mock:
    df_raw = load_mock_data()
    if df_raw is None:
        st.error("Mock dataset not found. Make sure `englishbhashi_feedback_100.csv` is in the same folder as `app.py`.")
        st.stop()
    _fname = "🧪 Mock Dataset · EdTech Feedback (100 entries)"
else:
    df_raw = pd.read_csv(uploaded)
    df_raw.columns = df_raw.columns.str.strip()
    _fname = uploaded.name.replace(".csv","").replace("_"," ").title()

df = df_raw.copy()

if f_dropoff and "Drop-off Point" in df.columns:
    df = df[df["Drop-off Point"].isin(f_dropoff)]

if df.empty:
    st.warning("No entries match your current filters — try adjusting the sidebar.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
fname = _fname
st.markdown(f"""
<div class="pg-header">
    <div class="pg-header-left">
        <div class="pg-header-eyebrow">// Feedback Postmortem</div>
        <div class="pg-header-title">{fname}</div>
        <div class="pg-header-sub">
            {len(df)} entries loaded · {len(df_raw) - len(df)} filtered out
        </div>
    </div>
    <div class="pg-header-meta">
        <span class="pg-badge">{len(df)} rows</span>
        <span class="pg-badge">AI ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RUN BUTTON
# ─────────────────────────────────────────────────────────────────────────────
rc1, rc2 = st.columns([2, 5])
with rc1:
    run = st.button("🔬  Run Postmortem Analysis")
with rc2:
    st.markdown(f"<div style='font-size:12px;color:#4e5370;padding-top:12px;font-family:IBM Plex Mono,monospace;'>→ will analyse {min(len(df),max_rows)} rows · ~{min(len(df),max_rows)*2}s</div>", unsafe_allow_html=True)

if "results" not in st.session_state:
    st.session_state.results = None

if run:
    total = min(len(df), max_rows)
    prog  = st.progress(0, "Initialising AI analysis…")
    tagged = []

    for i, (_, row) in enumerate(df.head(total).iterrows()):
        prog.progress((i+1)/total, f"Enriching {i+1} of {total} entries…")
        tagged.append(tag_row(row.to_dict()))
        time.sleep(0.08)

    prog.progress(1.0, "Writing executive brief…")
    exec_sum = gen_exec_summary(df.head(total), tagged)

    prog.progress(1.0, "Mapping feature requests…")
    feat_raw = gen_features(df.head(total))

    prog.progress(1.0, "Segmenting personas…")
    persona_text = gen_personas(df.head(total), tagged)

    prog.progress(1.0, "Competitive intelligence…")
    comp_text = gen_competitors(df.head(total))

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
        persona_text=persona_text, comp_text=comp_text
    )
    prog.empty()
    st.success(f"✓  Postmortem complete — {total} entries enriched across 4 AI modules")

if not st.session_state.results:
    st.markdown("""
    <div class="empty">
        <div class="empty-icon">🔬</div>
        <div class="empty-text">Click <strong>Run Postmortem Analysis</strong> above to start.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

R        = st.session_state.results
enriched = R["enriched"]
tagged   = R["tagged"]

# ─────────────────────────────────────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────────────────────────────────────
divider("Overview")

n        = len(enriched)
avg_s    = round(enriched["Sentiment Score"].mean(), 1)
avg_c    = round(enriched["Churn %"].mean())
hi_c     = int((enriched["Churn %"] >= 65).sum())
crit     = int((enriched["Impact"] == "Critical").sum())
urgent   = int((enriched["Urgency Score"] >= 8).sum())

sc  = "#2dd4a0" if avg_s >= 7 else "#f97316" if avg_s >= 5 else "#f43f5e"
cc  = "#f43f5e" if avg_c >= 50 else "#f97316" if avg_c >= 35 else "#2dd4a0"

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-val">{n}</div>
    <div class="kpi-lbl">Entries analysed</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:{sc}">{avg_s}/10</div>
    <div class="kpi-lbl">Avg sentiment</div>
    <div class="kpi-sub" style="color:{sc}">{"↑ Good signal" if avg_s>=7 else "↓ Needs attention"}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:{cc}">{avg_c}%</div>
    <div class="kpi-lbl">Avg churn risk</div>
    <div class="kpi-sub" style="color:{cc}">{"⚠ High" if avg_c>=50 else "Moderate risk"}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:#f43f5e">{hi_c}</div>
    <div class="kpi-lbl">High-risk users ≥65%</div>
    <div class="kpi-sub">{round(hi_c/n*100) if n else 0}% of batch</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-val" style="color:#f43f5e">{crit}</div>
    <div class="kpi-lbl">Critical issues</div>
    <div class="kpi-sub">{urgent} urgent actions</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📋 Brief",
    "📊 Charts",
    "🚨 Churn",
    "🐛 Bugs",
    "💡 Features",
    "✅ Praise",
    "👥 Personas",
    "🏁 Competitors",
    "🗂 Table",
    "⬇ Export",
])

# ── TAB 1 — EXECUTIVE BRIEF ──────────────────────────────────────────────────
with tabs[0]:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    lines = [l.strip() for l in R["exec_sum"].split("\n") if l.strip()]
    st.markdown("<div class='brief-card'><div class='brief-label'>PM Executive Brief · AI Generated</div>", unsafe_allow_html=True)
    for i, line in enumerate(lines, 1):
        clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line).lstrip("-•· ").strip()
        if clean:
            st.markdown(f"""
            <div class="brief-bullet">
                <div class="brief-bullet-num">0{i}</div>
                <div class="brief-bullet-text">{clean}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    tag_counts = enriched["AI Tag"].value_counts()
    items = [
        ("Bug",             "pill-bug",     "#f43f5e"),
        ("Churn Risk",      "pill-churn",   "#f97316"),
        ("Feature Request", "pill-feature", "#38bdf8"),
        ("Praise",          "pill-praise",  "#2dd4a0"),
        ("Neutral",         "pill-neutral", "#4e5370"),
    ]
    st.markdown("<div class='tag-summary'>", unsafe_allow_html=True)
    for tag, css, color in items:
        count = tag_counts.get(tag, 0)
        st.markdown(f"""
        <div class="tag-sum-card">
            <div class="tag-sum-num" style="color:{color}">{count}</div>
            <div class="tag-sum-lbl"><span class="pill {css}">{tag}</span></div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── TAB 2 — CHARTS ───────────────────────────────────────────────────────────
with tabs[1]:
    divider("Tag & Root Cause")
    c1, c2 = st.columns(2)
    with c1:
        tag_df = enriched["AI Tag"].value_counts().reset_index()
        tag_df.columns = ["Tag","Count"]
        fig = go.Figure(go.Pie(
            labels=tag_df["Tag"], values=tag_df["Count"], hole=0.58,
            marker=dict(colors=[TAG_COLORS.get(t,"#4e5370") for t in tag_df["Tag"]],
                        line=dict(color="#080910", width=2))
        ))
        fig.update_traces(textfont_color="#eceef5", textfont_size=12)
        fig.update_layout(**PLOT_LAYOUT, title="Tag Distribution")
        chart_wrap(fig)

    with c2:
        rc_df = enriched["Root Cause"].value_counts().reset_index()
        rc_df.columns = ["Root Cause","Count"]
        fig2 = px.bar(rc_df, x="Count", y="Root Cause", orientation="h",
                      color="Count", color_continuous_scale=["#1a1a2e","#7b5ea7","#a78bfa"])
        fig2.update_layout(**PLOT_LAYOUT, title="Root Cause Breakdown",
                           yaxis=dict(**GRID), xaxis=dict(**GRID), coloraxis_showscale=False)
        chart_wrap(fig2)

    divider("Risk & Segments")
    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.scatter(enriched, x="Urgency Score", y="Churn %",
                          color="AI Tag", size="Sentiment Score",
                          hover_data=(["Name","AI Summary"] if "Name" in enriched.columns else ["AI Summary"]),
                          color_discrete_map=TAG_COLORS)
        fig3.update_layout(**PLOT_LAYOUT, title="Urgency vs Churn Risk",
                           xaxis=dict(**GRID, title="Urgency Score"),
                           yaxis=dict(**GRID, title="Churn %"))
        chart_wrap(fig3)

    with c4:
        if "Persona Type" in enriched.columns:
            pd_agg = enriched.groupby("Persona Type").agg(
                avg_sent=("Sentiment Score","mean"),
                avg_churn=("Churn %","mean"),
                count=("AI Tag","count")
            ).reset_index()
            fig4 = px.scatter(pd_agg, x="avg_sent", y="avg_churn",
                              size="count", color="avg_churn", text="Persona Type",
                              color_continuous_scale=["#2dd4a0","#f97316","#f43f5e"])
            fig4.update_traces(textposition="top center", textfont_color="#eceef5", textfont_size=11)
            fig4.update_layout(**PLOT_LAYOUT, title="Persona: Sentiment vs Churn",
                               coloraxis_showscale=False,
                               xaxis=dict(**GRID, title="Avg Sentiment"),
                               yaxis=dict(**GRID, title="Avg Churn %"))
            chart_wrap(fig4)

    c5, c6 = st.columns(2)
    with c5:
        if "Drop-off Point" in enriched.columns:
            drop = enriched["Drop-off Point"].dropna()
            drop = drop[~drop.str.strip().str.lower().isin(["none as such","nan","none",""])]
            if len(drop) > 0:
                dc = drop.value_counts().reset_index()
                dc.columns = ["Drop-off","Count"]
                fig5 = px.bar(dc, x="Drop-off", y="Count",
                              color="Count", color_continuous_scale=["#1a1a2e","#f97316"])
                fig5.update_layout(**PLOT_LAYOUT, title="Drop-off Points",
                                   xaxis=dict(**GRID, tickangle=-30),
                                   yaxis=dict(**GRID), coloraxis_showscale=False)
                chart_wrap(fig5)

    with c6:
        if "Retention Signal" in enriched.columns:
            ret = enriched["Retention Signal"].value_counts().reset_index()
            ret.columns = ["Signal","Count"]
            c_map = {"positive":"#2dd4a0","negative":"#f43f5e","neutral":"#4e5370"}
            fig6 = go.Figure(go.Bar(
                x=ret["Signal"], y=ret["Count"],
                marker_color=[c_map.get(s,"#4e5370") for s in ret["Signal"]],
                marker_line_color="#080910", marker_line_width=2
            ))
            fig6.update_layout(**PLOT_LAYOUT, title="Retention Signals",
                               xaxis=dict(**GRID), yaxis=dict(**GRID))
            chart_wrap(fig6)


# ── TAB 3 — CHURN WATCHLIST ──────────────────────────────────────────────────
with tabs[2]:
    churn_df = enriched[enriched["Churn %"] >= 55].sort_values("Churn %", ascending=False)
    if churn_df.empty:
        st.markdown("<div class='empty'><div class='empty-icon'>✅</div><div class='empty-text'>No high-risk churn users in this batch.</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:12px;color:#4e5370;margin-bottom:20px;font-family:IBM Plex Mono,monospace;'>{len(churn_df)} users at ≥55% churn probability · sorted by risk</div>", unsafe_allow_html=True)
        for _, row in churn_df.iterrows():
            cp  = float(row.get("Churn %", 0))
            bc  = "#f43f5e" if cp >= 80 else "#f97316" if cp >= 65 else "#fbbf24"
            nm  = row.get("Name","Anonymous")
            ps  = row.get("Persona Type","")
            age = row.get("Age","")
            ls  = row.get("No. of Lessons Done","—")
            streak_val = row.get("Streaks","—")
            urg = row.get("Urgency Score",5)
            rt  = row.get("Root Cause","")
            tg  = row.get("AI Tag","Churn Risk")
            fb  = row.get("AI Summary") or row.get("Raw Feedback","")
            act = row.get("PM Action","Review manually")
            st.markdown(f"""
            <div class="wl-card">
              <div class="wl-top">
                <div>
                  <div class="wl-name">{nm}</div>
                  <div class="wl-meta">{ps} · {age} · {ls} lessons · streak {streak_val}</div>
                </div>
                <div style="text-align:right;">
                  <div class="wl-risk-num" style="color:{bc}">{cp:.0f}%</div>
                  <div class="wl-urg">Urgency {urg}/10</div>
                </div>
              </div>
              <div class="wl-bar-bg"><div class="wl-bar-fg" style="width:{min(cp,100)}%;background:{bc};"></div></div>
              <div class="wl-pills">{pill(tg)}<span class="pill pill-neutral">{rt}</span></div>
              <div class="wl-quote">"{str(fb)[:220]}"</div>
              <div class="wl-action">{act}</div>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 4 — BUG MATRIX ───────────────────────────────────────────────────────
with tabs[3]:
    bugs_df = enriched[enriched["AI Tag"] == "Bug"].sort_values("Urgency Score", ascending=False)
    if bugs_df.empty:
        st.markdown("<div class='empty'><div class='empty-icon'>✅</div><div class='empty-text'>No bugs flagged in this batch.</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:12px;color:#4e5370;margin-bottom:20px;font-family:IBM Plex Mono,monospace;'>{len(bugs_df)} bugs · sorted by urgency</div>", unsafe_allow_html=True)
        for _, row in bugs_df.iterrows():
            urg = row.get("Urgency Score",5)
            imp = row.get("Impact","Medium")
            if urg >= 8:
                bb, bc, bt = "rgba(244,63,94,0.1)", "#f43f5e", f"CRITICAL · U{urg}"
            elif urg >= 6:
                bb, bc, bt = "rgba(249,115,22,0.1)", "#f97316", f"HIGH · U{urg}"
            else:
                bb, bc, bt = "rgba(78,83,112,0.1)", "#4e5370", f"MEDIUM · U{urg}"
            nm  = row.get("Name","")
            ps  = row.get("Persona Type","")
            age = row.get("Age","")
            rt  = row.get("Root Cause","")
            fb  = row.get("AI Summary") or row.get("Raw Feedback","")
            act = row.get("PM Action","")
            ff  = []
            for fk, fl in [("Friction: Tech Bug","Tech Bug"),("Friction: UX","UX"),
                           ("Friction: Content","Content"),("Friction: Paywall","Paywall")]:
                if str(row.get(fk,"")).strip() not in ["","nan","None"]:
                    ff.append(fl)
            fs = " · ".join(ff) if ff else rt
            st.markdown(f"""
            <div class="bug-card">
              <div class="bug-badge-col">
                <div class="bug-badge" style="background:{bb};color:{bc};">{bt}</div>
                <div class="bug-impact">{imp}</div>
              </div>
              <div>
                <div class="bug-name">{nm} <span style="font-weight:400;color:#4e5370;font-size:12px;">— {ps} · {age}</span></div>
                <div class="bug-persona">{fs}</div>
                <div class="bug-quote">"{str(fb)[:200]}"</div>
                <div class="bug-action">{act}</div>
              </div>
            </div>""", unsafe_allow_html=True)


# ── TAB 5 — FEATURE MAP ──────────────────────────────────────────────────────
with tabs[4]:
    feat_data = safe_json(R["feat_raw"])
    if feat_data and isinstance(feat_data, list) and len(feat_data) > 0:
        st.markdown(f"<div style='font-size:12px;color:#4e5370;margin-bottom:20px;font-family:IBM Plex Mono,monospace;'>{len(feat_data)} feature opportunities · AI ranked</div>", unsafe_allow_html=True)
        for feat in feat_data:
            pri = feat.get("priority","Medium")
            eff = feat.get("effort","Medium")
            qw  = feat.get("quick_win", False)
            pc      = {"Critical":"#f43f5e","High":"#f97316","Medium":"#38bdf8","Low":"#2dd4a0"}.get(pri,"#4e5370")
            ec      = {"Low":"#2dd4a0","Medium":"#f97316","High":"#f43f5e"}.get(eff,"#4e5370")
            pc_rgba = {"Critical":"rgba(244,63,94","High":"rgba(249,115,22","Medium":"rgba(56,189,248","Low":"rgba(45,212,160"}.get(pri,"rgba(78,83,112")
            ec_rgba = {"Low":"rgba(45,212,160","Medium":"rgba(249,115,22","High":"rgba(244,63,94"}.get(eff,"rgba(78,83,112")
            st.markdown(f"""
            <div class="feat-card">
              <div class="feat-top">
                <div class="feat-name">{feat.get('feature','')}</div>
                <div class="feat-badges">
                  {"<span class='pill pill-praise'>⚡ Quick Win</span>" if qw else ""}
                  <span class="feat-badge" style="background:{pc_rgba},0.1);color:{pc};border:1px solid {pc_rgba},0.3);">{pri} Priority</span>
                  <span class="feat-badge" style="background:{ec_rgba},0.1);color:{ec};border:1px solid {ec_rgba},0.3);">{eff} Effort</span>
                </div>
              </div>
              <div class="feat-demand">{feat.get('estimated_demand','')}</div>
              <div class="feat-why">{feat.get('why_it_matters','')}</div>
            </div>""", unsafe_allow_html=True)
    else:
        if "Feature Complained About" in enriched.columns:
            for feat, cnt in enriched["Feature Complained About"].value_counts().items():
                if str(feat).strip().lower() not in ["none","nan",""]:
                    st.markdown(f"""
                    <div class="feat-card">
                      <div class="feat-top">
                        <div class="feat-name">{feat}</div>
                        <div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4e5370;">{cnt} mentions</div>
                      </div>
                    </div>""", unsafe_allow_html=True)


# ── TAB 6 — PRAISE ───────────────────────────────────────────────────────────
with tabs[5]:
    praise_df = enriched[enriched["AI Tag"] == "Praise"].sort_values("Sentiment Score", ascending=False)
    if praise_df.empty:
        st.markdown("<div class='empty'><div class='empty-icon'>🔍</div><div class='empty-text'>No praise entries in this filtered batch.</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(45,212,160,0.06);border:1px solid rgba(45,212,160,0.18);
                    border-radius:12px;padding:16px 20px;margin-bottom:24px;">
            <strong style="color:#2dd4a0;">What's working — don't break it.</strong>
            <span style="font-size:13px;color:#9da3be;margin-left:8px;">These are your retention anchors.
            Reference before every major feature change.</span>
        </div>""", unsafe_allow_html=True)

        pc1, pc2 = st.columns(2)
        cols = [pc1, pc2]
        for i, (_, row) in enumerate(praise_df.iterrows()):
            nm  = row.get("Name","")
            ps  = row.get("Persona Type","")
            age = row.get("Age","")
            sc  = row.get("Sentiment Score",0)
            fb  = row.get("AI Summary") or row.get("Raw Feedback","")
            lk  = row.get("Most Liked Feature","")
            ins = row.get("Persona Insight","")
            liked_str = f" · {lk}" if lk and str(lk).lower() not in ["none","nan",""] else ""
            with cols[i % 2]:
                st.markdown(f"""
                <div class="praise-card">
                  <div class="praise-meta">{nm} · {ps} · {age} · {sc}/10{liked_str}</div>
                  <div class="praise-quote">"{str(fb)[:240]}"</div>
                  {f'<div class="praise-insight">{ins}</div>' if ins and str(ins).lower() not in ["insufficient data","nan",""] else ""}
                </div>""", unsafe_allow_html=True)


# ── TAB 7 — PERSONAS ─────────────────────────────────────────────────────────
with tabs[6]:
    lines = [l.strip() for l in R["persona_text"].split("\n") if l.strip()]
    st.markdown("<div class='insight-card'><div class='insight-label'>AI Persona Analysis</div>", unsafe_allow_html=True)
    for line in lines:
        clean = re.sub(r"\*\*(.*?)\*\*", r"<b style='color:#a78bfa;'>\1</b>", line).lstrip("-•1234567890. ").strip()
        if clean:
            st.markdown(f"""
            <div class="insight-bullet">
              <div class="insight-dot" style="background:#a78bfa;"></div>
              <div class="insight-text">{clean}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if "Persona Type" in enriched.columns:
        pa1, pa2 = st.columns(2)
        with pa1:
            pc = enriched.groupby("Persona Type")["Churn %"].mean().sort_values().reset_index()
            pc.columns = ["Persona","Avg Churn %"]
            fig_pc = px.bar(pc, x="Avg Churn %", y="Persona", orientation="h",
                            color="Avg Churn %", color_continuous_scale=["#2dd4a0","#f97316","#f43f5e"])
            fig_pc.update_layout(**PLOT_LAYOUT, title="Churn Risk by Persona",
                                 xaxis=dict(**GRID), yaxis=dict(**GRID), coloraxis_showscale=False)
            chart_wrap(fig_pc)
        with pa2:
            ps2 = enriched.groupby("Persona Type")["Sentiment Score"].mean().sort_values(ascending=False).reset_index()
            ps2.columns = ["Persona","Avg Sentiment"]
            fig_ps = px.bar(ps2, x="Persona", y="Avg Sentiment",
                            color="Avg Sentiment", color_continuous_scale=["#f43f5e","#f97316","#2dd4a0"])
            fig_ps.update_layout(**PLOT_LAYOUT, title="Sentiment by Persona",
                                 xaxis=dict(**GRID, tickangle=-30),
                                 yaxis=dict(**GRID), coloraxis_showscale=False)
            chart_wrap(fig_ps)


# ── TAB 8 — COMPETITORS ──────────────────────────────────────────────────────
with tabs[7]:
    comp = R.get("comp_text","")
    if comp:
        lines = [l.strip() for l in comp.split("\n") if l.strip()]
        st.markdown("<div class='insight-card'><div class='insight-label'>Competitive Intelligence · AI Generated</div>", unsafe_allow_html=True)
        for line in lines:
            clean = re.sub(r"\*\*(.*?)\*\*", r"<b style='color:#38bdf8;'>\1</b>", line).lstrip("-•1234567890. ").strip()
            if clean:
                st.markdown(f"""
                <div class="insight-bullet">
                  <div class="insight-dot" style="background:#38bdf8;"></div>
                  <div class="insight-text">{clean}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if "Competitor Mentioned" in enriched.columns:
        cd = enriched["Competitor Mentioned"].dropna()
        cd = cd[~cd.str.strip().str.lower().isin(["","nan","none"])]
        if len(cd) > 0:
            cc_df = cd.value_counts().reset_index()
            cc_df.columns = ["Competitor","Mentions"]
            fig_cc = px.bar(cc_df, x="Competitor", y="Mentions",
                            color="Mentions", color_continuous_scale=["#1a1a2e","#38bdf8"])
            fig_cc.update_layout(**PLOT_LAYOUT, title="Competitor Mentions",
                                 xaxis=dict(**GRID), yaxis=dict(**GRID), coloraxis_showscale=False)
            chart_wrap(fig_cc)
    if not comp:
        st.markdown("<div class='empty'><div class='empty-icon'>🏁</div><div class='empty-text'>No competitor mentions found in this batch.</div></div>", unsafe_allow_html=True)


# ── TAB 9 — FULL TABLE ───────────────────────────────────────────────────────
with tabs[8]:
    show = [c for c in [
        "Name","Persona Type","Age","AI Tag","Sentiment Score","Urgency Score",
        "Churn %","Impact","Root Cause","Retention Signal","AI Summary","PM Action"
    ] if c in enriched.columns]

    search = st.text_input("", placeholder="🔍  Search by name, summary, tag, persona…", label_visibility="collapsed")
    disp = enriched[show]
    if search:
        mask = disp.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
        disp = disp[mask]
    st.markdown(f"<div style='font-size:11px;color:#4e5370;font-family:IBM Plex Mono,monospace;margin-bottom:8px;'>{len(disp)} rows</div>", unsafe_allow_html=True)
    st.dataframe(disp, use_container_width=True, height=500)


# ── TAB 10 — EXPORT ──────────────────────────────────────────────────────────
with tabs[9]:
    st.markdown("<div style='font-size:14px;color:#9da3be;margin-bottom:24px;'>Download your enriched data and PM-ready reports.</div>", unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button(
            "⬇  Full Enriched CSV",
            enriched.to_csv(index=False).encode("utf-8"),
            "postmortem_enriched.csv", "text/csv", use_container_width=True
        )
        st.caption("All AI tags, scores, and PM actions")

    with e2:
        churn_only = enriched[enriched["Churn %"] >= 55]
        st.download_button(
            "⬇  Churn Watchlist CSV",
            churn_only.to_csv(index=False).encode("utf-8"),
            "churn_watchlist.csv", "text/csv", use_container_width=True
        )
        st.caption(f"{len(churn_only)} high-risk users")

    with e3:
        bugs_only = enriched[enriched["AI Tag"] == "Bug"]
        st.download_button(
            "⬇  Bug Report CSV",
            bugs_only.to_csv(index=False).encode("utf-8"),
            "bugs_report.csv", "text/csv", use_container_width=True
        )
        st.caption(f"{len(bugs_only)} bugs exported")

    st.markdown("---")
    report_lines = [
        f"# Feedback Postmortem Report\n\n",
        f"**Entries:** {n}  |  **Avg Sentiment:** {avg_s}/10  |  **Avg Churn:** {avg_c}%  |  **Critical Issues:** {crit}\n\n",
        "---\n\n## Executive Brief\n\n", R["exec_sum"], "\n\n",
        "---\n\n## Churn Watchlist\n\n"
    ]
    for _, row in enriched[enriched["Churn %"] >= 55].sort_values("Churn %", ascending=False).head(10).iterrows():
        report_lines.append(f"- **{row.get('Name','')}** ({row.get('Churn %',0):.0f}%): {row.get('AI Summary','')}\n")
    report_lines += ["\n---\n\n## Persona Analysis\n\n", R["persona_text"], "\n\n"]
    if R.get("comp_text"):
        report_lines += ["---\n\n## Competitive Intelligence\n\n", R["comp_text"], "\n\n"]

    st.download_button(
        "⬇  Full PM Report (Markdown)",
        "".join(report_lines).encode("utf-8"),
        "postmortem_report.md", "text/markdown"
    )
    st.caption("Paste into Notion or share with your founding team")