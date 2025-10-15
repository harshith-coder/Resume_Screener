# Deploying to Render

1. Create a new Web Service on Render and connect your GitHub repository.
2. Use `python` environment. Set the start command to:

```
./.venv/Scripts/python.exe -m streamlit run app.py --server.port $PORT
```

or (Render Linux) replace with the linux venv path:

```
./.venv/bin/python -m streamlit run app.py --server.port $PORT
```

3. Add environment variables (`RESUME_ENABLE_EMBEDDINGS`, provider keys) as needed.
4. For heavy ML packages consider using Render's larger plans or using hosted embeddings.
