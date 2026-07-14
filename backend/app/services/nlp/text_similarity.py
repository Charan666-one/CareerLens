"""
TF-IDF textual similarity between a query document (resume text) and a
batch of corpus documents (role/skill descriptions).

Pure function, no DB dependency - the caller is responsible for assembling
the corpus (see app/services/nlp/job_corpus.py) so this module can stay
unit-testable with plain strings.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def similarity_scores(query_text: str, corpus_texts: list[str]) -> list[float]:
    """
    Fit one TF-IDF vectorizer over [query_text] + corpus_texts, then return
    the cosine similarity of the query against each corpus document, in the
    same order as corpus_texts.

    A completely blank batch (query and every corpus entry empty/whitespace)
    raises ValueError("empty vocabulary") in scikit-learn - that's treated
    as "no signal" and mapped to all zeros rather than propagating.
    """
    if not corpus_texts:
        return []

    documents = [query_text or ""] + [text or "" for text in corpus_texts]

    try:
        # No stop_words filtering: these documents are short (job/skill
        # descriptions), so aggressive stopword removal only raises the
        # risk of an empty vocabulary for no real benefit at this scale.
        matrix = TfidfVectorizer().fit_transform(documents)
    except ValueError:
        return [0.0] * len(corpus_texts)

    query_vector = matrix[0:1]
    corpus_vectors = matrix[1:]
    return cosine_similarity(query_vector, corpus_vectors).ravel().tolist()
