# 🔬 User\_Feedback\_Postmortem

> \*\*AI-powered user feedback intelligence for product managers.\*\*
> Upload any feedback CSV → every entry gets enriched by AI → get PM-ready insights in minutes.

!\[Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square\&logo=python)
!\[Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat-square\&logo=streamlit)
!\[Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-orange?style=flat-square)
!\[License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

\---

## What it does

Feedback Postmortem takes raw user feedback — from support calls, in-app surveys, NPS responses, or wherever — and runs it through an AI pipeline that turns it into structured PM intelligence.

**Every feedback entry gets:**

* A tag: `Bug` / `Feature Request` / `Praise` / `Churn Risk` / `Neutral`
* A sentiment score (1–10)
* An urgency score (1–10)
* A churn probability (0–100%)
* A root cause category
* An impact rating (Critical / High / Medium / Low)
* A one-line PM action
* A plain-English summary

**Across the full dataset, you get:**

* 📋 Executive PM Brief — 5 founder-ready bullets from the AI
* 🚨 Churn Watchlist — ranked by churn probability with PM actions
* 🐛 Bug Severity Matrix — sorted by urgency and impact
* 💡 Feature Request Map — AI-grouped with priority, effort, and quick-win flags
* ✅ Praise \& Retention Anchors — what's working, don't break it
* 👥 Persona Segmentation — who churns, who engages, and why
* 🏁 Competitive Intelligence — built from competitor mentions in feedback
* 📊 Distribution Charts — tags, root causes, drop-off points, retention signals

\---

## Demo

Don't have a CSV? Switch to **"Try with mock data"** in the sidebar — the app ships with 100 realistic user feedback entries from an Indian EdTech app, covering bugs, churn signals, feature requests, and praise.

\---

## Getting started

### 1\. Clone the repo

```bash
git clone https://github.com/K2169/User\_Feedback\_Postmortem.git
cd feedback-postmortem
```

### 2\. Install dependencies

```bash
pip install -r requirements.txt
```

### 3\. Set up your API key

Get a free Groq API key at [console.groq.com](https://console.groq.com) — no credit card needed.

Create a `.env` file in the project root:

```
GROQ\_API\_KEY=your\_groq\_api\_key\_here
```

### 4\. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

\---

## Project structure

```
feedback-postmortem/
├── app.py                            # Main Streamlit application
├── englishbhashi\_feedback\_100.csv    # Bundled mock dataset (100 entries)
├── requirements.txt                  # Python dependencies
├── .env                              # API key (not committed to git)
├── .gitignore                        # Ignores .env and other local files
└── README.md                         # This file
```

\---

## CSV format

The tool is flexible — it adapts to whatever columns are present. Only **`Raw Feedback`** is required.

Supported columns (all optional except `Raw Feedback`):

|Column|Description|
|-|-|
|`Raw Feedback`|The actual user feedback text (**required**)|
|`Feedback Category`|Pre-existing category label|
|`Sentiment`|Positive / Negative / Neutral|
|`Persona Type`|User persona (Student, Working Professional, etc.)|
|`Age`|Age group|
|`No. of Lessons Done`|Engagement metric|
|`Streaks`|Habit/streak count|
|`Drop-off Point`|Where the user dropped off|
|`Friction: Paywall`|Paywall friction flag|
|`Friction: UX`|UX friction flag|
|`Friction: Content`|Content friction flag|
|`Friction: Tech Bug`|Bug friction flag|
|`Feature Complained About`|Specific feature mentioned|
|`Most Liked Feature`|Feature the user praised|
|`Competitor Mentioned`|Competitor app mentioned|
|`Action Taken`|Follow-up action already taken|

\---

## Sidebar controls

|Control|Description|
|-|-|
|**Data Source**|Toggle between uploading your own CSV or running the bundled mock dataset|
|**Filters**|Filter by sentiment, persona, category, and drop-off point|
|**Rows to analyse**|Slider to control how many rows the AI processes (10–100)|

\---

## Tech stack

|Layer|Technology|
|-|-|
|UI|[Streamlit](https://streamlit.io)|
|AI inference|[Groq API](https://groq.com) — LLaMA 3.3 70B|
|Data|[Pandas](https://pandas.pydata.org)|
|Charts|[Plotly](https://plotly.com)|
|Env management|[python-dotenv](https://github.com/theskumar/python-dotenv)|

\---

## Outputs \& exports

From the **Export** tab you can download:

* **Full enriched CSV** — all original columns + every AI-generated column
* **Churn watchlist CSV** — only users at ≥55% churn probability
* **Bug report CSV** — only bug-tagged entries
* **Full PM report (Markdown)** — executive brief + churn list + persona analysis + competitive intel, ready to paste into Notion or send to your team

\---

## Roadmap

* \[ ] Multi-file upload and comparison across batches
* \[ ] Trend view across weekly/monthly uploads
* \[ ] Slack / email export for the executive brief
* \[ ] Custom tag taxonomy (define your own tags)
* \[ ] Webhook integration with CleverTap / Mixpanel

\---

## Built by

**Krishnam Parasrampuria** — Product Manager 
[LinkedIn](https://linkedin.com/in/Krishnam21) · [GitHub](https://github.com/YOUR_USERNAME)

\---

## License

MIT — free to use, modify, and distribute.

