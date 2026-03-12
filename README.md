<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-2.x-lightgrey?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Gemini_AI-Flash-FF6F00?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" />
</p>

<h1 align="center">🔮 Clarion — See Truth Clearly</h1>

<p align="center">
  <strong>An AI-powered credibility intelligence platform that scores the trustworthiness of posts from Reddit, Twitter/X, and news articles — in real time.</strong>
</p>

<p align="center">
  Clarion combines community analysis, NLP, large language models, fact-checking APIs, and reverse image search into a single credibility score you can actually understand.
</p>

---

## ✨ What Does Clarion Do?

Ever read a headline and thought *"Is this real?"* — Clarion answers that question for you.

Paste any URL from **Reddit**, **Twitter/X**, or a **news website**, and Clarion will:

1. **Scrape the content** — pulls the post, article text, and user comments
2. **Analyze sentiment & sarcasm** — NLP pipeline with VADER + a transformer-based sarcasm detector
3. **Score credibility** — a multi-layered scoring engine that weighs community consensus, source reputation, fact-check results, and more
4. **Cross-reference trusted news** — checks whether the story is reported by outlets like Reuters, BBC, AP News, etc.
5. **Verify images** — reverse image search via Google Lens to catch recycled/old photos
6. **Get an AI verdict** — Google Gemini analyzes the content for sensationalism, logical fallacies, and overall believability
7. **Return an explained score** — with a breakdown of *why* the score is what it is

All of this is wrapped in a beautiful, interactive 3D orb-based UI built with React, Three.js, and Framer Motion.

---

## 🖼️ Preview

The landing page features an animated 3D **particle orb** that serves as the central navigation hub. Hovering reveals orbiting menu buttons — *Top Posts Today*, *Check a Post*, *History*, *Sources*, *Settings*, and *Light/Dark Mode*.

The orb dynamically changes color based on the credibility score of the post you're viewing:
- 🟣 **Purple** — neutral / no score
- 🟢 **Green** — likely credible
- 🟡 **Gold** — highly credible
- 🔴 **Red** — likely unreliable

---

## 🏗️ Architecture Overview

```
clarion/
├── app/                          # Flask backend
│   ├── main.py                   # API routes & entry point
│   ├── models.py                 # SQLAlchemy models (Post, Comment, Source)
│   ├── run_pipeline.py           # Batch processing for unscored posts
│   └── utils/
│       ├── database.py           # PostgreSQL connection (SQLAlchemy)
│       ├── reddit_api.py         # Reddit ingestion via PRAW
│       ├── twitter_fallback_scraper.py  # Twitter/X via syndication API + Nitter fallbacks
│       ├── news_scraper.py       # News article scraping (newspaper3k + BeautifulSoup)
│       ├── nlp_pipeline.py       # Sentiment analysis, sarcasm detection, language detection
│       ├── credibility.py        # Multi-signal credibility scoring engine
│       ├── llm_analysis.py       # Gemini AI content analysis
│       ├── news_cross_check.py   # Cross-referencing via NewsAPI against trusted sources
│       ├── image_check.py        # Reverse image search via Google Lens (SerpAPI)
│       ├── seed_sources.py       # Pre-seed trusted source entries
│       └── init_db.py            # Database initialization
│
├── clarion-frontend/             # React frontend
│   ├── src/
│   │   ├── App.jsx               # Main layout, navigation, theme toggle
│   │   ├── components/
│   │   │   ├── OrbCanvas.jsx     # 3D particle orb (React Three Fiber)
│   │   │   ├── OrbMenuOrbit.jsx  # Orbiting menu buttons
│   │   │   └── OrbMenuOverlay.jsx
│   │   ├── pages/
│   │   │   ├── SectionTopToday.jsx   # Top posts feed with live scoring
│   │   │   ├── SectionCheck.jsx      # URL checker with score breakdown
│   │   │   ├── SectionHistory.jsx    # Previously analyzed posts
│   │   │   └── SectionSettings.jsx   # User preferences
│   │   ├── api/                  # API client (fetch-based)
│   │   └── store/                # Zustand state management
│   ├── package.json
│   └── tailwind.config.js
│
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not committed)
└── .gitignore
```

---

## ⚙️ How the Scoring Works

Clarion doesn't rely on a single signal — it fuses **multiple independent checks** into one score:

| Signal | Description | Impact |
|--------|-------------|--------|
| **Community Consensus** | Analyzes Reddit/Twitter comments for claims of truth or falsehood | Core baseline score |
| **Sarcasm Detection** | Hybrid detector (heuristics + transformer) identifies sarcastic comments | Prevents false signals |
| **Source Trust Score** | Pre-seeded trust ratings for known news domains (BBC = 9, satire sites = 1) | Weighted into score |
| **Google Fact Check API** | Queries Google's fact-check database for matching claims | ±0.3 adjustment |
| **News Cross-Reference** | Checks if the story is reported by Reuters, AP, BBC, NPR, etc. via NewsAPI | +0.4 if corroborated |
| **LLM Analysis (Gemini)** | Evaluates sensationalism, logical fallacies, and overall credibility | Weighted blend |
| **Image Provenance** | Reverse image search via Google Lens to detect recycled photos | -0.8 penalty if recycled |
| **Community Sentiment** | Emotional tone of comments (separate from truth-assessment) | Displayed alongside score |

The final **advanced score** blends these signals with platform-specific weights. For Reddit, community analysis is prioritized. For news articles, source reliability and fact-checks carry more weight.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL** (running locally or remotely)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/clarion.git
cd clarion
```

### 2. Set Up the Backend

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Download the spaCy English model
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/clariondb

# Reddit API (create an app at https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=clarion/1.0

# Google Fact Check API
GOOGLE_FACTCHECK_API_KEY=your_key

# Google Gemini AI
GEMINI_API_KEY=your_key

# NewsAPI (https://newsapi.org)
NEWS_API_KEY=your_key

# SerpAPI for reverse image search (https://serpapi.com)
SERPAPI_API_KEY=your_key
```

> **Note:** The app works progressively — if an API key is missing, that specific check is simply skipped. You can start with just the database and Reddit credentials.

### 4. Initialize the Database

```bash
python -c "from app.utils.database import init_db; init_db()"
python -c "from app.utils.seed_sources import seed_sources; seed_sources()"
```

### 5. Start the Backend

```bash
python -m flask --app app.main run --debug
```

The API will be available at `http://localhost:5000`.

### 6. Set Up the Frontend

```bash
cd clarion-frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/posts` | Get all posts with comments |
| `GET` | `/posts/<id>` | Get a single post with comments |
| `GET` | `/search?q=query` | Search posts by title |
| `POST` | `/check_url` | Analyze a URL (legacy) |
| `GET/POST` | `/check-post?url=...` | Analyze a URL — returns cached or fresh score |
| `GET` | `/top-posts?source=news` | Get top posts (auto-fetches if stale) |
| `GET` | `/history` | Get last 50 analyzed posts |

---

## 🧠 NLP & AI Pipeline

### Sarcasm Detection
Uses a **hybrid approach**: explicit keyword cues, heuristic scoring (capitalization, punctuation patterns, sentiment flips), and a **transformer model** (`helinivan/english-sarcasm-detector`) as a tie-breaker.

### Sentiment Analysis
**VADER** sentiment analysis runs on every comment, scoring emotional tone from -1 (very negative) to +1 (very positive).

### Language Detection
Uses `langdetect` to filter non-English comments before analysis — ensures only relevant comments influence the score.

### LLM Content Analysis
**Google Gemini 2.0 Flash Lite** evaluates post content for:
- Sensationalism level (0–1)
- Logical fallacies
- Overall credibility rating
- Comment classification (refuting / supporting / questioning / neutral)

---

## 🛠️ Tech Stack

### Backend
- **Flask** — lightweight Python web framework
- **SQLAlchemy** — ORM for PostgreSQL
- **PRAW** — Reddit API wrapper
- **newspaper3k + BeautifulSoup** — article scraping
- **VADER + Transformers** — sentiment & sarcasm detection
- **Google Gemini** — LLM-powered content analysis
- **NewsAPI** — news cross-referencing
- **SerpAPI** — Google Lens reverse image search

### Frontend
- **React 19** — UI framework
- **Vite** — build tool
- **TailwindCSS** — utility-first styling
- **React Three Fiber + Three.js** — 3D particle orb visualization
- **Framer Motion** — smooth animations & transitions
- **Recharts** — data visualization
- **Zustand** — lightweight state management
- **React Router** — client-side routing

---

## 📁 Data Models

### Post
Stores scraped content with scoring results:
- `title`, `url`, `platform` (Reddit / Twitter / News / Image)
- `credibility_score` (baseline), `advanced_score` (multi-signal)
- `community_sentiment`, `sensationalism_score`, `corroboration_score`
- `llm_verdict` (JSON), `image_provenance_status`, `score_explanation` (JSON)

### Comment
Stores individual comments linked to posts:
- `text`, `sentiment_score`, `is_sarcastic`, `language`
- `classification` (refuting / supporting / questioning / neutral)

### Source
Tracks known news domains with pre-assigned trust scores.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve Clarion:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ and a healthy skepticism for headlines.
</p>
