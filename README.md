# Automated Resume Screener — MVP

This repository contains a minimal starter scaffold for an Automated Resume Screener.

What's included:
- `requirements.txt` — Python dependencies for the MVP
- `app.py` — Streamlit app providing an attractive, simple UI to upload resumes and a job description, and perform a mock semantic match
- `resume_parser.py` — a small wrapper with simple parsing helpers (PDF/DOCX text extraction stubs)
- `matcher.py` — embedding and similarity computation stubs using sentence-transformers

How to run (Windows PowerShell):

```powershell
python -m venv .venv
# Activate (PowerShell) - if your system blocks script execution, see notes below
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Notes:
- This is an MVP designed to be extended. The parser/matcher provide a safe keyword-based fallback so the UI runs quickly.
- Embeddings (semantic matching) are optional. To enable embeddings (sentence-transformers) set an environment variable before running the app:

```powershell
$env:RESUME_ENABLE_EMBEDDINGS = '1'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If your machine has limited CPU or you prefer not to install large ML packages locally, keep embeddings disabled and the app will use a fast keyword-based matcher. Alternatively you can integrate a hosted embeddings API (OpenAI, Hugging Face) — see `docs/deployment.md` for notes.

If PowerShell blocks activation scripts, you can avoid changing execution policy by invoking the venv Python directly:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Follow the rest of the docs in the `docs/` directory for architecture, testing, and deployment guidance.
