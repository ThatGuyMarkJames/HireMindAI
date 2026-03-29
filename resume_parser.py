"""
resume_parser.py — Text extraction from PDF, DOCX, TXT
"""

import re
import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file) -> str:
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        return text
    except Exception as e:
        logger.error(f"PDF error: {e}")
        raise ValueError(f"Could not read PDF: {e}")


def extract_text_from_docx(file) -> str:
    try:
        from docx import Document
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        logger.error(f"DOCX error: {e}")
        raise ValueError(f"Could not read DOCX: {e}")


def extract_text_from_txt(file) -> str:
    try:
        raw = file.read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")
    except Exception as e:
        raise ValueError(f"Could not read TXT: {e}")


def extract_text(uploaded_file) -> str:
    """Route to correct extractor based on file type."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx") or name.endswith(".doc"):
        return extract_text_from_docx(uploaded_file)
    elif name.endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {name}")


def preprocess_text(text: str) -> str:
    """Clean extracted text."""
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_sections(text: str) -> dict:
    """
    Roughly split resume into sections by common headings.
    Returns dict: {section_name: section_text}
    """
    section_patterns = {
        "skills":      r"(skills?|technical skills?|core competencies|technologies)",
        "experience":  r"(experience|work experience|employment|work history|professional experience)",
        "education":   r"(education|academic|qualification|degree)",
        "projects":    r"(projects?|personal projects?|key projects?)",
        "summary":     r"(summary|objective|profile|about)",
        "certifications": r"(certif|license|credential)",
    }

    lines = text.split(". ")
    sections = {k: "" for k in section_patterns}
    current_section = "summary"

    for line in lines:
        stripped = line.strip().lower()
        matched = False
        for section, pattern in section_patterns.items():
            if re.search(pattern, stripped, re.I) and len(stripped) < 60:
                current_section = section
                matched = True
                break
        if not matched:
            sections[current_section] += line + " "

    return {k: v.strip() for k, v in sections.items()}
