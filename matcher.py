import importlib
import os
import re
import numpy as np

# Control whether to enable embeddings via environment variable to avoid heavy imports by default
_ENABLE_EMBEDDINGS = os.environ.get('RESUME_ENABLE_EMBEDDINGS', '0') in ('1', 'true', 'True')

# Lazy-load model to keep startup quick during development
_model = None
_HAS_ST = False


def _get_model():
    """Lazily import sentence-transformers and return a model instance.

    Raises RuntimeError if embeddings are not enabled or import fails.
    """
    global _model, _HAS_ST
    if not _ENABLE_EMBEDDINGS:
        raise RuntimeError('Embeddings disabled via RESUME_ENABLE_EMBEDDINGS')

    if _model is None:
        try:
            st_mod = importlib.import_module('sentence_transformers')
            SentenceTransformer = getattr(st_mod, 'SentenceTransformer')
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            _HAS_ST = True
        except Exception as e:
            _HAS_ST = False
            raise
    return _model


def _cosine_sim(a, b):
    """Compute cosine similarity between two 1D numpy arrays."""
    a = np.asarray(a)
    b = np.asarray(b)
    if a.size == 0 or b.size == 0:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def extract_keywords(text, top_k=20):
    # very simple keyword extraction: return frequent words excluding stopwords
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.+-]{1,}\b", (text or '').lower())
    stop = set(["the", "and", "for", "with", "a", "an", "to", "in", "on", "of", "is", "are", "as", "by", "from"])
    freq = {}
    for w in words:
        if w in stop or len(w) < 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in items[:top_k]]


def match_with_weights(jd_text, resume_input, weight_embedding=0.7, weight_keywords=0.3):
    """Compute a weighted match score between a job description and a resume.

    resume_input can be either a plain text string or the dict {'text':..., 'meta':...} returned by `extract_text_from_file`.

    Returns: (final_score, details_dict)
    """
    if isinstance(resume_input, dict):
        resume_text = resume_input.get('text', '')
        resume_meta = resume_input.get('meta', {})
    else:
        resume_text = resume_input or ''
        resume_meta = {}

    emb_sim = 0.0
    emb_fallback = False
    if _ENABLE_EMBEDDINGS:
        try:
            model = _get_model()
            jd_emb = model.encode([jd_text])[0]
            res_emb = model.encode([resume_text])[0]
            emb_sim = _cosine_sim(jd_emb, res_emb)
        except Exception:
            emb_fallback = True
            emb_sim = 0.0
    else:
        emb_fallback = True
        emb_sim = 0.0

    # Keyword-based score using either meta.skills (if present) or extracted keywords
    jd_keywords = extract_keywords(jd_text, top_k=40)
    if resume_meta and isinstance(resume_meta.get('skills'), (list, tuple)) and len(resume_meta.get('skills')) > 0:
        res_keywords = [s.lower() for s in resume_meta.get('skills')]
    else:
        res_keywords = extract_keywords(resume_text, top_k=120)

    overlap = len(set(jd_keywords) & set(res_keywords))
    kw_score = overlap / max(1, len(jd_keywords))

    final = weight_embedding * emb_sim + weight_keywords * kw_score
    final = max(0.0, min(1.0, final))

    details = {
        'skill_sim': kw_score,
        'exp_sim': emb_sim,
        'top_keywords': [k for k in res_keywords if k in jd_keywords],
        'emb_fallback': emb_fallback,
        'meta': resume_meta
    }
    return final, details


def explain_match(jd_text, resume_input, top_k=3):
    """Return explainability mapping between resume sentences and JD sentences.

    Returns a list of dicts: { 'resume_sentence', 'best_jd_sentence', 'score' }
    """
    if isinstance(resume_input, dict):
        resume_text = resume_input.get('text', '')
    else:
        resume_text = resume_input or ''

    # Simple sentence split
    jd_sents = [s.strip() for s in re.split(r'(?<=[\.!?])\s+', jd_text) if s.strip()]
    res_sents = [s.strip() for s in re.split(r'(?<=[\.!?])\s+', resume_text) if s.strip()]

    results = []

    # Try embedding-based nearest neighbor if enabled
    if _ENABLE_EMBEDDINGS:
        try:
            model = _get_model()
            if jd_sents and res_sents:
                jd_embs = model.encode(jd_sents)
                res_embs = model.encode(res_sents)
                for r_idx, r_emb in enumerate(res_embs):
                    sims = [ _cosine_sim(r_emb, j_emb) for j_emb in jd_embs ]
                    best_i = int(np.argmax(sims))
                    results.append({'resume_sentence': res_sents[r_idx], 'best_jd_sentence': jd_sents[best_i], 'score': float(sims[best_i])})
            # sort by score and return top_k
            results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
            return results
        except Exception:
            # fall back to keyword overlap
            pass

    # Keyword-overlap fallback: score each resume sentence by overlap with JD keywords
    jd_keywords = set(extract_keywords(jd_text, top_k=60))
    for s in res_sents:
        words = set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.+-]{1,}\b", s.lower()))
        overlap = len(words & jd_keywords)
        score = overlap / max(1, len(jd_keywords))
        results.append({'resume_sentence': s, 'best_jd_sentence': '', 'score': float(score)})

    results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
    return results
