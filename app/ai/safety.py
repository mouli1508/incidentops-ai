import re


# Experimental starting threshold.
# We will measure and adjust it using evaluation data.
MIN_SIMILARITY = 0.40

# Matches source references like [S1], [S2], [S12].
CITATION_PATTERN = re.compile(r"\[S\d+\]")


def filter_relevant_sources(
    sources: list[dict],
    min_similarity: float = MIN_SIMILARITY,
) -> list[dict]:
    """
    Keep only search results above the similarity threshold.
    """

    if not -1.0 <= min_similarity <= 1.0:
        raise ValueError("Invalid similarity threshold")

    return [
        source
        for source in sources
        if source["similarity"] >= min_similarity
    ]


def validate_citations(
    answer: str,
    sources: list[dict],
) -> bool:
    """
    Verify that the answer cites at least one
    existing source and contains no unknown citations.
    
    This checks citation IDs, NOT factual correctness.
    """

    cited_ids = set(CITATION_PATTERN.findall(answer))

    available_ids = {
        f"[{source['source_id']}]"
        for source in sources
    }

    if not cited_ids:
        return False

    return cited_ids.issubset(available_ids)


def abstention_message() -> str:
    return (
        "I couldn't find sufficient enterprise knowledge "
        "to answer this question reliably. "
        "Please consult your IT support team."
    )
