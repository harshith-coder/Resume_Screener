import streamlit as st
from matcher import match_with_weights
from resume_parser import extract_text_from_file
from ui_helpers import highlight_text, extract_snippets
from feedback import save_feedback, list_feedback

st.set_page_config(page_title="Resume Screener MVP", page_icon="📄", layout="centered")

# Theme-like colors (inspired by modern food-delivery apps)
PRIMARY = "#ff6f00"  # orange
SECONDARY = "#ffffff"  # white
BG = "#0f1724"  # dark navy
CARD = "#0b1220"

st.markdown(f"<style>body {{background-color: {BG}; color: {SECONDARY};}} .stButton>button {{background-color: {PRIMARY};}}</style>", unsafe_allow_html=True)

st.title("Automated Resume Screener — MVP")
st.write("Upload resumes and a job description to get semantic match scores.")

with st.expander("Upload inputs", expanded=True):
    jd_text = st.text_area("Paste job description (or key skills):", height=150)
    uploaded_files = st.file_uploader("Upload one or more resumes (PDF/DOCX/TXT)", accept_multiple_files=True)

# Weight controls
st.sidebar.header("Scoring weights")
weight_embedding = st.sidebar.slider("Embedding weight", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
weight_keywords = st.sidebar.slider("Keyword weight", min_value=0.0, max_value=1.0, value=0.3, step=0.05)

if st.button("Run Screening"):
    if not jd_text.strip():
        st.error("Please provide a job description or skills.")
    elif not uploaded_files:
        st.error("Please upload at least one resume file.")
    else:
        results = []
        for f in uploaded_files:
            parsed = extract_text_from_file(f)
            score, details = match_with_weights(jd_text, parsed, weight_embedding=weight_embedding, weight_keywords=weight_keywords)
            results.append((f.name, score, details, parsed))

        # Display results in card-like layout
        st.subheader("Results")
        cols = st.columns(2)
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        # CSV export
        import pandas as _pd
        df_rows = []
        for name, score, details, parsed in sorted_results:
            df_rows.append({'candidate': name, 'score': float(score), 'top_keywords': ','.join(details.get('top_keywords', [])[:10])})
        if df_rows:
            df = _pd.DataFrame(df_rows)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download results CSV", data=csv, file_name='screening_results.csv', mime='text/csv')

        for idx, (name, score, details, parsed) in enumerate(sorted_results):
            col = cols[idx % 2]
            with col:
                st.markdown(f"<div style='background:{CARD}; padding:12px; border-radius:10px; margin-bottom:10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color:{SECONDARY}; margin:0 0 6px 0;'>{name} - {score*100:.1f}%</h3>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:{SECONDARY}; opacity:0.9; font-size:14px;'>Top keywords: {', '.join(details.get('top_keywords', [])[:10])}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top:8px; color:{SECONDARY};'>Skill similarity: {details.get('skill_sim', 0):.3f} &nbsp; | &nbsp; Experience similarity: {details.get('exp_sim', 0):.3f}</div>", unsafe_allow_html=True)

                # show highlighted snippets
                snippets = extract_snippets(parsed.get('text', ''), details.get('top_keywords', [])[:8])
                for s in snippets:
                    highlighted = highlight_text(s, details.get('top_keywords', [])[:8])
                    st.markdown(f"<div style='margin-top:8px; background:transparent; padding:6px; color:{SECONDARY};'>" + highlighted + "</div>", unsafe_allow_html=True)

                # small meta listing
                if parsed.get('meta'):
                    metas = parsed['meta']
                    meta_lines = []
                    for k, v in metas.items():
                        if isinstance(v, (list, tuple)):
                            meta_lines.append(f"{k}: {', '.join([str(x) for x in v][:5])}")
                        else:
                            meta_lines.append(f"{k}: {str(v)[:120]}")
                    st.markdown(f"<div style='color:{SECONDARY}; opacity:0.8; margin-top:8px; font-size:12px;'>{'<br>'.join(meta_lines)}</div>", unsafe_allow_html=True)

                # explainability / rationale (nearest JD sentences)
                try:
                    from matcher import explain_match
                    rationale = explain_match(jd_text, parsed, top_k=3)
                    if rationale:
                        st.markdown(f"<div style='margin-top:8px; color:{SECONDARY};'><b>Rationale (top snippets):</b></div>", unsafe_allow_html=True)
                        for r in rationale:
                            left = highlight_text(r.get('resume_sentence',''), details.get('top_keywords', [])[:8])
                            right = r.get('best_jd_sentence','') or ''
                            st.markdown(f"<div style='margin-top:6px; color:{SECONDARY}; font-size:13px;'><b>Resume:</b> {left}<br/><b>JD:</b> {right}<br/><i>score: {r.get('score',0):.3f}</i></div>", unsafe_allow_html=True)
                except Exception:
                    pass

                st.markdown("</div>", unsafe_allow_html=True)

                # feedback form
                with st.form(key=f"fb_{idx}"):
                    st.write("Give feedback for this candidate:")
                    rating = st.slider("Rating (1-5)", min_value=1, max_value=5, value=4, key=f"r_{idx}")
                    comments = st.text_area("Comments (optional)", key=f"c_{idx}")
                    submitted = st.form_submit_button("Submit feedback")
                    if submitted:
                        save_feedback(name, jd_text, rating, comments)
                        st.success("Feedback saved")

st.sidebar.header("About")
st.sidebar.write("This MVP demonstrates core ideas: parsing, embedding-based matching, and an attractive UI. Extend with bias checks, explainability, and deployment.")

st.sidebar.header("Recent feedback")
for ts, cand, jd, rating, comments in list_feedback(10):
    st.sidebar.markdown(f"**{cand}** — {rating}/5 — {ts.split('T')[0]}")
    if comments:
        st.sidebar.markdown(f"_{comments[:120]}_")
