# PrescriptAI — AI-Powered Prescription Reminder System

A college mini/major project: a web app that helps a patient track prescriptions,
get reminded to take medicine on time, and chat with an AI assistant ("Aura")
about drug information — powered by the **Groq LLM API**.


![Uploading Screenshot (27).png…]()


---

## 1. Tech Stack (kept intentionally simple)

| Layer          | Technology                                   |
|----------------|-----------------------------------------------|
| Frontend       | HTML5, CSS3, Vanilla JavaScript (no framework needed) |
| Backend        | Python 3 + Flask (REST API)                  |
| Database       | SQLite (file-based, zero setup)              |
| AI / LLM       | Groq API (`llama-3.1-8b-instant`)            |
| Auth           | Flask session cookies + password hashing (werkzeug) |
| Deployment     | Docker / Docker Compose (also runs locally with no containers) |

No React/Spring/MongoDB is used on purpose — this keeps the project easy to
explain in a viva while still covering every required feature (auth,
dashboard, prescription analysis, AI, alerts, database).

---

## 2. Folder Structure

```
prescriptai/
├── backend/
│   ├── app.py             # Flask app: all REST API routes
│   ├── database.py        # SQLite schema + connection helper
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

## 3. Features Mapped to Requirements

- **Authentication** → `/api/register`, `/api/login`, `/api/logout`, `/api/me`
  (passwords hashed with `werkzeug.security`, session-cookie based).
- **Dashboard** → `dashboard.html` + `/api/dashboard`: today's intake %,
  upcoming dose, missed doses, active protocol count, and a live checklist
  (Taken / Skip buttons), styled like the reference screenshot.
- **Prescription Analysis (AI)** → when a prescription is added, `ai_engine.py`
  sends a structured prompt to Groq and returns JSON: what it's used for,
  side effects, precautions, and food interactions — shown instantly on the
  Add Prescription page.
- **AI Assistant** → `ai_assistant.html` is a full chat UI with Aura, grounded
  in the user's real prescriptions (context injection) and chat memory
  (`chat_history` table).
- **Alerts / Reminders** → `intake_logs` table + `/api/dashboard` auto-detects
  doses whose scheduled time has passed and marks them **missed**; the
  dashboard shows a red "Missed Today" alert card.
- **Database** → SQLite (`prescriptai.db`, auto-created on first run) with 4
  tables: `users`, `prescriptions`, `intake_logs`, `chat_history`.

---

## 4. Prompt Engineering Principles Used (`backend/ai_engine.py`)

1. **Role / persona definition** — a system prompt defines "Aura" and her tone.
2. **Explicit constraints / guardrails** — never diagnose, always recommend a
   doctor for serious issues, no invented dosages.
3. **Output format constraints** — `analyze_prescription()` forces strict JSON
   output (Groq JSON mode) so the frontend can render clean cards.
4. **Context injection / grounding** — `chat_with_aura()` injects the user's
   real active prescriptions into the system prompt so answers are
   personalised, not generic.
5. **Conversational memory** — last 6 turns of chat history are replayed to
   the model for coherent multi-turn conversations.
6. **Low temperature (0.2–0.4)** — keeps medical-adjacent answers factual and
   consistent rather than creative.

---

## 5. Running It Locally (no Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt

# Add your free Groq API key (https://console.groq.com/keys)
cp .env.example .env
# then edit .env and paste your key, OR simply:
export GROQ_API_KEY="your_key_here"      # Mac/Linux
setx GROQ_API_KEY "your_key_here"        # Windows (restart terminal after)

python app.py
```
The API runs at `http://127.0.0.1:5000`. The SQLite file `prescriptai.db` is
created automatically on first run.

### Frontend
No build step needed — just open the file directly, or serve it (recommended
so cookies behave correctly):
```bash
cd frontend
python -m http.server 8080
```
Then visit **http://127.0.0.1:8080/pages/login.html**

---

## 6. Running with Docker

```bash
export GROQ_API_KEY="your_key_here"
docker compose up --build
```
- Backend API → `http://localhost:5000`
- Frontend    → `http://localhost:8080/pages/login.html`

This also satisfies the "deploy in Docker" requirement — the same
`docker-compose.yml` can be pushed to an AWS EC2 instance or an Azure VM and
run with the same command.

---

## 7. Demo Flow (for viva)

1. Register a new account → redirected straight to Dashboard.
2. Add a prescription (e.g. "Lisinopril", 10mg, twice daily, times 08:00 & 20:00)
   → Aura instantly returns an AI analysis card.
3. Dashboard shows the new medicine in today's checklist with reminder times.
4. Click "Taken" / "Skip" → dashboard stats update live.
5. Go to AI Assistant → ask "What are the side effects of Lisinopril?" → Aura
   answers using your real prescription as context.
6. Check Prescription History → full log of every dose taken/missed/skipped.

---

## 8. Notes / Possible Extensions

- Add email/SMS reminders (e.g. via Twilio) for true push alerts.
- Add drug-drug interaction checks across all active prescriptions.
- Swap SQLite → PostgreSQL/MongoDB for multi-user production scale.
- Add browser push notifications using the Notifications Web API.
