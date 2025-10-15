import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from matcher import match_with_weights, explain_match


def test_keyword_match():
    jd = "Python developer with pandas and REST API experience"
    resume = {'text': 'Experience in Python, pandas and building REST APIs', 'meta': {}}
    score, details = match_with_weights(jd, resume, weight_embedding=0.0, weight_keywords=1.0)
    assert score > 0.5
    assert 'python' in details['top_keywords']


def test_explain_match():
    jd = 'Looking for ML engineer experienced with NLP and transformers.'
    resume = {'text': 'Built NLP pipelines and used transformers for classification.'}
    rationale = explain_match(jd, resume, top_k=1)
    assert isinstance(rationale, list)
    assert len(rationale) == 1