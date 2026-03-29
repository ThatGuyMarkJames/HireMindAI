<div align='center'>
  <h1>🚀 HireMind AI</h1>
  <p>AI-Powered ATS Resume Analyzer · Career Assistant · Resume Rewriter</p>
</div>

---

## 🌟 Project Overview

HireMind AI is a full-featured, production-grade resume intelligence platform. It parses resumes, performs NER-based ATS scoring with section-wise weighted analysis, provides an AI career assistant with chat history, rewrites resume bullets, compares multiple resumes, and exports detailed PDF reports — all running locally with Ollama.

---

## ✨ Feature Roadmap

| # | Feature | Status |
|---|---------|--------|
| 1 | Resume parsing (PDF, DOCX, TXT) | ✅ Done |
| 2 | Custom spaCy NER model | ✅ Done |
| 3 | Weighted ATS scoring (Skills 45%, Exp 30%, Edu 20%) | ✅ Done |
| 4 | Section-wise score breakdown | ✅ Done |
| 5 | Matched / Missing keyword visualization | ✅ Done |
| 6 | AI Career Chatbot (Ollama / Mistral) | ✅ Done |
| 7 | Chat history (multi-turn conversation) | ✅ Done |
| 8 | Resume Rewrite Feature (AI bullet improvements) | ✅ Done |
| 9 | Multi-Resume Upload & Comparison | ✅ Done |
| 10 | Analytics Dashboard (uploads, trends, gaps) | ✅ Done |
| 11 | PDF Report Export | ✅ Done |
| 12 | Dark modern UI | ✅ Done |
| 13 | Firebase Integration (optional) | 🔧 Configurable |

---

## 🏗 Architecture

```
HireMind AI
├── app.py               ← Streamlit UI (4 pages)
├── resume_parser.py     ← PDF/DOCX/TXT extraction + section detection
├── ats_scorer.py        ← Weighted NER-based ATS scoring engine
├── ai_assistant.py      ← Ollama chatbot + resume rewriter
├── report_generator.py  ← PDF report builder (fpdf2)
├── analytics.py         ← Local JSON analytics tracking
├── requirements.txt
└── ner_model/           ← Your trained spaCy NER model
```

### Scoring Weights

| Section | Weight | What it captures |
|---------|--------|-----------------|
| Skills | 45% | Tools, languages, frameworks |
| Experience | 30% | Job titles, company names, years |
| Education | 20% | Degrees, colleges, graduation year |
| Other | 5% | Location, contact, misc |

---

## 🚀 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Place your NER model
```bash
# Put your trained model in ./ner_model/
# (trained via CLI_Model_Building.ipynb)
```

### 3. Start Ollama
```bash
ollama pull mistral
ollama serve
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 📱 Pages

| Page | Features |
|------|---------|
| 📊 Analyzer | Upload resume, paste JD, get full ATS breakdown + rewrite + PDF |
| 💬 AI Assistant | Multi-turn chatbot with resume + JD context, suggested prompts |
| 📁 Compare Resumes | Upload up to 5 resumes, compare scores side by side |
| 📈 Analytics | Upload trends, score history, most common missing skills |

---

## 🛠 Technologies

- **spaCy** — Custom NER for entity extraction
- **Ollama + Mistral** — Local LLM for chat + rewriting
- **FAISS / pdfplumber / python-docx** — Document processing  
- **fpdf2** — PDF report generation
- **Streamlit** — Web UI
- **Pandas** — Data handling + visualizations

---

## 📜 License

MIT License — see LICENSE file for details.
