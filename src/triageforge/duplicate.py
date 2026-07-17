from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable
from typing import Any

from .models import DuplicateCandidate

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "when",
    "with",
    "you",
    "your",
}


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9][a-z0-9_.-]+", text.lower())
    return [token for token in tokens if token not in _STOP_WORDS and len(token) > 1]


def cosine_similarity(left: str, right: str) -> float:
    a = Counter(tokenize(left))
    b = Counter(tokenize(right))
    if not a or not b:
        return 0.0
    dot = sum(count * b.get(token, 0) for token, count in a.items())
    norm_a = math.sqrt(sum(count * count for count in a.values()))
    norm_b = math.sqrt(sum(count * count for count in b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def find_duplicates(
    title: str,
    body: str,
    existing_issues: Iterable[dict[str, Any]],
    *,
    threshold: float = 0.30,
    limit: int = 5,
) -> list[DuplicateCandidate]:
    query = f"{title}\n{body}"
    candidates: list[DuplicateCandidate] = []
    for issue in existing_issues:
        candidate_text = f"{issue.get('title', '')}\n{issue.get('body', '')}"
        similarity = cosine_similarity(query, candidate_text)
        if similarity >= threshold:
            number_value = issue.get("number")
            candidates.append(
                DuplicateCandidate(
                    number=int(number_value) if number_value is not None else None,
                    title=str(issue.get("title", "Untitled issue")),
                    similarity=round(similarity, 3),
                    url=str(issue["url"]) if issue.get("url") else None,
                )
            )
    return sorted(candidates, key=lambda item: item.similarity, reverse=True)[:limit]
