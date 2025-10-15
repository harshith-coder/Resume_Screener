# Deploying to Streamlit Cloud

1. Push this repository to a GitHub repo.
2. Log in to https://share.streamlit.io and click "New app".
3. Select your GitHub repo, branch (e.g., main) and `app.py` as the file to run.
4. Ensure `requirements.txt` includes all runtime packages. If you plan to enable embeddings on Streamlit Cloud, add `sentence-transformers` but be mindful of the instance size.
5. Set environment variables in the Streamlit Cloud app settings:
   - `RESUME_ENABLE_EMBEDDINGS=1` (optional)
   - any provider keys if using hosted embeddings (e.g., `OPENAI_API_KEY`)
6. Deploy and open the app URL.

Notes:
- Streamlit Cloud is easiest for demos. If model downloads time out, consider pre-loading embeddings or using hosted embeddings.
