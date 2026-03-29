"""
ats_scorer.py — Advanced ATS scoring with weighted section-wise analysis
"""

import re
import spacy
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# ─── Label → Section mapping for NER labels from Kaggle resume dataset ───────
LABEL_SECTION_MAP = {
    "SKILLS":              "skills",
    "DESIGNATION":         "experience",
    "COMPANIES_WORKED_AT": "experience",
    "YEARS_OF_EXPERIENCE": "experience",
    "COLLEGE_NAME":        "education",
    "DEGREE":              "education",
    "GRADUATION_YEAR":     "education",
    "EMAIL_ADDRESS":       "other",
    "PHONE_NUMBER":        "other",
    "NAME":                "other",
    "LOCATION":            "other",
    "LINKEDIN_LINK":       "other",
}

# ─── Weights for each section in overall score ────────────────────────────────
SECTION_WEIGHTS = {
    "skills":    0.45,
    "experience": 0.30,
    "education":  0.20,
    "other":      0.05,
}

_nlp_cache: Optional[spacy.language.Language] = None


def _load_nlp() -> spacy.language.Language:
    """Load spaCy NER model (cached)."""
    global _nlp_cache
    if _nlp_cache is None:
        try:
            _nlp_cache = spacy.load("./ner_model")
            logger.info("Custom NER model loaded.")
        except Exception:
            try:
                _nlp_cache = spacy.load("en_core_web_sm")
                logger.warning("Custom NER model not found. Using en_core_web_sm fallback.")
            except Exception as e:
                raise RuntimeError(f"No spaCy model found: {e}")
    return _nlp_cache


def extract_entities(text: str) -> List[Tuple[str, str]]:
    """
    Run NER on text.
    Returns list of (label, text) tuples.
    """
    nlp = _load_nlp()
    doc = nlp(text[:100_000])  # cap input
    return [(ent.label_, ent.text.strip()) for ent in doc.ents if ent.text.strip()]


def extract_keywords_simple(text: str) -> List[str]:
    """
    Fallback: extract multi-word noun phrases + technical tokens.
    Used for JD parsing when NER is less reliable.
    """
    # Match common tech keywords, tools, frameworks
    pattern = re.compile(
        r'\b(python|java|javascript|sql|ml|ai|nlp|docker|aws|react|'
        r'machine learning|deep learning|tensorflow|pytorch|git|linux|'
        r'agile|scrum|api|rest|flask|django|spark|hadoop|kubernetes|'
        r'tableau|power bi|excel|r\b|c\+\+|node\.?js|mongodb|postgresql)\b',
        re.IGNORECASE,
    )
    return [m.group(0).lower() for m in pattern.finditer(text)]


def group_entities_by_section(
    entities: List[Tuple[str, str]]
) -> Dict[str, List[str]]:
    """
    Group extracted entities into sections using label map.
    """
    grouped: Dict[str, List[str]] = {k: [] for k in SECTION_WEIGHTS}
    for label, text in entities:
        section = LABEL_SECTION_MAP.get(label.upper(), "other")
        grouped[section].append(text.lower())
    return grouped


def compute_section_score(
    resume_terms: List[str],
    jd_terms: List[str],
) -> float:
    """
    Compute match score for a single section.
    Returns 0-100 float.
    """
    if not jd_terms:
        return 100.0  # if JD has nothing for this section, full marks
    resume_set = set(t.lower() for t in resume_terms)
    jd_set = set(t.lower() for t in jd_terms)
    if not jd_set:
        return 100.0
    matched = resume_set & jd_set
    return round((len(matched) / len(jd_set)) * 100, 1)


def compute_ats_score(
    resume_text: str,
    jd_text: str,
) -> Dict:
    """
    Full ATS scoring pipeline.

    Returns:
        {
          overall_score: float,
          section_scores: {skills, experience, education, other},
          matched_keywords: List[str],
          missing_keywords: List[str],
          resume_entities: [(label, text)],
          jd_entities: [(label, text)],
          keyword_match_pct: float,
        }
    """
    resume_ents = extract_entities(resume_text)
    jd_ents     = extract_entities(jd_text)

    # Supplement with simple keyword extraction for JD
    jd_simple   = extract_keywords_simple(jd_text)
    resume_simple = extract_keywords_simple(resume_text)

    # Group into sections
    resume_grouped = group_entities_by_section(resume_ents)
    jd_grouped     = group_entities_by_section(jd_ents)

    # Add simple keywords to skills
    resume_grouped["skills"] += resume_simple
    jd_grouped["skills"]    += jd_simple

    # Section-wise scores
    section_scores = {}
    for section, weight in SECTION_WEIGHTS.items():
        section_scores[section] = compute_section_score(
            resume_grouped[section],
            jd_grouped[section],
        )

    # Weighted overall
    overall = sum(
        section_scores[s] * SECTION_WEIGHTS[s]
        for s in SECTION_WEIGHTS
    )
    overall = round(overall, 1)

    # Keyword match analysis (flat sets)
    all_resume_terms = set(
        t.lower() for terms in resume_grouped.values() for t in terms
    )
    all_jd_terms = set(
        t.lower() for terms in jd_grouped.values() for t in terms
    )

    matched  = sorted(all_resume_terms & all_jd_terms)
    missing  = sorted(all_jd_terms - all_resume_terms)
    kw_pct   = round((len(matched) / len(all_jd_terms) * 100), 1) if all_jd_terms else 0.0

    return {
        "overall_score":     overall,
        "section_scores":    section_scores,
        "matched_keywords":  matched,
        "missing_keywords":  missing,
        "resume_entities":   resume_ents,
        "jd_entities":       jd_ents,
        "keyword_match_pct": kw_pct,
    }
