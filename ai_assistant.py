"""
ai_assistant.py — Ollama-powered AI assistant with chat history
"""

import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral"


def check_ollama() -> bool:
    """Return True if Ollama is reachable."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def list_models() -> List[str]:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return [DEFAULT_MODEL]


def ask_llm(
    user_message: str,
    system_prompt: str,
    history: List[Dict],
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Send message to Ollama with full chat history.

    Args:
        user_message: Latest user query
        system_prompt: Context injected as system message
        history: List of {role, content} dicts (prior turns)
        model: Ollama model name

    Returns:
        AI response string
    """
    messages = [{"role": "system", "content": system_prompt}]
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "top_p": 0.9,
            "num_ctx": 4096,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        return "⚠️ Cannot connect to Ollama. Run `ollama serve` in a terminal."
    except requests.exceptions.Timeout:
        return "⚠️ Ollama timed out. Try a smaller model or shorter input."
    except Exception as e:
        return f"⚠️ Error: {e}"


def rewrite_resume_bullets(
    resume_text: str,
    jd_text: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Ask LLM to rewrite weak resume bullet points.
    """
    system = """You are an expert resume writer and career coach.
Your task: rewrite resume bullet points to be stronger, more impactful, and better aligned to the job description.
Rules:
- Use action verbs (Developed, Implemented, Led, Optimized, etc.)
- Add quantifiable metrics where possible (%, $, time saved)
- Match keywords from the job description naturally
- Keep it concise and professional
- Output ONLY the rewritten bullets, grouped under their section headers"""

    prompt = f"""RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}

Rewrite the key resume bullet points to better match this job description.
Focus on skills, experience, and achievements."""

    return ask_llm(prompt, system, [], model)


def build_system_prompt(resume_text: str, jd_text: str) -> str:
    return f"""You are HireMind AI — an expert resume coach and career advisor.

CANDIDATE'S RESUME:
{resume_text[:2500]}

JOB DESCRIPTION:
{jd_text[:1500] if jd_text else "Not provided."}

Your role:
- Give specific, actionable resume improvement advice
- Point out gaps between the resume and job description
- Suggest better phrasing, skills to add, or sections to improve
- Be concise, direct, and encouraging
- Always ground advice in the actual resume content above"""
