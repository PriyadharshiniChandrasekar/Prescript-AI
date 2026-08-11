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

#### 📊 Dashboard
<img width="1920" height="978" alt="Screenshot (73)" src="https://github.com/user-attachments/assets/d3c6a991-2449-478f-a343-1b773d59b5dd" />

#### 💬 Aura Chat
<img width="1920" height="969" alt="Screenshot (74)" src="https://github.com/user-attachments/assets/cfa9375b-7530-47f3-9b2f-37adb5cb85e7" />

#### 💊 Add Prescription
<img width="1920" height="978" alt="Screenshot (71)" src="https://github.com/user-attachments/assets/66b6291b-c63c-4e05-992b-c8be81c3806d" />

#### 🤖 AI Analysis
<img width="1920" height="967" alt="Screenshot (72)" src="https://github.com/user-attachments/assets/64633f5c-d020-4673-b3c4-d1ba5ae58d07" />

#### 📜 History Log
<img width="1920" height="963" alt="Screenshot (75)" src="https://github.com/user-attachments/assets/cabe5a08-c033-49c9-95e8-6dfce7eb54bc" />

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
