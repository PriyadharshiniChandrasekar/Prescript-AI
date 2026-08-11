<div align="center">

# 💊 PrescriptAI
### AI-Powered Prescription Reminder System

A full-stack web app that helps patients track prescriptions, get reminded to take medicine on time and chat with an AI assistant ("Aura") about drug information — powered by the **Groq LLM API**.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Visit_App-16c9a8?style=for-the-badge)](https://prescript-ai.vercel.app/pages/login.html)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM_API-F55036?style=flat-square)
![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

<img width="1920" height="1080" alt="PrescriptAI Dashboard" src="https://github.com/user-attachments/assets/66c581c0-410e-48f1-ab38-63ee373ece0c" />

</div>

---

## 🚀 Live Demo

| | |
|---|---|
| 🌐 **Frontend** | [prescript-ai.vercel.app](https://prescript-ai.vercel.app/pages/login.html) |
| ⚙️ **Backend API** | [prescriptai-backend.onrender.com](https://prescriptai-backend.onrender.com) |

> **Note:** The backend runs on Render's free tier, so it may "sleep" after 15 minutes of inactivity. The first request can take **30–50 seconds** to wake up — this is expected free-tier cold-start behaviour, not a bug.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Authentication** | Secure register/login with hashed passwords and session cookies |
| 📊 **Dashboard** | Live stats — today's intake %, upcoming dose, missed doses, active prescriptions |
| 🤖 **AI Prescription Analysis** | Every new medicine is instantly analyzed by Groq — usage, side effects, precautions, food interactions |
| 💬 **AI Assistant ("Aura")** | Full chat interface grounded in the user's real prescriptions, with conversational memory |
| ⏰ **Smart Alerts** | Automatically detects and flags missed doses based on scheduled reminder times |
| 📜 **History Log** | Complete record of every dose taken, skipped, or missed |

---

## 🛠️ Tech Stack

Kept intentionally simple and explainable — no React/Spring/MongoDB — while still covering every required feature (auth, dashboard, prescription analysis, AI, alerts, database).

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Python 3 + Flask (REST API) |
| **Database** | SQLite (file-based, zero setup) |
| **AI / LLM** | Groq API — `llama-3.1-8b-instant` |
| **Auth** | Flask session cookies + password hashing (Werkzeug) |
| **Deployment** | Render (backend, Docker) + Vercel (frontend) |

---

## 📁 Folder Structure

```
prescriptai/
├── backend/
│   ├── app.py              # Flask app: all REST API routes
│   ├── database.py         # SQLite schema + connection helper
│   ├── ai_engine.py        # Groq prompt engineering + LLM calls
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example        # copy to .env and add your GROQ_API_KEY
├── frontend/
│   ├── index.html          # redirects to login
│   ├── pages/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── add_prescription.html
│   │   ├── ai_assistant.html
│   │   ├── history.html
│   │   └── profile.html
│   ├── css/style.css
│   └── js/
│       ├── common.js       # shared fetch/auth helpers
│       ├── auth.js
│       ├── dashboard.js
│       ├── add_prescription.js
│       ├── ai_assistant.js
│       └── history.js
└── docker-compose.yml
```

---

## 🎯 Features Mapped to Requirements

- **Authentication** → `/api/register`, `/api/login`, `/api/logout`, `/api/me` (passwords hashed with `werkzeug.security`, session-cookie based)
- **Dashboard** → `dashboard.html` + `/api/dashboard`: today's intake %, upcoming dose, missed doses, active protocol count, and a live checklist (Taken / Skip buttons)
- **Prescription Analysis (AI)** → when a prescription is added, `ai_engine.py` sends a structured prompt to Groq and returns JSON: what it's used for, side effects, precautions, and food interactions
- **AI Assistant** → `ai_assistant.html` is a full chat UI with Aura, grounded in the user's real prescriptions (context injection) and chat memory (`chat_history` table)
- **Alerts / Reminders** → `intake_logs` table + `/api/dashboard` auto-detects doses whose scheduled time has passed and marks them **missed**
- **Database** → SQLite (`prescriptai.db`, auto-created on first run) with 4 tables: `users`, `prescriptions`, `intake_logs`, `chat_history`

---

## 🧠 Prompt Engineering Principles Used (`backend/ai_engine.py`)

1. **Role / persona definition** — a system prompt defines "Aura" and her tone
2. **Explicit constraints / guardrails** — never diagnose, always recommend a doctor for serious issues, no invented dosages
3. **Output format constraints** — `analyze_prescription()` forces strict JSON output (Groq JSON mode) so the frontend can render clean cards
4. **Context injection / grounding** — `chat_with_aura()` injects the user's real active prescriptions into the system prompt so answers are personalised, not generic
5. **Conversational memory** — last 6 turns of chat history are replayed to the model for coherent multi-turn conversations
6. **Low temperature (0.2–0.4)** — keeps medical-adjacent answers factual and consistent rather than creative

---

## ⚙️ Running It Locally

### Backend
```bash
cd backend
pip install -r requirements.txt

# Add your free Groq API key: https://console.groq.com/keys
cp .env.example .env
# then edit .env and paste your key, OR simply:
export GROQ_API_KEY="your_key_here"      # Mac/Linux
setx GROQ_API_KEY "your_key_here"        # Windows (restart terminal after)

python app.py
```
The API runs at `http://127.0.0.1:5000`. The SQLite file `prescriptai.db` is created automatically on first run.

### Frontend
```bash
cd frontend
python -m http.server 8080
```
Then visit **http://127.0.0.1:8080/pages/login.html**

---

## 🎬 Demo Flow (for viva)

1. **Register** a new account → redirected straight to Dashboard
2. **Add a prescription** (e.g. "Lisinopril", 10mg, twice daily, times 08:00 & 20:00) → Aura instantly returns an AI analysis card
3. **Dashboard** shows the new medicine in today's checklist with reminder times
4. Click **"Taken" / "Skip"** → dashboard stats update live
5. Go to **AI Assistant** → ask *"What are the side effects of Lisinopril?"* → Aura answers using your real prescription as context
6. Check **Prescription History** → full log of every dose taken/missed/skipped

---

## 🔮 Possible Extensions

- Add email/SMS reminders (e.g. via Twilio) for true push alerts
- Add drug-drug interaction checks across all active prescriptions
- Swap SQLite → PostgreSQL/MongoDB for multi-user production scale
- Add browser push notifications using the Notifications Web API

---

<div align="center">

💊 Thank you for checking out PrescriptAI — feedback and contributions are welcome! 🙌

**✨ Priyadharshini Chandrasekar ✨**

</div>
