# Deploying to Heroku

1. Create a Heroku app.
2. Add a `Procfile` (already present in this repo):

```
web: streamlit run app.py --server.port $PORT
```

3. Ensure `requirements.txt` is up to date.
4. Push to Heroku remote. Set config vars for `RESUME_ENABLE_EMBEDDINGS` and any API keys.

Notes:
- Heroku's free tier may not be suitable for large model downloads; consider hosted embeddings or a separate embeddings service.
- Use a managed DB for feedback if you need persistence beyond the ephemeral filesystem.
