# 🔥 CRUCIBLE: Dual-Agent AI Technical Interview Platform

<p align="center">
  <img src="frontend/assets/logo.png" alt="CRUCIBLE Flame-Skull Logo" width="130" style="border-radius: 50%;">
</p>

<p align="center">
  <b>"Face the interview before it faces you."</b><br>
  An intelligent, voice-interactive technical mock interview platform powered by an autonomous <b>Dual-Agent Architecture</b> (Confidence Tracker & Adaptive Interrogator), real-time trajectory graphing, and neural conversational speech.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Dual--Agent-Architecture-E11D24?style=for-the-badge&logo=probot&logoColor=white" alt="Dual-Agent Architecture">
  <img src="https://img.shields.io/badge/Groq-Llama%203.3%2070B-F05A28?style=for-the-badge&logo=ai&logoColor=white" alt="Groq Llama 3.3">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Edge--TTS-Neural%20Speech-0078D7?style=for-the-badge&logo=microsoft&logoColor=white" alt="Edge-TTS">
  <img src="https://img.shields.io/badge/Whisper-Fast%20STT-412991?style=for-the-badge&logo=openai&logoColor=white" alt="Whisper">
  <img src="https://img.shields.io/badge/Chart.js-Live%20Telemetry-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Chart.js">
  <img src="https://img.shields.io/badge/Design-Neobrutalism-FFE600?style=for-the-badge&logoColor=black" alt="Neobrutalism UI">
</p>

---

## 📑 Table of Contents

1. [Core Mission: The Dual-Agent Interview Breakthrough](#-core-mission-the-dual-agent-interview-breakthrough)
2. [Why Was CRUCIBLE Created? (The Deep-Rooted Problem & Real Reason)](#-why-was-crucible-created-the-deep-rooted-problem--real-reason)
   - [The Psychological Wall: The "Interview Freeze"](#the-psychological-wall-the-interview-freeze)
   - [The High-Cost & Anxiety Trap of Human Mocks](#the-high-cost--anxiety-trap-of-human-mocks)
   - [Critical Gap Analysis in Existing Solutions (Comparison Matrix)](#️-critical-gap-analysis-in-existing-solutions)
3. [The Dual-Agent Dynamic Interview Architecture](#-the-dual-agent-dynamic-interview-architecture)
   - [Agent 2: Real-Time Confidence Tracker (4 Behavioral Signals)](#agent-2-real-time-confidence-tracker)
   - [Agent 1: Adaptive Interrogator (5 Questioning Strategies)](#agent-1-adaptive-interrogator)
   - [Real-Time Live Reaction Matrix & Dual Trajectory Curve (Chart.js)](#live-reaction-matrix--dual-trajectory-curve)
   - [Sub-Second Unified Turn Evaluation Engine](#sub-second-unified-turn-evaluation-engine)
4. [Natural Speech Engine (Microsoft Edge-TTS)](#-natural-speech-engine-microsoft-edge-tts)
5. [How CRUCIBLE Solves the Problem for Students & Job Seekers](#-how-crucible-solves-the-problem-for-students--job-seekers)
6. [System Architecture & Technology Matrix](#-system-architecture--technology-matrix)
7. [Folder & Project Structure](#-folder--project-structure)
8. [How to Create & Build This Project From Scratch](#-how-to-create--build-this-project-from-scratch)
9. [How to Use CRUCIBLE (Step-by-Step User Guide)](#-how-to-use-crucible-step-by-step-user-guide)
10. [External Datasets & Google Drive ZIP Setup](#-external-datasets--google-drive-zip-setup)
11. [Configuration & Environment Variables](#-configuration--environment-variables)
12. [Automated Verification & Test Suite](#-automated-verification--test-suite)
13. [Future Roadmap](#-future-roadmap)

---

## 🚀 Core Mission: The Dual-Agent Interview Breakthrough

Traditional mock interview tools generate a **static, pre-compiled list of questions** before the interview starts. This static model is broken:

- If a candidate aces a question, a static platform cannot push them into advanced distributed edge cases to test their real depth.
- If a candidate freezes or stumbles, a static platform blindly proceeds to an even harder question, completely unaware that the candidate's technical knowledge broke down.
- Static tools only score written text, ignoring hesitation, verbal hedging, answer latency, and self-contradictions.

**CRUCIBLE's primary innovation is an autonomous Dual-Agent Feedback Loop**:

1. **Agent 2 (Confidence Tracker)** listens first. It monitors candidate confidence in real time across four psycho-linguistic signals: answer length/depth, hedging words, response latency, and factual self-contradictions.
2. **Agent 1 (Adaptive Interrogator)** reads Agent 2's confidence score and trajectory to dynamically adjust difficulty (1 to 10) and formulate the exact next question—pushing harder, easing off, pivoting, or tagging a confirmed **Breaking Point**.
3. **Live Two-Line Reaction Curve (Chart.js)** plots Candidate Confidence (Cyan) alongside Question Difficulty (Crimson) turn-by-turn on screen and archives the trajectory into SQLite.

---

## 🔍 Why Was CRUCIBLE Created? (The Deep-Rooted Problem & Real Reason)

### The Psychological Wall: The "Interview Freeze"

Most candidates—especially university students, self-taught programmers, and junior engineers—do not fail technical interviews because they cannot write code. **They fail because of performance anxiety, fear of judgment, and verbal paralysis.**

1. **Passive Knowledge vs. Spoken Articulation**:
   
   - Candidates can spend months solving LeetCode problems in total silence or building apps alone in their bedrooms.
   - But the moment a senior engineer asks: *"Walk me through your backend architecture, and explain why you chose Redis over an in-memory cache?"*, their heart races, their brain freezes, and their words tumble into incoherent rambling.
   - **Talking through architectural trade-offs out loud under evaluation is a completely different cognitive skill than writing code in isolation.**

2. **The High-Cost & Anxiety Trap of Human Mocks**:
   
   - Services like *Interviewing.io* and *Exponent* charge **$150 to $300 per single session**. For an unemployed student or entry-level job seeker submitting hundreds of applications, paying hundreds of dollars for practice is impossible.
   - Free peer platforms (*Pramp*) match candidates with random strangers on the internet. For beginners already suffering from imposter syndrome, freezing in front of a stranger causes acute social humiliation and reinforces interview terror. Furthermore, human peers frequently cancel last minute and provide subjective, vague feedback (e.g., *"You seemed a bit nervous, good luck"*).
   - Text chatbots (*ChatGPT*, *Claude*) involve typing on a keyboard. Typing carries **zero physiological resemblance** to spoken conversation—it does not train vocal composure, pause control, or concise verbal delivery.

---

### ⚖️ Critical Gap Analysis in Existing Solutions

| Solution Category                                           | Key Offerings                        | Fatal Shortcomings                                                                                                    | Where **CRUCIBLE** Solves It                                                                                     |
|:----------------------------------------------------------- |:------------------------------------ |:--------------------------------------------------------------------------------------------------------------------- |:---------------------------------------------------------------------------------------------------------------- |
| **Paid Human Mock Platforms** *(Interviewing.io, Exponent)* | 1-on-1 with senior engineers         | **Cost Prohibitive & Intimidating**: $150–$300/hr. Triggers severe anxiety; requires scheduling days ahead.           | **100% Free, Private, & On-Demand**: Practice at 2:00 AM in your bedroom with zero judgment.                     |
| **Peer Mock Services** *(Pramp)*                            | Free peer-to-peer exchanges          | **Social Embarrassment & No-Shows**: High anxiety facing strangers; subjective peer feedback; frequent cancellations. | **Autonomous Dual-Agent System**: Available 24/7, never cancels, grades using rigorous objective rubrics.        |
| **Silent Coding Sites** *(LeetCode, HackerRank)*            | Algorithm & data structure puzzles   | **Zero Conversational Training**: Real interviews interrogate resume claims, design decisions, and trade-offs.        | **Resume-Grounded Interrogation**: Probes your actual stack, personal projects, and target job descriptions.     |
| **Text-Based Chatbots** *(ChatGPT, Claude UI)*              | Generic text prompt chatting         | **Typing is Not Speaking**: Cannot build vocal muscle memory or train composure under verbal pressure.                | **Full Voice Loop**: Neural Edge-TTS speaks questions; microphone STT captures and transcribes spoken answers.   |
| **Static Question Banks** *(Standard Mock Apps)*            | Fixed list of 5-10 pre-set questions | **Blind to Candidate Performance**: Cannot adapt difficulty or detect when candidate knowledge collapses.             | **Dual-Agent Dynamic Interrogation**: Questions and difficulty adapt turn-by-turn with breaking-point detection. |

---

## 🤖 The Dual-Agent Dynamic Interview Architecture

```
                      ┌──────────────────────────────────────────────┐
                      │           Candidate Submits Answer           │
                      │  (Spoken Answer + Response Latency in sec)   │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           AGENT 2 — CONFIDENCE TRACKER                            │
│  Evaluates 4 explicit behavioral & verbal signals:                                │
│  1. Answer Length & Substance (Avoidance vs. In-depth Explanation)                 │
│  2. Hedging Lexicon ("maybe", "I think", "shayad", "not sure", "probably")        │
│  3. Response Latency (Elapsed seconds before candidate started answering)         │
│  4. Historical Contradictions (Cross-checks against all prior session answers)    │
│                                                                                   │
│  Output: Continuous Confidence Score (0.0 to 1.0) + Telemetry Breakdown           │
└───────────────────────────────────────────┬───────────────────────────────────────┘
                                             │
                                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           AGENT 1 — ADAPTIVE INTERROGATOR                         │
│  Reads: Confidence Score, 3-Turn Trajectory, Current Difficulty (1-10), Target JD │
│                                                                                   │
│  Executes 5 Dynamic Interrogation Strategies:                                     │
│  - High & Rising        ──► PUSH HARDER (+2.0 difficulty, edge cases, scale)      │
│  - Suddenly Dropped     ──► PIVOT (probe same weak skill from a fresh angle)      │
│  - Low for 3 turns      ──► BREAKING POINT (lock verified knowledge ceiling)      │
│  - Slightly Low         ──► EASE OFF (-1.5 difficulty, test core fundamentals)    │
│  - Stable               ──► MAINTAIN (continue at current difficulty baseline)    │
│                                                                                   │
│  Output: next_question, difficulty (1.0 to 10.0), strategy, breaking_point flag  │
└───────────────────────────────────────────┬───────────────────────────────────────┘
                                             │
                                             ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        LIVE TWO-LINE REACTION MATRIX & GRAPH                      │
│  - Cyan Line (#0284c7): Candidate Confidence (Turn-by-turn, 0.0 to 1.0)           │
│  - Crimson Line (#e11d24): Question Difficulty (Turn-by-turn, 1.0 to 10.0)        │
│  - Breaking Point Pin: Marks exact turn where knowledge ceiling was identified    │
│  - Telemetry Badges: Word Count, Hedging Count, Latency (s), Contradictions       │
│  - Archived to SQLite `user_history` for post-interview review & Profile Graph    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### Agent 2: Real-Time Confidence Tracker

Agent 2 runs first on every candidate answer. It does not ask questions; it evaluates how confident, grounded, and consistent the candidate sounded using 4 signals:

1. **Answer Length & Substance**: Short, 1-sentence answers indicate avoidance or superficial knowledge. Candidates with true mastery provide detailed, structured trade-offs.
2. **Hedging Lexicon Penalty**: Scans for verbal hesitation markers (`maybe`, `I think`, `shayad`, `not sure`, `probably`, `might be`, `I guess`, `kinda`, `sort of`). Each detected hedging word reduces the confidence score.
3. **Response Latency**: Measures elapsed seconds from question delivery until speech initiation. Prompt answers (< 8s) earn confidence bonuses; delayed responses (> 25s) reflect hesitation or lookup delays.
4. **Historical Contradictions**: Cross-references the current answer against all previous answers in the session. Conflicting statements trigger an immediate **-0.25 confidence penalty** and an alert flag in the UI.

**Output**: A continuous confidence score between `0.0` and `1.0`.

---

### Agent 1: Adaptive Interrogator

Agent 1 inspects the confidence score and the 3-turn trajectory to select one of 5 distinct interrogation strategies:

| Strategy           | Trajectory Condition                                | Difficulty Action                | Interrogator Behavior                                                                                             |
|:------------------ |:--------------------------------------------------- |:-------------------------------- |:----------------------------------------------------------------------------------------------------------------- |
| **Push Harder**    | High & Rising ($\Delta \ge +0.15$, Conf $\ge 0.75$) | **+2.0 Difficulty** (up to 10.0) | Drills into high concurrency, extreme edge cases, failure modes, and distributed scale.                           |
| **Pivot**          | Suddenly Dropped ($\Delta \le -0.25$)               | **-1.0 to -1.5 Difficulty**      | Probes the same weak skill from a practical, real-world scenario without shaming the candidate.                   |
| **BREAKING POINT** | Low for 3 consecutive turns (Conf $< 0.40$)         | **Locks to Baseline**            | Confirms candidate's knowledge boundary on that skill. Logs weak skill, tags breaking point pin, and pivots away. |
| **Ease Off**       | Slightly Low ($0.40 \le$ Conf $< 0.55$)             | **-1.5 Difficulty**              | Tests fundamental architectural definitions and core principles to rebuild baseline.                              |
| **Maintain**       | Stable ($0.55 \le$ Conf $< 0.75$)                   | **Current Difficulty**           | Continues natural technical follow-up at current difficulty baseline.                                             |

---

### Live Reaction Matrix & Dual Trajectory Curve

The interview screen renders a real-time **Chart.js** Neobrutalist graph:

- **Blue/Cyan Curve**: Candidate confidence trajectory across turns.
- **Crimson Red Curve**: AI question difficulty scaling up and down.
- **Breaking Point Indicator**: Visual alert banner and map marker placed at the exact turn where candidate knowledge collapsed.
- **Live Signal Telemetry**: Displays Word Count, Hedging Count, Latency (seconds), and Contradiction Status.

### Sub-Second Unified Turn Evaluation Engine

To prevent multiple sequential LLM calls from slowing down the conversation:

- `unified_turn_evaluation()` in `llm.py` performs answer evaluation, coaching critique, blunder detection, and next adaptive question generation in a **single, unified Groq Llama 3.3 call**.
- Total turnaround time is **under 1.2 seconds**.

---

## 🎙️ Natural Speech Engine (Microsoft Edge-TTS)

CRUCIBLE features high-definition neural speech powered by Microsoft Edge-TTS:

1. **Warm, Human Tone (`en-US-AriaNeural`)**: Replaces robotic, flat browser voices with conversational human inflection and natural cadence.
2. **Server-Side MD5 Caching (`uploads/tts_cache/`)**: All synthesized audio files are cached on disk via MD5 hashes. Repeated question playback serves in under **5 milliseconds**.
3. **Startup Warmup & Background Pre-Generation**: Default baseline questions are pre-cached on server launch (`startup_tts_warmup`). In `/api/interview/start` and `/api/interview/turn`, FastAPI `BackgroundTasks` pre-synthesize upcoming questions in the background while the candidate is reading feedback.
4. **Client-Side Prefetching & Race-Condition Prevention**: The frontend proactively caches upcoming question audio. A singleton audio engine with session locking (`currentPlaybackSessionId`) and clean stream termination (`removeAttribute('src')`) eliminates double-speech, lag, and audio overlap.
5. **Automatic Microphone Handover**: When the question finishes speaking (`audio.onended`), microphone recording and the live recording indicator start automatically.

---

## 💡 How CRUCIBLE Solves the Problem for Students & Job Seekers

- **Overcoming the "Freeze" Barrier**: Fresh graduates who have never sat in a corporate technical interview desensitize themselves to the pressure by running 20+ realistic voice simulations before their first interview.
- **Targeted ATS Gap Discovery**: Candidates paste target job descriptions *before* applying to calculate their exact **Role Match Score** and identify missing technical competencies.
- **Verbal Articulation of Complex Systems**: Knowing how to code is different from explaining *why* an architectural choice was made. Voice interaction trains concise, articulate verbal delivery.
- **Exact Knowledge Ceiling Discovery**: The Breaking Point Tracker identifies the exact difficulty level and topics where candidate explanations broke down.
- **Automated PDF Cheatsheet**: Compiles role-tailored PDF cheat sheets using ReportLab with targeted study tips for last-minute revision.

---

## 🏗️ System Architecture & Technology Matrix

```
                     ┌──────────────────────────────────────────────┐
                     │           FRONTEND (Neobrutalism)            │
                     │  HTML5 + CSS3 (High-Contrast Vibrant Retro)  │
                     │  Vanilla JS + Chart.js + Web Audio / STT     │
                     └──────────────────────┬───────────────────────┘
                                            │ HTTP / REST
                                            ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND (`backend/app.py`)                      │
├───────────────────┬───────────────────┬───────────────────┬───────────────────────┤
│   AUTH & PROFILE  │   DOCUMENT ENGINE │   DUAL-AGENT AI   │    SPEECH PIPELINE    │
│  - Session Tokens │  - PDF/DOCX Loader│  - Groq Llama 3.3 │  - Faster-Whisper     │
│  - SQLite3 / ORM  │  - Text Cleaning  │  - Agent 2 (Conf) │  - Microsoft Edge-TTS │
│  - Password Hash  │  - Skill Matcher  │  - Agent 1 (Inter)│  - MD5 Audio Cache    │
└─────────┬─────────┴─────────┬─────────┴─────────┬─────────┴───────────┬───────────┘
          │                   │                   │                     │
          ▼                   ▼                   ▼                     ▼
┌──────────────────┐ ┌─────────────────┐ ┌─────────────────┐  ┌───────────────────┐
│ SQLite Database  │ │ Uploads & Docs  │ │   Groq Cloud    │  │   Edge-TTS Cloud  │
│ (`interview.db`) │ │ (`/uploads/`)   │ │   Llama APIs    │  │ (`en-US-Aria`)    │
└──────────────────┘ └─────────────────┘ └─────────────────┘  └───────────────────┘
```

| Layer                    | Component / Tool                   | Role in CRUCIBLE                                                                                            |
|:------------------------ |:---------------------------------- |:----------------------------------------------------------------------------------------------------------- |
| **Backend Framework**    | **FastAPI**                        | High-performance async Python web framework powering all REST endpoints.                                    |
| **AI / LLM Engine**      | **Groq Cloud API (Llama 3.3 70B)** | Sub-second inference for Agent 2 confidence scoring, Agent 1 dynamic interrogation, and coaching critiques. |
| **Speech-to-Text (STT)** | **Faster-Whisper & Web Speech**    | Real-time speech transcription, live subtitles, and latency measurement.                                    |
| **Text-to-Speech (TTS)** | **Microsoft Edge-TTS**             | Cloud neural speech synthesis generating natural, warm human audio (`en-US-AriaNeural`).                    |
| **Live Telemetry Graph** | **Chart.js**                       | Live dual-curve plotting of Candidate Confidence vs. Question Difficulty with Breaking Point markers.       |
| **Document Loaders**     | **pypdf, pdfplumber, docx2txt**    | Extraction of raw resume text from multi-page PDFs and Word documents.                                      |
| **PDF Generation**       | **ReportLab**                      | Programmatic generation of multi-page, personalized PDF interview study sheets.                             |
| **Database & ORM**       | **SQLAlchemy + SQLite3**           | Relational store for users, profiles, skills, turn trajectories (`turns_data`), and `breaking_points`.      |
| **Frontend UI**          | **Modern Neobrutalism**            | Clean, accessible, retro comic-sticker design featuring solid `#000000` borders and saturated pastels.      |

---

## 📁 Folder & Project Structure

```
working/
├── backend/
│   ├── __init__.py
│   └── app.py                     # FastAPI server (Auth, Skills, Dual-Agent Turn, Edge-TTS, History)
├── frontend/
│   ├── assets/
│   │   └── logo.png               # Official CRUCIBLE Flame-Skull logo asset
│   ├── css/
│   │   └── style.css              # Neobrutalist styling system (borders, shadows, pastels)
│   ├── js/
│   │   ├── api.js                 # Centralized API fetch wrapper and authentication manager
│   │   ├── app.js                 # Home workspace logic (resume upload, JD skill matching)
│   │   ├── interview.js           # Live interview room (Edge-TTS engine, Chart.js live reaction curve, STT)
│   │   ├── prep.js                # Document listing and PDF cheatsheet generator trigger
│   │   └── profile.js             # Candidate analytics, metric cards, and SQLite history table
│   ├── index.html                 # Home / Setup launchpad
│   ├── interview.html             # Fullscreen adaptive interview room with live reaction matrix
│   ├── login.html                 # Sign In & Registration portal
│   ├── prep.html                  # Preparation hub & study material library
│   └── profile.html               # Candidate performance profile & interview history
├── documents/                     # Sample study documents and auto-generated cheatsheet PDFs
├── uploads/                       # User-uploaded PDF/DOCX resume store
│   └── tts_cache/                 # Cached Edge-TTS neural speech MP3 files
├── data_space.py                  # SQLAlchemy ORM models (User, UserProfile, UserHistory)
├── database.py                    # SQLite database engine and session factory
├── doc_loader.py                  # PDF/DOCX extraction and regex text cleaner
├── genrating_cheatsheet.py        # ReportLab automated PDF cheatsheet generator
├── interview_flow.py              # CLI standalone interview pipeline reference
├── llm.py                         # Groq prompts: confidence tracker, interrogator, unified turn
├── main.py                        # Server launcher script (`http://127.0.0.1:8000`)
├── pyproject.toml                 # Project metadata and pip dependency specifications
├── report.py                      # JSON summary builder for candidate performance metrics
├── run.bat                        # One-click Windows startup batch script
├── skill_matcher.py               # 250+ skill taxonomy dictionary and scoring algorithm
├── test_backend_e2e.py            # Automated end-to-end test suite (10 verification checks)
├── transcription.py               # Audio capture and Faster-Whisper transcription handler
├── CRUCIBLE_PROJECT_OVERVIEW.txt  # Comprehensive project documentation export
├── CRUCIBLE_IMPLEMENTATION_SPECIFICATIONS.txt # Complete technical specifications export
└── README.md                      # Primary project documentation
```

---

## 🛠️ How to Create & Build This Project From Scratch

### Step 1: Environment Setup

Verify Python 3.11+ is installed:

```bash
python --version  # Must be >= 3.11
```

Create and activate a virtual environment:

```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Core Dependencies

Install the required packages:

```bash
pip install fastapi uvicorn sqlalchemy python-multipart
pip install langchain langchain-community langchain-core langchain-groq
pip install edge-tts faster-whisper sounddevice numpy
pip install pypdf pdfplumber docx2txt reportlab scikit-learn
```

### Step 3: Database & Models (`data_space.py`)

Create the SQLAlchemy database models:

- `User`: Stores `username` and SHA-256 hashed `password`.
- `UserProfile`: Stores `target_role`, `resume_skill`, `matching_skill`, `missing_skill`, and `score`.
- `UserHistory`: Stores `turns_data` (JSON array of turns with confidence, difficulty, strategy, latency, and breaking points), `breaking_points` (JSON array of failed skills), `avg_confidence`, `peak_difficulty`, `accuracy`, and `blunder`.

### Step 4: Resume Parsing & Skill Matching (`doc_loader.py` & `skill_matcher.py`)

- In `doc_loader.py`, use `pypdf` and `docx2txt` with regex text normalization.
- In `skill_matcher.py`, define 250+ technical skills and calculate deterministic match percentage:
  $$\text{Match Score} = \left( \frac{|\text{Matching Skills}|}{|\text{Job Description Skills}|} \right) \times 100$$

### Step 5: Dual-Agent Prompts & Groq Integration (`llm.py`)

Configure `ChatGroq` with `llama-3.3-70b-versatile`:

- **`track_confidence()`**: Calculates confidence score (`0.0` to `1.0`) from answer length, hedging count, latency, and prior statement contradictions.
- **`adaptive_interrogate()`**: Chooses among the 5 strategies and adjusts difficulty (`1` to `10`).
- **`unified_turn_evaluation()`**: Merges evaluation critique and next-question generation into a single sub-second call.

### Step 6: Neural Speech Service (`backend/app.py`)

- Implement `POST /api/tts/generate` and `GET /api/tts/stream` using `edge_tts.Communicate(text, voice="en-US-AriaNeural")`.
- Store audio in `uploads/tts_cache/` using MD5 keys.
- Add `startup_tts_warmup()` on server startup and schedule background TTS pre-generation via `BackgroundTasks`.

### Step 7: Neobrutalist UI & Chart.js Integration

- Assemble the HTML/CSS templates in `frontend/`.
- In `frontend/js/interview.js`, instantiate the Chart.js graph, stream Edge-TTS audio, track latency, and start microphone recording on `audio.onended`.

---

## 🚀 How to Use CRUCIBLE (Step-by-Step User Guide)

### 1. Launching the Platform

Run the platform using either the Windows batch file or the Python launcher:

```bash
# Option A: Windows batch script
run.bat

# Option B: Direct Python launcher
.\.venv\Scripts\python.exe main.py
```

Open your browser and navigate to **`http://127.0.0.1:8000`**.

---

### 2. User Flow & Features

#### Step 1: Sign In or Register (`/login`)

- Open the login page.
- New users: Click **Register**, enter a username and password, and create an account.
- Returning users: Sign in to resume your workspace.

#### Step 2: Upload Resume & Extract Skills (`/`)

- On the Home screen, drag and drop your **PDF** or **DOCX** resume into the upload zone.
- Click **Resume Skills** to extract all technical skills identified in your resume.

#### Step 3: Match with Job Description (Optional)

- Enter your **Target Role** (e.g., *Backend Engineer*, *Full Stack Developer*, *AI Engineer*).
- Paste the job description and click **Analyze Skill Match**.
- View your **Role Match Score**, matching skill tags (green), and missing skill tags (red).

#### Step 4: Enter the Adaptive Interview Room (`/interview`)

- Click **Enter CRUCIBLE**.
- In the dedicated interview room:
  - **Question Audio**: The question plays aloud in natural human speech via Microsoft Edge-TTS.
  - **Voice Recording**: The microphone automatically activates when speech ends. Speak your response, or type in the input box.
  - **Suggested Answer**: If stuck, click **💡 Auto-write Suggested Answer** to review a model structure.
  - **Submit Answer**: Click **Submit Answer & Evaluate**:
    * Agent 2 computes your confidence score, detects hedging words, and tracks latency.
    * Agent 1 adapts question difficulty and selects strategy (Push Harder, Pivot, Ease Off, Breaking Point).
    * The **Live Reaction Matrix** plots the new turn data on the dual-curve graph.
    * If 3 consecutive drops occur, a **Breaking Point Alert** identifies the exact skill ceiling.
  - Click **Next Adaptive Question →** to proceed.
  - When finished, click **Complete & Save Report** to archive session metrics to SQLite.

#### Step 5: Candidate Profile & Analytics (`/profile`)

- View lifetime interview analytics: Total Sessions, Accuracy Trends, Blunder Counts, and historical session curves with confirmed breaking points.

#### Step 6: Preparation Hub & Custom Cheatsheet (`/prep`)

- Access curated study materials and click **+ Generate Cheatsheet** to compile a personalized PDF study guide based on your resume and skill gaps.

---

## 📦 External Datasets & Google Drive ZIP Setup

If you have downloaded an external dataset, model checkpoints, or sample preparation materials from a Google Drive ZIP link:

1. **Curated Study Materials & Reference PDFs**: Extract into `working/documents/`. Files placed here automatically display in the Preparation Hub table.
2. **Sample Candidate Resumes**: Extract into `working/uploads/`.
3. **Offline Model Weights (Optional)**: Extract into `working/models/`.

---

## ⚙️ Configuration & Environment Variables

Create or edit a `.env` file in the project root:

```env
# Groq Cloud API Key for ultra-fast Llama-3.3 inference
GROQ_API_KEY=your_groq_api_key_here

# Server Settings
HOST=127.0.0.1
PORT=8000

# Whisper Configuration (options: tiny, base, small, medium)
WHISPER_MODEL_SIZE=base

# Edge-TTS Neural Voice (default: en-US-AriaNeural)
EDGE_TTS_VOICE=en-US-AriaNeural
```

> [!TIP]
> You can acquire a free, high-speed API key directly from [Groq Cloud Console](https://console.groq.com/).

---

## 🧪 Automated Verification & Test Suite

CRUCIBLE includes an automated end-to-end test suite verifying the entire stack:

```bash
.\.venv\Scripts\python.exe test_backend_e2e.py
```

The test validates 10 core criteria:

1. Candidate account registration
2. Session login and token generation
3. Candidate profile sanitization (zero password leaks)
4. Job description skill matching and score accuracy
5. Preparation document enumeration
6. **Dual-Agent Interview Turn processing (`/api/interview/turn`)**:
   - Hedging lexicon detection (`maybe`, `I think`, `shayad`, `not sure`)
   - Confidence score calibration
   - Dynamic difficulty adjustment
7. Interview completion and SQLite history persistence
8. SQL history retrieval with turn trajectory and breaking points
9. Programmatic ReportLab PDF cheatsheet compilation
10. **Microsoft Edge-TTS generation, caching, and streaming (`/api/tts/generate`)**

---

## 🔮 Future Roadmap

- [ ] **Multi-Agent Panel Interviews**: Simulate a full interview panel with distinct AI personas (HR Manager, Senior Architect, Engineering Director).
- [ ] **Live Video & Body Language Analysis**: Optional webcam tracking for eye contact and facial confidence cues.
- [ ] **Cybersecurity Red Team Training**: AI escalates the attack vector precisely when the analyst thinks they've contained the threat
- [ ] **Debate & Argumentation Coachings**: AI targets your weakest argument in real time and hits it harder until it holds or breaks.

---

<p align="center">
  Built with ❤️ for every aspiring engineer preparing to conquer their dream technical interview.
</p>
