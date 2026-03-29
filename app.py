"""
app.py — HireMind AI · Fixed version (syntax error resolved)
"""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="HireMind AI", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
    --bg:#0a0a0f; --bg2:#111118; --card:#16161f; --border:#2a2a3e;
    --accent:#6366f1; --accent2:#818cf8; --green:#10b981;
    --amber:#f59e0b; --red:#ef4444; --text:#e8e8f0; --muted:#8888aa; --radius:12px;
}
html,body,[class*="css"]{font-family:'Inter',sans-serif !important;}
.stApp{background:var(--bg) !important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"]{background:var(--bg2) !important;border-right:1px solid var(--border) !important;}
.stButton>button{background:linear-gradient(135deg,#6366f1,#4f46e5) !important;color:white !important;border:none !important;border-radius:8px !important;font-weight:500 !important;transition:all 0.2s !important;}
.stButton>button:hover{transform:translateY(-1px) !important;box-shadow:0 4px 20px rgba(99,102,241,0.4) !important;}
.section-bar-wrap{margin:8px 0;}
.section-bar-label{display:flex;justify-content:space-between;font-size:0.85rem;color:var(--text);margin-bottom:4px;}
.section-bar-bg{background:#1e1e2e;border-radius:4px;height:8px;overflow:hidden;}
.section-bar-fill{height:100%;border-radius:4px;}
.chip-row{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;}
.chip{display:inline-block;padding:3px 12px;border-radius:20px;font-size:0.78rem;font-weight:500;font-family:'JetBrains Mono',monospace;}
.chip-green{background:rgba(16,185,129,0.12);color:#10b981;border:1px solid rgba(16,185,129,0.3);}
.chip-red{background:rgba(239,68,68,0.12);color:#ef4444;border:1px solid rgba(239,68,68,0.3);}
.chat-user{background:linear-gradient(135deg,#3730a3,#4c1d95);color:#e8e8ff;padding:12px 16px;border-radius:18px 18px 4px 18px;max-width:78%;margin-left:auto;margin-bottom:12px;font-size:0.9rem;line-height:1.6;}
.chat-ai{background:var(--card);border:1px solid var(--border);color:var(--text);padding:14px 18px;border-radius:18px 18px 18px 4px;max-width:82%;margin-bottom:12px;font-size:0.9rem;line-height:1.7;}
.chat-label{font-size:0.68rem;font-weight:600;letter-spacing:0.06em;margin-bottom:4px;text-transform:uppercase;}
.chat-ai-label{color:var(--accent2);}
.chat-user-label{color:#a78bfa;text-align:right;}
.sec-head{font-size:1rem;font-weight:600;color:var(--text);border-left:3px solid var(--accent);padding-left:10px;margin:1.5rem 0 0.75rem;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:var(--card) !important;border:1px solid var(--border) !important;color:var(--text) !important;border-radius:8px !important;}
[data-testid="stFileUploader"]{background:var(--card) !important;border:2px dashed var(--border) !important;border-radius:var(--radius) !important;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
hr{border-color:var(--border) !important;}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1rem;}
</style>
""", unsafe_allow_html=True)

from resume_parser    import extract_text, preprocess_text
from ats_scorer       import compute_ats_score
from ai_assistant     import ask_llm, build_system_prompt, rewrite_resume_bullets, check_ollama, list_models
from analytics        import record_session, get_analytics
from report_generator import generate_pdf_report


# ─── Session State ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "chat_history": [], "ats_result": None, "resume_text": "",
        "jd_text": "", "resume_name": "", "rewrite_text": "",
        "resumes": {}, "llm_model": "mistral",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── _run_chat DEFINED HERE — before any page uses it ────────────────────────
def _run_chat(question: str):
    system = build_system_prompt(st.session_state.resume_text, st.session_state.jd_text)
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.spinner("Thinking..."):
        response = ask_llm(
            user_message=question,
            system_prompt=system,
            history=st.session_state.chat_history[:-1],
            model=st.session_state.llm_model,
        )
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div style="font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,#818cf8,#6ee7b7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;padding:0.5rem 0 0.25rem;">🚀 HireMind AI</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;color:#8888aa;margin-bottom:1rem;letter-spacing:0.05em;">AI-Powered Resume Analyzer</div>', unsafe_allow_html=True)

    ollama_ok = check_ollama()
    st.markdown(f'<div style="font-size:0.75rem;color:{"#10b981" if ollama_ok else "#ef4444"};margin-bottom:1rem;">{"● Ollama Connected" if ollama_ok else "● Ollama Offline — run: ollama serve"}</div>', unsafe_allow_html=True)

    with st.expander("⚙️ LLM Settings"):
        models = list_models()
        st.session_state.llm_model = st.selectbox("Model", models if models else ["mistral"], key="model_sel")

    st.divider()
    st.markdown('<div style="font-size:0.72rem;color:#8888aa;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;">Navigation</div>', unsafe_allow_html=True)
    pages = ["📊 Analyzer", "💬 AI Assistant", "📁 Compare Resumes", "📈 Analytics"]
    page = st.radio("", pages, label_visibility="collapsed")

    st.divider()
    analytics = get_analytics()
    st.markdown(f"""
    <div style="font-size:0.72rem;color:#8888aa;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Stats</div>
    <div style="display:flex;gap:10px;">
        <div style="flex:1;background:#16161f;border:1px solid #2a2a3e;border-radius:8px;padding:8px;text-align:center;">
            <div style="font-size:1.2rem;font-weight:700;color:#818cf8;">{analytics["total_uploads"]}</div>
            <div style="font-size:0.65rem;color:#8888aa;">Uploads</div>
        </div>
        <div style="flex:1;background:#16161f;border:1px solid #2a2a3e;border-radius:8px;padding:8px;text-align:center;">
            <div style="font-size:1.2rem;font-weight:700;color:#10b981;">{analytics["avg_score"]}%</div>
            <div style="font-size:0.65rem;color:#8888aa;">Avg Score</div>
        </div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Analyzer":
    st.markdown('<h1 style="font-size:1.8rem;font-weight:700;margin:0;">Resume ATS Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8888aa;margin-top:4px;margin-bottom:1.5rem;">Upload your resume + paste a job description to get a full ATS breakdown</p>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="large")
    with col_left:
        st.markdown('<div class="sec-head">📄 Upload Resume</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("PDF, DOCX or TXT", type=["pdf","docx","txt"], label_visibility="collapsed")
    with col_right:
        st.markdown('<div class="sec-head">💼 Job Description</div>', unsafe_allow_html=True)
        jd_text = st.text_area("Paste JD", height=160, placeholder="Paste the full job description here...", label_visibility="collapsed")

    if st.button("🔍 Analyze Resume", use_container_width=True):
        if not uploaded:
            st.warning("Please upload a resume first.")
        elif not jd_text.strip():
            st.warning("Please enter a job description.")
        else:
            with st.spinner("Extracting text..."):
                resume_text = preprocess_text(extract_text(uploaded))
                jd_clean    = preprocess_text(jd_text)
            with st.spinner("Computing ATS scores..."):
                result = compute_ats_score(resume_text, jd_clean)
            st.session_state.ats_result  = result
            st.session_state.resume_text = resume_text
            st.session_state.jd_text     = jd_clean
            st.session_state.resume_name = uploaded.name
            st.session_state.resumes[uploaded.name] = {"text": resume_text, "result": result}
            record_session(uploaded.name, result["overall_score"], result["missing_keywords"])
            st.rerun()

    result = st.session_state.ats_result
    if result:
        score   = result["overall_score"]
        sscores = result["section_scores"]
        ring_color = "#ef4444" if score < 50 else "#f59e0b" if score < 75 else "#10b981"
        status     = "Low — Needs Work ❌" if score < 50 else "Average ⚠️" if score < 75 else "Strong ✅"

        st.divider()
        col1, col2 = st.columns([1,2], gap="large")

        with col1:
            st.markdown(f"""
            <div style="text-align:center;padding:1.5rem;">
                <div style="font-size:0.72rem;color:#8888aa;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">Overall ATS Score</div>
                <div style="display:inline-flex;align-items:center;justify-content:center;width:150px;height:150px;border-radius:50%;border:10px solid {ring_color};font-size:2.8rem;font-weight:700;color:{ring_color};background:rgba(0,0,0,0.2);">{score}%</div>
                <div style="margin-top:12px;font-size:0.9rem;color:{ring_color};font-weight:500;">{status}</div>
            </div>""", unsafe_allow_html=True)
            kw_pct = result["keyword_match_pct"]
            st.markdown(f"""
            <div style="background:#16161f;border:1px solid #2a2a3e;border-radius:10px;padding:1rem;text-align:center;margin-top:0.5rem;">
                <div style="font-size:0.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:0.06em;">Keyword Match</div>
                <div style="font-size:1.8rem;font-weight:700;color:#818cf8;">{kw_pct}%</div>
                <div style="font-size:0.75rem;color:#8888aa;">{len(result["matched_keywords"])} of {len(result["matched_keywords"])+len(result["missing_keywords"])} keywords found</div>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="sec-head">📊 Score Breakdown</div>', unsafe_allow_html=True)
            for key, label, weight in [("skills","Skills Match",0.45),("experience","Experience Match",0.30),("education","Education Match",0.20),("other","Other Keywords",0.05)]:
                s = sscores.get(key, 0)
                bc = "#ef4444" if s < 50 else "#f59e0b" if s < 75 else "#10b981"
                st.markdown(f"""
                <div class="section-bar-wrap">
                    <div class="section-bar-label">
                        <span>{label} <span style="color:#8888aa;font-size:0.72rem;">(weight: {int(weight*100)}%)</span></span>
                        <span style="font-weight:600;color:{bc};">{s}%</span>
                    </div>
                    <div class="section-bar-bg"><div class="section-bar-fill" style="width:{s}%;background:{bc};"></div></div>
                </div>""", unsafe_allow_html=True)

        st.divider()
        col_match, col_miss = st.columns(2, gap="large")
        with col_match:
            matched = result["matched_keywords"]
            st.markdown(f'<div class="sec-head">✅ Matched Keywords ({len(matched)})</div>', unsafe_allow_html=True)
            if matched:
                st.markdown('<div class="chip-row">' + "".join(f'<span class="chip chip-green">{kw}</span>' for kw in matched[:30]) + '</div>', unsafe_allow_html=True)
            else:
                st.info("No keyword matches found.")
        with col_miss:
            missing = result["missing_keywords"]
            st.markdown(f'<div class="sec-head">❌ Missing Keywords ({len(missing)})</div>', unsafe_allow_html=True)
            if missing:
                st.markdown('<div class="chip-row">' + "".join(f'<span class="chip chip-red">{kw}</span>' for kw in missing[:30]) + '</div>', unsafe_allow_html=True)
            else:
                st.success("No missing keywords detected!")

        st.divider()
        st.markdown('<div class="sec-head">✍️ AI Resume Rewriter</div>', unsafe_allow_html=True)
        st.caption("Click below to get AI-rewritten bullet points aligned to the job description.")
        if st.button("🔁 Improve My Resume"):
            with st.spinner("Rewriting with AI..."):
                st.session_state.rewrite_text = rewrite_resume_bullets(
                    st.session_state.resume_text, st.session_state.jd_text, model=st.session_state.llm_model)
        if st.session_state.rewrite_text:
            st.markdown(st.session_state.rewrite_text)

        st.divider()
        st.markdown('<div class="sec-head">📥 Export Report</div>', unsafe_allow_html=True)
        if st.button("📄 Generate PDF Report"):
            with st.spinner("Building PDF..."):
                pdf_bytes = generate_pdf_report(
                    filename=st.session_state.resume_name,
                    overall_score=result["overall_score"],
                    section_scores=result["section_scores"],
                    matched_keywords=result["matched_keywords"],
                    missing_keywords=result["missing_keywords"],
                    rewrite_text=st.session_state.rewrite_text,
                )
            st.download_button("⬇️ Download PDF Report", data=bytes(pdf_bytes),
                file_name=f"HireMind_{st.session_state.resume_name}.pdf", mime="application/pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AI ASSISTANT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💬 AI Assistant":
    st.markdown('<h1 style="font-size:1.8rem;font-weight:700;margin:0 0 0.5rem;">AI Career Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8888aa;margin-bottom:1.5rem;">Ask anything about your resume, job fit, or career growth</p>', unsafe_allow_html=True)

    if not st.session_state.resume_text:
        st.info("📄 Please analyze a resume first from the **Analyzer** tab.")
    else:
        st.markdown(f'<div style="font-size:0.82rem;color:#8888aa;margin-bottom:1rem;">Active resume: <span style="color:#818cf8;">{st.session_state.resume_name}</span></div>', unsafe_allow_html=True)

        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div><div class="chat-label chat-user-label">You</div><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div><div class="chat-label chat-ai-label">HireMind AI</div><div class="chat-ai">{msg["content"].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

        if not st.session_state.chat_history:
            st.markdown('<div class="sec-head">💡 Suggested Questions</div>', unsafe_allow_html=True)
            suggestions = [
                "What skills am I missing for this role?",
                "How can I improve my resume summary?",
                "What experience should I highlight more?",
                "How do I tailor my resume for this job?",
            ]
            c1, c2 = st.columns(2)
            for i, s in enumerate(suggestions):
                with (c1 if i % 2 == 0 else c2):
                    if st.button(f"→ {s}", key=f"sug_{i}", use_container_width=True):
                        _run_chat(s)

        user_input = st.chat_input("Ask about your resume, job fit, career advice...")
        if user_input:
            _run_chat(user_input)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPARE RESUMES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📁 Compare Resumes":
    st.markdown('<h1 style="font-size:1.8rem;font-weight:700;margin:0 0 0.5rem;">Multi-Resume Comparison</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8888aa;margin-bottom:1.5rem;">Upload multiple resumes and compare them side by side</p>', unsafe_allow_html=True)

    col_up, col_jd = st.columns(2, gap="large")
    with col_up:
        st.markdown('<div class="sec-head">📄 Upload Resumes (up to 5)</div>', unsafe_allow_html=True)
        multi_files = st.file_uploader("Resumes", type=["pdf","docx","txt"], accept_multiple_files=True, label_visibility="collapsed")
    with col_jd:
        st.markdown('<div class="sec-head">💼 Job Description</div>', unsafe_allow_html=True)
        compare_jd = st.text_area("JD", height=130, placeholder="Paste JD here...", label_visibility="collapsed", key="compare_jd")

    if st.button("⚡ Compare All Resumes", use_container_width=True):
        if not multi_files:
            st.warning("Please upload at least one resume.")
        elif not compare_jd.strip():
            st.warning("Please enter a job description.")
        else:
            jd_clean = preprocess_text(compare_jd)
            prog = st.progress(0)
            for i, f in enumerate(multi_files[:5]):
                with st.spinner(f"Analyzing {f.name}..."):
                    text   = preprocess_text(extract_text(f))
                    result = compute_ats_score(text, jd_clean)
                    st.session_state.resumes[f.name] = {"text": text, "result": result}
                    record_session(f.name, result["overall_score"], result["missing_keywords"])
                prog.progress((i+1) / min(len(multi_files), 5))
            prog.empty()

    if st.session_state.resumes:
        st.divider()
        st.markdown('<div class="sec-head">📊 Comparison Results</div>', unsafe_allow_html=True)
        sorted_r = sorted(st.session_state.resumes.items(), key=lambda x: x[1]["result"]["overall_score"], reverse=True)
        cols = st.columns(min(len(sorted_r), 3))
        for i, (name, data) in enumerate(sorted_r):
            r = data["result"]
            s = r["overall_score"]
            bc = "#ef4444" if s < 50 else "#f59e0b" if s < 75 else "#10b981"
            rb = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:#16161f;border:1px solid #2a2a3e;border-radius:12px;padding:1.25rem;margin-bottom:1rem;">
                    <div style="font-size:0.78rem;color:#8888aa;">{rb}</div>
                    <div style="font-weight:600;margin-bottom:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{name}">{name}</div>
                    <div style="font-size:2rem;font-weight:700;color:{bc};text-align:center;">{s}%</div>
                    <div style="font-size:0.72rem;color:#8888aa;text-align:center;margin-bottom:10px;">Overall ATS Score</div>
                    <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#8888aa;">
                        <span>Skills: <b style="color:{bc};">{r["section_scores"]["skills"]}%</b></span>
                        <span>Exp: <b style="color:{bc};">{r["section_scores"]["experience"]}%</b></span>
                        <span>Edu: <b style="color:{bc};">{r["section_scores"]["education"]}%</b></span>
                    </div>
                    <div style="margin-top:8px;font-size:0.75rem;color:#8888aa;">✓ {len(r["matched_keywords"])} matched &nbsp;·&nbsp; ✗ {len(r["missing_keywords"])} missing</div>
                </div>""", unsafe_allow_html=True)

        if len(sorted_r) > 1:
            import pandas as pd
            st.markdown('<div class="sec-head">📈 Score Chart</div>', unsafe_allow_html=True)
            df = pd.DataFrame([{"Resume": n[:25], "Skills": d["result"]["section_scores"]["skills"],
                "Experience": d["result"]["section_scores"]["experience"],
                "Education":  d["result"]["section_scores"]["education"],
                "Overall":    d["result"]["overall_score"]} for n, d in sorted_r])
            st.bar_chart(df.set_index("Resume")[["Skills","Experience","Education","Overall"]])


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Analytics":
    analytics = get_analytics()
    st.markdown('<h1 style="font-size:1.8rem;font-weight:700;margin:0 0 0.5rem;">Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8888aa;margin-bottom:1.5rem;">Usage patterns, score trends, and common skill gaps</p>', unsafe_allow_html=True)

    sessions = analytics.get("sessions", [])
    scores   = [s["score"] for s in sessions if s.get("score",-1) > 0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Uploads",     analytics["total_uploads"])
    c2.metric("Average Score",     f"{analytics['avg_score']}%")
    c3.metric("High Scorers 75%+", len([s for s in scores if s >= 75]))
    c4.metric("Low Scorers <50%",  len([s for s in scores if s < 50]))

    st.divider()
    col_miss, col_hist = st.columns(2, gap="large")

    with col_miss:
        st.markdown('<div class="sec-head">🔴 Most Missing Skills</div>', unsafe_allow_html=True)
        top_missing = analytics.get("top_missing_skills", [])
        if top_missing:
            max_c = top_missing[0][1] or 1
            for skill, count in top_missing:
                pct = int((count / max_c) * 100)
                st.markdown(f"""
                <div style="margin:6px 0;">
                    <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:3px;">
                        <span style="color:#e8e8f0;">{skill}</span>
                        <span style="color:#8888aa;font-family:monospace;">{count}x</span>
                    </div>
                    <div style="background:#1e1e2e;border-radius:3px;height:5px;">
                        <div style="background:#ef4444;width:{pct}%;height:100%;border-radius:3px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No data yet — analyze some resumes first.")

    with col_hist:
        st.markdown('<div class="sec-head">📋 Recent Sessions</div>', unsafe_allow_html=True)
        recent = list(reversed(sessions[-10:]))
        if recent:
            import pandas as pd
            df = pd.DataFrame(recent)[["timestamp","filename","score","missing_count"]]
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%m/%d %H:%M")
            df.columns = ["Time","File","Score","Missing"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No sessions yet.")

    if len(scores) >= 3:
        st.divider()
        st.markdown('<div class="sec-head">📈 Score Trend</div>', unsafe_allow_html=True)
        import pandas as pd
        st.line_chart(pd.DataFrame({"Session": range(1, len(scores)+1), "ATS Score": scores}).set_index("Session"))
