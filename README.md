CyberSentric
AI-powered real-time cybersecurity intelligence and response system with threat detection, auto-response, and dashboard visualization.

👥 Team Roles
| Member   | Role                           |
| -------- | ------------------------------ |
| Krutika  | AI/ML & Documentation Lead     |
| Kanishka | Frontend Developer             |
| Monika   | Backend Developer              |
| Adarsh   | System Architect & Integration |

CyberSentric  
Real-Time Autonomous Cyber Defense with Self-Healing System

![Status](https://img.shields.io/badge/Status-Active-success)
![Tech](https://img.shields.io/badge/Tech-AI%20%7C%20Cybersecurity%20%7C%20FullStack-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

🚀 Tagline
An intelligent cybersecurity system that detects, analyzes, and automatically responds to threats in real-time.

---

📌 Project Overview

 🔹 Simple Explanation:
CyberSentric is a smart system that monitors user and system activity, detects suspicious behavior, and automatically takes action (like blocking attacks) without human intervention.

🔹 Technical Explanation:
It is a full-stack AI-powered cybersecurity system that integrates:
- Real-time log monitoring  
- Hybrid threat detection (rule-based + ML + AI reasoning)  
- Autonomous response engine  
- Interactive dashboard for monitoring and control  

---

❗ Problem Statement

Modern cybersecurity systems face critical challenges:

- ⏳ Delayed response to threats  
- ⚠️ High false positives  
- 🧑‍💻 Manual monitoring dependency  
- 📉 Increasing cyber attacks (~10–12% CAGR growth globally)  
- 💸 Global cybercrime cost expected to exceed $10 trillion annually  

👉 Existing systems detect threats but **fail to respond instantly and autonomously**.

---
💡 Solution Overview

CyberSentric solves this by:

- Monitoring logs in real-time  
- Detecting anomalies using ML + rules  
- Using AI to analyze threats  
- Automatically taking actions (block IP, alert admin, etc.)  
- Providing a live dashboard for insights  

---

✨ Features

- 🔍 Real-time log monitoring  
- 🧠 AI-based threat analysis  
- ⚡ Automatic response system (self-healing)  
- 📊 Interactive dashboard  
- 🔐 Authentication & role-based access  
- 🚨 Threat scoring system  
- 📡 Live alerts using WebSockets  
- 📁 Log storage & tracking  

---
🏗️ System Architecture
User Activity / Logs
↓
Log Collector Layer
↓
Detection Engine
(Rules + ML Models)
↓
AI Analysis Engine
↓
Decision Engine
↓
Response System
↓
Database + Dashboard


---

🧰 Tech Stack

🌐 Frontend
- React.js → UI development  
- Tailwind CSS → Styling  
- Axios → API communication  

⚙️ Backend
- FastAPI → High-performance APIs  
- Python → Core logic  

🧠 AI/ML
- Scikit-learn → Anomaly detection  
- LLM APIs → Threat analysis  

🗄️ Database
- MongoDB → Log storage  
- PostgreSQL → Structured data  

☁️ Cloud / Realtime
- Firebase → Authentication & real-time sync  
- WebSockets → Live updates  

 🔐 Security
- JWT Authentication  
- Role-Based Access Control  

---

🛠️ Tools & Technologies

| Tool | Full Form | Why Used |
|------|----------|---------|
| FastAPI | Fast Application Programming Interface | High-speed backend APIs |
| MongoDB | NoSQL Database | Flexible log storage |
| Firebase | Backend-as-a-Service | Auth + real-time features |
| Git | Version Control System | Code management |
| Docker | Containerization Platform | Easy deployment |
| Postman | API Testing Tool | Testing endpoints |


🔮 Future Scope (2026–2050)
🤖 Self-learning AI defense systems

🌐 Zero Trust Architecture integration

🔗 Blockchain-based security

🧬 Predictive threat intelligence

🛰️ Autonomous cyber defense networks

✅ Advantages
Faster threat detection

Reduced human effort

Real-time response

Scalable architecture

❌Limitations
Requires quality data

Possible false positives

Complex implementation

Resource intensive

📈 Market Impact
Global cybersecurity market > $200 Billion

Growing at ~10–12% CAGR

AI-driven security tools are in high demand


---

⚙️ Installation Guide

🔹 1. Clone Repository
```bash
git clone https://github.com/your-username/cybersentric.git
cd cybersentric

▶️ Usage Instructions
Login/Register

Access dashboard

Monitor logs & alerts

System automatically detects threats

Actions (block/alert) are triggered

-Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

-Frontend Setup
cd frontend
npm install
npm run dev

backend/
  ├── routes/        → API endpoints
  ├── models/        → Data models
  ├── services/      → Business logic
  ├── db/            → Database config

frontend/
  ├── pages/         → UI pages
  ├── components/    → Reusable UI
  ├── services/      → API calls

firebase/            → Firebase config
docs/                → Diagrams & reports


