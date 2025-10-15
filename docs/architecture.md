# Architecture Overview

This project is a modular MVP for an automated resume screener. Key components:

- `app.py` - Streamlit frontend, handles file uploads, JD input, scoring controls, candidate cards, and feedback UI.
- `resume_parser.py` - Resume text extraction and optional structured parsing (pyresparser). Supports PDF, DOCX, TXT. Includes OCR fallback via `pytesseract` + `pdf2image`.
- `matcher.py` - Matching logic. By default uses a keyword-overlap heuristic. Optionally (via `RESUME_ENABLE_EMBEDDINGS=1`) uses `sentence-transformers` for semantic embeddings and cosine similarity.
- `ui_helpers.py` - Small helpers for highlighting keywords and extracting snippets for explainability.
- `feedback.py` - Simple SQLite-backed feedback storage and retrieval at `data/feedback.db`.
- `test_smoke.py` - Local smoke test to validate parser, matcher, and feedback.

Data flow:
1. Recruiter pastes a job description and uploads resumes.
2. `resume_parser` extracts text and meta fields.
3. `matcher` computes a match score (embedding + keyword weighted) and returns top keywords.
4. Frontend displays cards with highlighted snippets and allows recruiters to submit feedback.
5. Feedback is persisted and shown in the sidebar.

Scaling notes and production
- For larger scale, store embeddings in a vector DB (FAISS, Milvus, or Chroma) and serve a backend API (FastAPI) with worker processes for extraction/embedding.
- Use background workers (Celery/RQ) to process uploaded resumes and compute embeddings asynchronously.
- Add authentication, RBAC, and audit logs before production use.

Security & Privacy
- Treat uploaded resumes as sensitive PII. Store only when necessary and follow data retention policies.
- Consider redacting PII and encrypting storage at rest.
