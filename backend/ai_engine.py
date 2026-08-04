"""
ai_engine.py
------------
All Groq LLM calls live here. This is the "prompt engineering" core of the
project. Two capabilities are exposed:

    1. analyze_prescription()  -> one-shot structured analysis of a new
                                   medicine (used/for, common side effects,
                                   precautions, food interactions)
    2. chat_with_aura()        -> multi-turn conversational assistant that
                                   answers drug-related questions, grounded
                                   in the user's own active prescriptions.

Prompt engineering principles applied:
    - Clear persona / role definition (system prompt)
    - Explicit task instructions + output format constraints
    - Context injection (few-shot style grounding with user's real data)
    - Guardrails (no diagnosis, always recommend a doctor for serious issues)
    - Temperature tuned low (0.3) for factual, consistent answers
"""

import os
import json
from groq import Groq

# ---------------------------------------------------------------------
# Set your key as an environment variable before running the server:
#   export GROQ_API_KEY="your_key_here"        (Mac/Linux)
#   setx GROQ_API_KEY "your_key_here"           (Windows)
# Get a free key at https://console.groq.com
# ---------------------------------------------------------------------
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

MODEL = "llama-3.1-8b-instant"   # fast + free-tier friendly on Groq

# System prompt = persona + rules (prompt engineering: role + constraints)
SYSTEM_PERSONA = """You are Aura, a calm, friendly pharmacology assistant \
inside the PrescriptAI app. Your job is to explain medicines in simple, \
plain language for everyday patients.

Rules you must always follow:
1. Never give a medical diagnosis and never tell a user to stop/start a \
   medicine on your own authority.
2. Always mention that a doctor or pharmacist should be consulted for any \
   serious, urgent, or personal medical decision.
3. Keep answers short: use bullet points, avoid long paragraphs.
4. If asked about dosages, only repeat the standard label information, \
   never invent numbers.
5. Be warm and reassuring in tone, never alarming unless the situation is \
   genuinely urgent (e.g. overdose, severe allergic reaction) - in that \
   case clearly say to seek emergency help immediately.
"""


def _safe_chat_completion(messages, temperature=0.3, max_tokens=500, json_mode=False):
    """Wrapper around the Groq chat completion call with basic error handling."""
    try:
        kwargs = dict(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": str(e)}) if json_mode else \
            "Aura is temporarily unavailable. Please check your GROQ_API_KEY " \
            f"or internet connection. (details: {e})"


def analyze_prescription(medicine_name, dosage, frequency):
    """
    One-shot structured prompt: asks the model to return STRICT JSON so the
    frontend can render it into neat cards (prompt engineering: output
    format constraint + JSON mode).
    """
    user_prompt = f"""Analyze this prescription and respond ONLY with a JSON
object (no markdown, no extra text) with exactly these keys:
"used_for" (1 short sentence),
"common_side_effects" (array of max 4 short strings),
"precautions" (array of max 3 short strings),
"food_interaction" (1 short sentence).

Medicine: {medicine_name}
Dosage: {dosage}
Frequency: {frequency}
"""
    messages = [
        {"role": "system", "content": SYSTEM_PERSONA},
        {"role": "user", "content": user_prompt},
    ]
    raw = _safe_chat_completion(messages, temperature=0.2, max_tokens=400, json_mode=True)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {
            "used_for": "Analysis unavailable right now.",
            "common_side_effects": [],
            "precautions": [],
            "food_interaction": raw if isinstance(raw, str) else "N/A",
        }


def chat_with_aura(user_message, active_prescriptions, chat_history):
    """
    Multi-turn chat grounded in the user's real prescriptions
    (prompt engineering: context injection so answers are personalised
    instead of generic).
    """
    if active_prescriptions:
        med_list = "\n".join(
            f"- {p['medicine_name']} ({p['dosage']}, {p['frequency']})"
            for p in active_prescriptions
        )
        context = f"The user is currently taking:\n{med_list}\n"
    else:
        context = "The user has no active prescriptions on record.\n"

    messages = [{"role": "system", "content": SYSTEM_PERSONA + "\n" + context}]

    # include short rolling history for conversational memory
    for turn in chat_history[-6:]:
        role = "assistant" if turn["role"] == "assistant" else "user"
        messages.append({"role": role, "content": turn["message"]})

    messages.append({"role": "user", "content": user_message})

    return _safe_chat_completion(messages, temperature=0.4, max_tokens=350)
