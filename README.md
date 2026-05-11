<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Tech-AI%20%7C%20Cybersecurity%20%7C%20FullStack-blue?style=for-the-badge" alt="Tech">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Scikit--Learn-ML%20Powered-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="ML">
</p>

# 🛡️ CyberSentric

### Real-Time Autonomous Cyber Defense with Self-Healing System

> An AI-Agent-Driven Cybersecurity Defense Platform that uses **Isolation Forest** anomaly detection, **multi-agent orchestration**, and **real-time WebSocket feeds** to autonomously detect, classify, and respond to cyber threats — all from a stunning dark-mode React dashboard.

---

## 👥 Team Members

| Member | Role | Responsibility |
|--------|------|----------------|
| **Krutika** | AI/ML & Documentation Lead | Designed the Isolation Forest ML pipeline, feature engineering, threat classification model, and project documentation |
| **Kanishka** | Frontend Developer | Built the React dashboard UI with real-time charts, glassmorphism design, WebSocket live feeds, and interactive threat analysis |
| **Monika** | Backend Developer | Implemented FastAPI multi-agent architecture, JWT authentication, response automation, and API routing |
| **Adarsh** | System Architect & Integration | Designed the multi-agent orchestrator pipeline, WebSocket infrastructure, Red Team simulation engine, and system integration |

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Folder Structure](#-folder-structure-explained)
- [ML Pipeline — How It Works](#-ml-pipeline--how-it-works)
- [Multi-Agent System](#-multi-agent-system)
- [API Endpoints](#-api-endpoints)
- [Setup & Installation](#-setup--installation)
- [Running the Application](#-running-the-application)
- [Screenshots](#-screenshots)
- [Future Scope](#-future-scope)

---

## 🎯 Project Overview

**CyberSentric** is a full-stack cybersecurity platform that combines **artificial intelligence**, **machine learning**, and **multi-agent systems** to create an autonomous cyber defense solution. Unlike traditional rule-based security tools, CyberSentric uses:

1. **Real ML anomaly detection** (Isolation Forest) — not dummy/hardcoded logic
2. **5 autonomous AI agents** working in a coordinated pipeline
3. **Real-time WebSocket** dashboard for live threat monitoring
4. **Automated response system** that blocks IPs, rate-limits, and alerts admins
5. **Red Team simulation** to test and validate the defense system

### Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **ML Anomaly Detection** | Isolation Forest model trained on 800+ synthetic baseline samples, auto-retrains on live traffic |
| 🤖 **Multi-Agent Pipeline** | Defender → Analyzer → Response → Monitor pipeline processes every request |
| 📊 **Real-Time Dashboard** | Live charts, threat feeds, agent status panels via WebSocket |
| 🔐 **JWT Authentication** | Role-based access (admin/user) with bcrypt password hashing |
| 🔴 **Red Team Simulation** | Automated attack simulations (SQLi, XSS, brute force, prompt injection) |
| ⚡ **Auto Response** | Automatic IP blocking, rate limiting, and admin alerts |
| 📈 **14-Feature Vectors** | Behavioral profiling using request frequency, entropy, error rates, etc. |
| 🔄 **Online Retraining** | Model adapts to traffic drift by retraining every 200 samples |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     REACT FRONTEND                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐    │
│  │Dashboard │ │  Charts  │ │  Threat  │ │  Red Team    │    │
│  │  Panel   │ │(Recharts)│ │   Feed   │ │  Simulator   │    │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘    │
│       │             │            │               │            │
│       └─────────────┴────────────┴───────────────┘            │
│                          │  WebSocket + REST API              │
└──────────────────────────┼───────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                    FASTAPI BACKEND                            │
│                          │                                    │
│  ┌───────────────────────▼───────────────────────────┐       │
│  │              ORCHESTRATOR                          │       │
│  │  (Coordinates all agents in sequence)              │       │
│  └──┬──────────┬──────────┬──────────────┬───────────┘       │
│     │          │          │              │                     │
│  ┌──▼──┐  ┌───▼───┐  ┌──▼───┐  ┌──────▼──────┐             │
│  │DEFE-│  │ANALY- │  │RESP- │  │  MONITOR    │             │
│  │NDER │  │ ZER   │  │ONSE  │  │  AGENT      │             │
│  │AGENT│  │ AGENT │  │AGENT │  │             │             │
│  │     │  │       │  │      │  │  (Logging & │             │
│  │(Rule│  │(ML    │  │(Auto │  │  WebSocket  │             │
│  │Based│  │Isola- │  │Block │  │  Broadcast) │             │
│  │Scan)│  │tion   │  │IPs)  │  │             │             │
│  │     │  │Forest)│  │      │  │             │             │
│  └─────┘  └───┬───┘  └──────┘  └─────────────┘             │
│               │                                               │
│  ┌────────────▼────────────────────────────────┐             │
│  │            ML PIPELINE                       │             │
│  │  ┌──────────────┐  ┌───────────────────┐    │             │
│  │  │   Feature    │  │  Isolation Forest │    │             │
│  │  │  Extractor   │──│  Anomaly Detector │    │             │
│  │  │  (14 dims)   │  │  (scikit-learn)   │    │             │
│  │  └──────────────┘  └────────┬──────────┘    │             │
│  │                             │                │             │
│  │  ┌──────────────────────────▼──────────┐    │             │
│  │  │      Threat Classifier              │    │             │
│  │  │  (ML + Rules → Structured Output)   │    │             │
│  │  └─────────────────────────────────────┘    │             │
│  └─────────────────────────────────────────────┘             │
│                                                               │
│  ┌─────────────────────────────────────────────┐             │
│  │            RED TEAM AGENT                    │             │
│  │  (Simulates attacks to test defenses)        │             │
│  │  • Prompt Injection  • XSS  • SQLi           │             │
│  │  • Command Injection • Brute Force            │             │
│  └─────────────────────────────────────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why It's Used |
|-------|-----------|---------------|
| **Frontend** | React 18 + Vite | Fast, component-based UI with hot module reload |
| **Styling** | Tailwind CSS | Rapid dark-theme styling with glassmorphism effects |
| **Charts** | Recharts | Beautiful, animated data visualisation |
| **Icons** | Lucide React | Clean, modern SVG icon set |
| **Backend** | FastAPI (Python) | High-performance async API with auto-generated docs |
| **ML Model** | Scikit-Learn (Isolation Forest) | Unsupervised anomaly detection — learns what "normal" is |
| **Feature Engineering** | NumPy | Fast numerical computation for feature vectors |
| **Auth** | JWT (python-jose) + bcrypt | Secure token-based authentication with password hashing |
| **Real-Time** | WebSocket (FastAPI) | Instant push updates to the dashboard without polling |
| **Data Models** | Pydantic | Strict data validation and serialisation |

---

## 📁 Folder Structure (Explained)

```
CyberSentric/
│
├── start.bat                       # 🚀 One-click launcher — builds frontend & starts server
├── README.md                       # 📖 This file — complete project documentation
├── docker-compose.yml              # 🐳 Docker setup for containerised deployment
├── .gitignore                      # 🚫 Files/folders excluded from Git
│
├── backend/                        # ⚙️ PYTHON BACKEND (FastAPI)
│   │
│   ├── requirements.txt            # 📦 All Python dependencies listed here
│   ├── .env                        # 🔑 Secret keys (DB URLs, JWT secret) — NEVER commit this
│   ├── .env.example                # 📋 Template showing required environment variables
│   ├── Dockerfile                  # 🐳 Docker config for backend container
│   │
│   └── app/                        # 🏠 Main application package
│       │
│       ├── main.py                 # 🚪 Entry point — creates FastAPI app, registers routes,
│       │                           #    starts monitor heartbeat, serves frontend build
│       │
│       ├── config.py               # ⚙️ Loads settings from .env (DB URLs, JWT secrets,
│       │                           #    CORS origins, app name/version)
│       │
│       ├── orchestrator.py         # 🎯 THE BRAIN — coordinates all 5 agents in sequence:
│       │                           #    Defender → Analyzer → Response → Monitor
│       │                           #    Also handles Red Team simulations
│       │
│       ├── websocket_manager.py    # 📡 Manages WebSocket connections, broadcasts real-time
│       │                           #    events (threats, metrics) to all connected clients
│       │
│       ├── agents/                 # 🤖 AI AGENT MODULES
│       │   ├── __init__.py
│       │   ├── base_agent.py       # 🧱 Abstract base class — defines ThreatResult, AgentEvent,
│       │   │                       #    Severity enum, status tracking (all agents inherit this)
│       │   │
│       │   ├── defender.py         # 🛡️ DEFENDER AGENT — First line of defense
│       │   │                       #    • Regex pattern matching for prompt injection
│       │   │                       #    • XSS / SQLi / Command injection detection
│       │   │                       #    • Shannon entropy analysis for obfuscation
│       │   │                       #    • Input sanitisation (strips malicious tags)
│       │   │
│       │   ├── analyzer.py         # 🧠 ANALYZER AGENT — ML-Powered Intelligence (★ CORE)
│       │   │                       #    • Calls FeatureExtractor for 14-dim vectors
│       │   │                       #    • Runs Isolation Forest inference
│       │   │                       #    • Combines ML + behavioural flags + defender results
│       │   │                       #    • Returns structured threat classification
│       │   │
│       │   ├── response.py         # ⚡ RESPONSE AGENT — Automated mitigation
│       │   │                       #    • Blocks malicious IPs
│       │   │                       #    • Applies rate limiting
│       │   │                       #    • Sends admin alerts
│       │   │                       #    • Logs incidents at appropriate severity
│       │   │
│       │   ├── monitor.py          # 📊 MONITOR AGENT — System health tracking
│       │   │                       #    • Heartbeat system metrics (CPU, memory, connections)
│       │   │                       #    • Broadcasts events to WebSocket subscribers
│       │   │                       #    • Logs all threat responses for audit trail
│       │   │
│       │   └── redteam.py          # 🔴 RED TEAM AGENT — Attack simulator
│       │                           #    • Prompt injection test suite (10 payloads)
│       │                           #    • XSS test suite (5 payloads)
│       │                           #    • SQL injection test suite (5 payloads)
│       │                           #    • Command injection test suite (5 payloads)
│       │                           #    • Brute force login simulation
│       │                           #    • Full suite — runs everything + reports detection rate
│       │
│       ├── ml/                     # 🧪 MACHINE LEARNING PIPELINE
│       │   ├── __init__.py
│       │   ├── feature_extractor.py  # 📐 Extracts 14-dimensional feature vectors:
│       │   │                         #    request_count, failed_logins, unique_endpoints,
│       │   │                         #    payload_size, time_delta, session_duration,
│       │   │                         #    error_rate, requests_per_minute, payload_entropy,
│       │   │                         #    unique_ips, is_login, is_failed, hour_of_day,
│       │   │                         #    special_char_ratio
│       │   │
│       │   ├── anomaly_detector.py   # 🤖 Isolation Forest model:
│       │   │                         #    • Trains on 800 synthetic "normal" samples
│       │   │                         #    • StandardScaler normalisation
│       │   │                         #    • 150 estimator trees, 8% contamination
│       │   │                         #    • Auto-retrains every 200 live samples
│       │   │                         #    • Sigmoid-normalised anomaly scores (0-1)
│       │   │
│       │   └── threat_classifier.py  # 🎯 Merges ML scores + rules → final output:
│       │                             #    { "threat": "brute_force",
│       │                             #      "severity": "high",
│       │                             #      "confidence": 0.92 }
│       │
│       └── routes/                 # 🌐 API ENDPOINTS
│           ├── auth.py             # 🔐 Authentication routes:
│           │                       #    POST /api/auth/login    — JWT token login
│           │                       #    POST /api/auth/register — new user registration
│           │                       #    GET  /api/auth/me       — current user info
│           │
│           └── core.py             # 📡 Core API routes:
│                                   #    POST /api/analyze       — run ML threat analysis
│                                   #    GET  /api/dashboard     — aggregated dashboard data
│                                   #    GET  /api/agents        — all agent statuses
│                                   #    GET  /api/threats       — recent threat data
│                                   #    GET  /api/stats         — chart statistics
│                                   #    POST /api/redteam/simulate — run attack simulation
│                                   #    WS   /api/ws            — WebSocket endpoint
│
├── frontend/                       # 🎨 REACT FRONTEND (Vite)
│   │
│   ├── package.json                # 📦 Node.js dependencies (React, Recharts, Lucide, Tailwind)
│   ├── vite.config.js              # ⚡ Vite dev server config + API proxy to backend
│   ├── tailwind.config.js          # 🎨 Tailwind theme (custom cyber colours, fonts, animations)
│   ├── postcss.config.js           # CSS processing pipeline
│   ├── index.html                  # 🏠 HTML entry point (loads Google Fonts, favicon)
│   ├── Dockerfile                  # 🐳 Docker config for frontend
│   │
│   └── src/                        # 📂 Source code
│       │
│       ├── main.jsx                # 🚪 React entry — mounts App to DOM
│       ├── index.css               # 🎨 Global styles:
│       │                           #    • Tailwind base/components/utilities
│       │                           #    • Glassmorphism .glass class
│       │                           #    • Neon glow effects (.neon-blue, .neon-red)
│       │                           #    • Cyber grid background
│       │                           #    • Severity badge classes
│       │                           #    • Custom scrollbar styling
│       │
│       ├── App.jsx                 # 🏠 Main app layout:
│       │                           #    • Sidebar navigation (6 tabs)
│       │                           #    • Dashboard / Agents / Threats / RedTeam / Logs / Settings
│       │                           #    • JWT auth flow + token management
│       │                           #    • WebSocket event tracking
│       │                           #    • 5-second polling for dashboard data
│       │
│       ├── services/
│       │   └── api.js              # 🌐 API client — all fetch calls to backend
│       │                           #    (login, register, analyze, dashboard, stats, etc.)
│       │
│       ├── hooks/
│       │   └── useWebSocket.js     # 📡 Custom React hook for WebSocket connection
│       │                           #    Auto-reconnects, parses events, tracks status
│       │
│       └── components/             # 🧩 REUSABLE UI COMPONENTS
│           ├── LoginScreen.jsx     # 🔐 Beautiful login/register page with demo credentials
│           ├── Sidebar.jsx         # 📋 Left navigation panel with 6 tab icons
│           ├── Topbar.jsx          # 📊 Top bar showing connection status + quick stats
│           ├── RiskScore.jsx       # 🎯 Animated risk gauge based on latest threat severity
│           ├── AgentPanel.jsx      # 🤖 Grid of agent status cards (5 agents)
│           ├── ThreatFeed.jsx      # 📡 Live scrolling feed of WebSocket threat events
│           ├── Charts.jsx          # 📈 Line chart (threats over time) + Pie chart (attack types)
│           ├── ActionHistory.jsx   # 📋 Table of all automated response actions taken
│           ├── InputAnalyzer.jsx   # ⌨️ Text input to test threat detection with quick-test buttons
│           └── RedTeamPanel.jsx    # 🔴 Red Team simulation launcher + results display
```

---

## 🧠 ML Pipeline — How It Works

### The Problem
Traditional cybersecurity tools use **rule-based detection** — they only catch attacks they've been explicitly programmed to recognize. New, unknown attack patterns slip through.

### Our Solution: Isolation Forest (Unsupervised Learning)
Isolation Forest is a machine learning algorithm that learns what **"normal" traffic looks like**, then flags anything that deviates from normal as anomalous — even attacks it has never seen before.

### Pipeline Steps

#### Step 1: Data Preprocessing & Feature Extraction
Every incoming request is converted into a **14-dimensional numeric feature vector**:

```
Feature Vector (14 dimensions):
───────────────────────────────────────────────────────────────
 [0]  request_count        — How many requests in the last 10 min
 [1]  failed_login_count   — Failed login attempts in window
 [2]  unique_endpoints     — How many different URLs were accessed
 [3]  payload_size         — Size of the request payload (chars)
 [4]  time_delta_seconds   — Time since previous request
 [5]  session_duration     — Total session length
 [6]  error_rate           — Fraction of failed requests
 [7]  requests_per_minute  — Request frequency
 [8]  payload_entropy      — Shannon entropy (randomness) of input
 [9]  unique_ips_for_user  — How many IPs this user has used
 [10] is_login_action      — Whether this is a login attempt
 [11] is_failed_status     — Whether the request failed
 [12] hour_of_day          — Time of day (normalised 0-1)
 [13] special_char_ratio   — Fraction of special characters
```

#### Step 2: Model Training (Isolation Forest)
```python
# At startup, the model trains on 800 synthetic "normal" samples:
model = IsolationForest(
    n_estimators=150,      # 150 decision trees
    contamination=0.08,    # expect ~8% anomalies
    max_features=1.0,      # use all 14 features
)
model.fit(StandardScaler().fit_transform(normal_data))
```

**How Isolation Forest works:**
- It builds random decision trees that try to "isolate" each data point
- Normal points are hard to isolate (they're similar to many others)
- Anomalous points are easy to isolate (they're different from everything)
- Points that get isolated quickly → **anomalous** (shorter tree paths)

#### Step 3: Real-Time Inference
```python
# For each incoming request:
features = feature_extractor.extract(event)    # 14-dim vector
result = anomaly_detector.predict(features)     # ML scoring

# Output:
{
    "anomaly_score": 0.78,           # 0.0 = normal, 1.0 = anomalous
    "classification": "high_threat", # normal | suspicious | high_threat
    "confidence": 0.88,              # model confidence
    "ml_prediction": "anomaly"       # raw model output
}
```

#### Step 4: Threat Classification
The ML score is combined with:
- **Behavioral flags** (failed logins, request rate, endpoint scanning)
- **Defender Agent results** (pattern-matched injection/XSS/SQLi)

Final structured output:
```json
{
    "threat": "brute_force",
    "severity": "high",
    "confidence": 0.92,
    "threat_category": "authentication_attack",
    "recommended_actions": ["block_ip", "alert_admin", "log_critical"]
}
```

#### Step 5: Online Retraining
The model **automatically retrains** every 200 new samples using the accumulated live traffic data. This allows it to adapt to changing traffic patterns without manual intervention.

---

## 🤖 Multi-Agent System

| Agent | Role | How It Works |
|-------|------|-------------|
| **🛡️ Defender** | First filter | Regex pattern matching for known attacks (prompt injection, XSS, SQLi, command injection). Computes entropy for obfuscation detection. Sanitises dangerous inputs. |
| **🧠 Analyzer** | ML brain | Runs the full ML pipeline: feature extraction → Isolation Forest inference → threat classification. Combines ML scores with behavioral analysis. |
| **⚡ Response** | Auto-responder | Executes recommended actions: blocks IPs, applies rate limits, sends alerts, logs incidents. Maintains block lists and action history. |
| **📊 Monitor** | Observer | Broadcasts all events via WebSocket. Tracks system metrics (CPU, memory, connections). Maintains audit trail of all threat-response pairs. |
| **🔴 Red Team** | Tester | Simulates 5 types of attacks through the full pipeline. Measures detection rates. Validates that defenses are working correctly. |

---

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/login` | ❌ | Login with username/password, returns JWT |
| `POST` | `/api/auth/register` | ❌ | Register a new user account |
| `GET` | `/api/auth/me` | ✅ | Get current user info |
| `POST` | `/api/analyze` | ✅ | Submit input for ML threat analysis |
| `GET` | `/api/dashboard` | ✅ | Get full dashboard data (agents, alerts, metrics) |
| `GET` | `/api/agents` | ✅ | Get all 5 agent statuses |
| `GET` | `/api/agents/{name}` | ✅ | Get specific agent details + events |
| `GET` | `/api/threats` | ✅ | Get recent alerts, blocked IPs, action history |
| `GET` | `/api/stats` | ✅ | Get chart data (attack types, severity distribution) |
| `POST` | `/api/redteam/simulate` | 🔒 Admin | Run attack simulation (full/xss/sqli/etc.) |
| `GET` | `/api/redteam/history` | ✅ | Get past simulation results |
| `WS` | `/api/ws` | ❌ | WebSocket for real-time event streaming |

**Default Credentials:**
- **Admin:** `admin` / `admin123`
- **User:** `user` / `user123`

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.10+** (with pip)
- **Node.js 18+** (with npm)
- **Git** (for version control)

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/cybersentric.git
cd cybersentric

# 2. Setup Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt

# 3. Setup Frontend
cd ../frontend
npm install

# 4. Go back to root
cd ..
```

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173
DEBUG=true
```

---

## ▶️ Running the Application

### Option 1: One-Click Start (Windows)
```bash
# Double-click start.bat or run:
start.bat
```
This will build the frontend and start the unified server at `http://localhost:8000`

### Option 2: Development Mode (Two terminals)
```bash
# Terminal 1 — Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend (with hot reload)
cd frontend
npm run dev
```
Frontend dev server: `http://localhost:5173` (proxies API calls to backend)

---

## 🔮 Future Scope

- [ ] **Supabase/PostgreSQL** integration for persistent threat logging
- [ ] **LSTM time-series** model for advanced temporal anomaly detection
- [ ] **Email/SMS alerts** via Twilio or SendGrid for critical threats
- [ ] **Docker Compose** one-click deployment to cloud
- [ ] **Grafana integration** for professional monitoring dashboards
- [ ] **Threat intelligence feeds** (VirusTotal, AbuseIPDB) for IP reputation
- [ ] **Multi-tenant** support for enterprise deployment

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

<p align="center">
  <b>Built with ❤️ by Team CyberSentric</b><br>
  <i>Krutika • Kanishka • Monika • Adarsh</i>
</p>
