# Deployment Notes

Prefer simple deployments for the MVP:

Streamlit Cloud:
- Easy for demos. Add a `requirements.txt` and point Streamlit Cloud to this repository.
- If embeddings are required in the cloud, ensure the instance size supports model downloads.

Heroku / Render / Railway:
- Create a `Procfile` and use the venv to install dependencies.
- For heavy ML packages, consider using smaller CPU instances and a separate embeddings service.

Production recommendations:
- Host embeddings in a managed vector DB or use API-based embeddings (OpenAI/Hugging Face).
- Serve a FastAPI backend and use React for a richer frontend if you need more control over UI.
- Add logging, monitoring, and authentication (OAuth2 / JWT).

Environment variables:
- `RESUME_ENABLE_EMBEDDINGS=1` to enable local sentence-transformers embeddings.
- `EMBEDDINGS_PROVIDER=openai|hf` and credentials if using hosted embeddings APIs.

Storage:
- Use a managed database (Postgres) for feedback and metadata. Use S3 (or equivalent) for storing raw resumes.

CI/CD:
- Add unit tests and a GitHub Actions workflow to run tests and linting on PRs.
