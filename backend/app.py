"""
app.py
------
PrescriptAI backend - Flask + SQLite + Groq.

Run:
    pip install -r requirements.txt
    export GROQ_API_KEY="your_key"
    python app.py

Server starts at http://127.0.0.1:5000
Open frontend/pages/login.html in your browser (or serve the frontend
folder with any static server) to use the app.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, date, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads GROQ_API_KEY from a local .env file if present
except ImportError:
    pass

from database import get_connection, init_db, now_iso
from ai_engine import analyze_prescription, chat_with_aura

app = Flask(__name__)
app.secret_key = "prescriptai-college-project-secret-key-change-me"

# Allow the frontend (opened as a static file / different port) to call the
# API and send the session cookie back and forth. We must list explicit
# origins (not "*") because browsers reject wildcard origins when
# credentials (cookies) are involved.
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
)

app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)

init_db()


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def login_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please log in first."}), 401
        return fn(*args, **kwargs)

    return wrapper


def current_user_id():
    return session.get("user_id")


# ----------------------------------------------------------------------
# AUTHENTICATION
# ----------------------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "An account with this email already exists."}), 409

    password_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, now_iso()),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    session["user_id"] = user_id
    session["user_name"] = name
    return jsonify({"success": True, "message": "Account created successfully.", "name": name})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return jsonify({"success": True, "message": "Logged in successfully.", "name": user["name"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out."})


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "name": session.get("user_name")})


# ----------------------------------------------------------------------
# PRESCRIPTIONS
# ----------------------------------------------------------------------
@app.route("/api/prescriptions", methods=["POST"])
@login_required
def add_prescription():
    data = request.get_json(force=True)
    medicine_name = (data.get("medicine_name") or "").strip()
    dosage = (data.get("dosage") or "").strip()
    frequency = (data.get("frequency") or "").strip()
    times = data.get("times") or []
    start_date = data.get("start_date") or str(date.today())
    end_date = data.get("end_date") or None
    notes = data.get("notes") or ""

    if not medicine_name or not dosage or not frequency or not times:
        return jsonify({"success": False, "message": "Medicine name, dosage, frequency and at least one time are required."}), 400

    # AI prescription analysis (Groq) - prompt engineering in ai_engine.py
    ai_summary = analyze_prescription(medicine_name, dosage, frequency)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prescriptions
            (user_id, medicine_name, dosage, frequency, times, start_date, end_date, notes, ai_summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user_id(), medicine_name, dosage, frequency, json.dumps(times),
        start_date, end_date, notes, json.dumps(ai_summary), now_iso()
    ))
    conn.commit()
    prescription_id = cur.lastrowid

    # seed today's intake log rows so the dashboard checklist has entries
    for t in times:
        cur.execute("""
            INSERT INTO intake_logs (prescription_id, user_id, log_date, scheduled_time, status, logged_at)
            VALUES (?, ?, ?, ?, 'pending', NULL)
        """, (prescription_id, current_user_id(), str(date.today()), t))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Prescription added.", "id": prescription_id, "ai_summary": ai_summary})


@app.route("/api/prescriptions", methods=["GET"])
@login_required
def list_prescriptions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM prescriptions WHERE user_id = ? ORDER BY created_at DESC", (current_user_id(),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for r in rows:
        r["times"] = json.loads(r["times"])
        try:
            r["ai_summary"] = json.loads(r["ai_summary"]) if r["ai_summary"] else None
        except json.JSONDecodeError:
            pass
    return jsonify({"success": True, "prescriptions": rows})


@app.route("/api/prescriptions/<int:pid>", methods=["DELETE"])
@login_required
def delete_prescription(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM prescriptions WHERE id = ? AND user_id = ?", (pid, current_user_id()))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Prescription removed."})


# ----------------------------------------------------------------------
# DASHBOARD / INTAKE / ALERTS
# ----------------------------------------------------------------------
def _ensure_today_logs(user_id):
    """Make sure every active prescription has a log row for each of its
    scheduled times today (covers days after the prescription was created)."""
    conn = get_connection()
    cur = conn.cursor()
    today = str(date.today())
    cur.execute("SELECT * FROM prescriptions WHERE user_id = ?", (user_id,))
    prescriptions = cur.fetchall()
    for p in prescriptions:
        times = json.loads(p["times"])
        for t in times:
            cur.execute("""
                SELECT id FROM intake_logs
                WHERE prescription_id = ? AND log_date = ? AND scheduled_time = ?
            """, (p["id"], today, t))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO intake_logs (prescription_id, user_id, log_date, scheduled_time, status, logged_at)
                    VALUES (?, ?, ?, ?, 'pending', NULL)
                """, (p["id"], user_id, today, t))
    conn.commit()
    conn.close()


@app.route("/api/dashboard", methods=["GET"])
@login_required
def dashboard():
    user_id = current_user_id()
    _ensure_today_logs(user_id)
    today = str(date.today())
    now_time = datetime.now().strftime("%H:%M")

    conn = get_connection()
    cur = conn.cursor()

    # today's checklist (joined with prescription info)
    cur.execute("""
        SELECT il.id as log_id, il.scheduled_time, il.status,
               p.id as prescription_id, p.medicine_name, p.dosage
        FROM intake_logs il
        JOIN prescriptions p ON p.id = il.prescription_id
        WHERE il.user_id = ? AND il.log_date = ?
        ORDER BY il.scheduled_time ASC
    """, (user_id, today))
    checklist = [dict(r) for r in cur.fetchall()]

    taken_count = sum(1 for c in checklist if c["status"] == "taken")
    total_count = len(checklist)

    # missed = pending items whose scheduled time has already passed
    missed = [c for c in checklist if c["status"] == "pending" and c["scheduled_time"] < now_time]
    for m in missed:
        cur.execute("UPDATE intake_logs SET status = 'missed' WHERE id = ?", (m["log_id"],))
    conn.commit()

    # recompute missed count after update
    missed_count = sum(1 for c in checklist if c["status"] == "missed") + len(missed)

    # next upcoming dose (pending, soonest time >= now)
    upcoming = None
    for c in sorted(checklist, key=lambda x: x["scheduled_time"]):
        if c["status"] == "pending" and c["scheduled_time"] >= now_time:
            upcoming = c
            break

    cur.execute("SELECT COUNT(*) as cnt FROM prescriptions WHERE user_id = ?", (user_id,))
    active_protocols = cur.fetchone()["cnt"]
    conn.close()

    return jsonify({
        "success": True,
        "date": today,
        "taken": taken_count,
        "total": total_count,
        "missed": missed_count,
        "upcoming": dict(upcoming) if upcoming else None,
        "active_protocols": active_protocols,
        "checklist": checklist,
    })


@app.route("/api/intake/<int:log_id>", methods=["POST"])
@login_required
def update_intake(log_id):
    data = request.get_json(force=True)
    status = data.get("status")  # "taken" or "skipped"
    if status not in ("taken", "skipped"):
        return jsonify({"success": False, "message": "Invalid status."}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE intake_logs SET status = ?, logged_at = ?
        WHERE id = ? AND user_id = ?
    """, (status, now_iso(), log_id, current_user_id()))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Marked as {status}."})


@app.route("/api/history", methods=["GET"])
@login_required
def history():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT il.log_date, il.scheduled_time, il.status, p.medicine_name, p.dosage
        FROM intake_logs il
        JOIN prescriptions p ON p.id = il.prescription_id
        WHERE il.user_id = ?
        ORDER BY il.log_date DESC, il.scheduled_time DESC
        LIMIT 100
    """, (current_user_id(),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "history": rows})


# ----------------------------------------------------------------------
# AI ASSISTANT (AURA) - Groq powered chat
# ----------------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"success": False, "message": "Message cannot be empty."}), 400

    user_id = current_user_id()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT medicine_name, dosage, frequency FROM prescriptions WHERE user_id = ?", (user_id,))
    active_prescriptions = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT role, message FROM chat_history WHERE user_id = ? ORDER BY id ASC", (user_id,))
    chat_history = [dict(r) for r in cur.fetchall()]

    reply = chat_with_aura(user_message, active_prescriptions, chat_history)

    cur.execute("INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?, 'user', ?, ?)",
                (user_id, user_message, now_iso()))
    cur.execute("INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?, 'assistant', ?, ?)",
                (user_id, reply, now_iso()))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "reply": reply})


@app.route("/api/chat/history", methods=["GET"])
@login_required
def chat_history_route():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, message, created_at FROM chat_history WHERE user_id = ? ORDER BY id ASC",
                (current_user_id(),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "history": rows})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
