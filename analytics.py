"""
analytics.py — Local analytics: uploads, scores, missing skills tracking
"""

import os
import json
from datetime import datetime
from typing import List, Dict

ANALYTICS_FILE = "analytics.json"


def _load() -> dict:
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"sessions": [], "missing_skills_freq": {}}


def _save(data: dict):
    try:
        with open(ANALYTICS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def record_session(
    filename: str,
    score: float,
    missing_keywords: List[str],
):
    """Log an ATS analysis session."""
    data = _load()
    data["sessions"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "filename": filename,
        "score": score,
        "missing_count": len(missing_keywords),
    })
    for kw in missing_keywords:
        data["missing_skills_freq"][kw] = data["missing_skills_freq"].get(kw, 0) + 1
    _save(data)


def get_analytics() -> Dict:
    data = _load()
    sessions = data.get("sessions", [])
    scores = [s["score"] for s in sessions if s.get("score", -1) != -1]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    freq = data.get("missing_skills_freq", {})
    top_missing = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_uploads": len(sessions),
        "avg_score": avg_score,
        "sessions": sessions[-20:],  # last 20
        "top_missing_skills": top_missing,
    }
