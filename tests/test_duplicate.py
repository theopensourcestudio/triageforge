from triageforge.duplicate import cosine_similarity, find_duplicates


def test_similarity_finds_related_text() -> None:
    score = cosine_similarity("CLI crashes on Windows startup", "Windows CLI crash during startup")
    assert score > 0.5


def test_duplicate_candidates_are_sorted() -> None:
    issues = [
        {"number": 1, "title": "Docs typo", "body": "small typo"},
        {"number": 2, "title": "CLI crashes on Windows", "body": "startup exception"},
    ]
    matches = find_duplicates("Windows CLI startup crash", "exception shown", issues, threshold=0.1)
    assert matches[0].number == 2
