from app.services.nlp.text_similarity import similarity_scores


def test_identical_text_scores_near_one():
    text = "Build and maintain REST APIs and backend services with Python and FastAPI."
    scores = similarity_scores(text, [text])
    assert scores[0] > 0.99


def test_unrelated_text_scores_lower_than_similar_text():
    query = "Build and maintain REST APIs and backend services with Python and FastAPI."
    similar = "Design and build backend REST APIs using Python and FastAPI."
    unrelated = "Paint watercolor landscapes and sell them at the farmers market."

    scores = similarity_scores(query, [similar, unrelated])

    assert scores[0] > scores[1]


def test_index_offset_query_compared_against_corpus_not_itself():
    # A naive off-by-one bug would compare the query against itself
    # (always ~1.0) instead of against corpus_texts[0].
    query = "react typescript frontend web applications"
    close = "Build user-facing web applications with React and TypeScript."
    far = "Operate industrial manufacturing equipment on a factory floor."

    scores = similarity_scores(query, [far, close])

    assert scores[1] > scores[0]


def test_empty_corpus_returns_empty_list():
    assert similarity_scores("anything", []) == []


def test_all_blank_batch_returns_zeros_not_raises():
    # scikit-learn's TfidfVectorizer raises ValueError("empty vocabulary")
    # when every document in the batch is blank - similarity_scores must
    # catch that and degrade to "no signal" rather than propagating.
    scores = similarity_scores("", ["", "   "])
    assert scores == [0.0, 0.0]


def test_single_blank_corpus_entry_among_nonblank_scores_zero():
    query = "python fastapi backend"
    scores = similarity_scores(query, ["Backend Python FastAPI services.", ""])
    assert scores[0] > 0.0
    assert scores[1] == 0.0
