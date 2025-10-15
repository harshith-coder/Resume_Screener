import re


def highlight_text(text, keywords, mark_style="background-color: #ffd7a3; color: #0f1724; padding: 0 3px; border-radius: 3px;"):
    """Return HTML-safe text with keywords wrapped in a styled <span> for highlighting.

    - text: the source string
    - keywords: iterable of keywords (lowercased recommended)
    - mark_style: inline CSS for the highlighted span
    """
    if not text or not keywords:
        return text or ""

    # build regex to match whole words (case-insensitive)
    kw_escaped = [re.escape(k) for k in set([k for k in keywords if k])]
    if not kw_escaped:
        return text
    pattern = r"\b(" + "|".join(kw_escaped) + r")\b"

    def _repl(m):
        return f"<span style='{mark_style}'>" + m.group(0) + "</span>"

    try:
        return re.sub(pattern, _repl, text, flags=re.IGNORECASE)
    except Exception:
        return text


def extract_snippets(text, keywords, max_snippets=2, chars_each_side=60):
    """Find up to max_snippets fragments that contain keywords. Return list of snippets.

    If no keywords are found, return the first few sentences.
    """
    if not text:
        return []

    # split into sentences (simple)
    sentences = re.split(r'(?<=[\\.!?])\s+', text)
    hits = []
    kws = set([k.lower() for k in keywords if k])
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in kws):
            hits.append(s.strip())
        if len(hits) >= max_snippets:
            break

    if not hits:
        # fallback: first N sentences
        hits = [s.strip() for s in sentences[:max_snippets]]

    # crop snippets to chars_each_side around first keyword occurrence
    cropped = []
    for s in hits:
        idx = 0
        for kw in kws:
            i = s.lower().find(kw)
            if i >= 0:
                idx = i
                break
        start = max(0, idx - chars_each_side)
        end = min(len(s), idx + chars_each_side)
        prefix = '...' if start > 0 else ''
        suffix = '...' if end < len(s) else ''
        cropped.append(prefix + s[start:end].strip() + suffix)

    return cropped
