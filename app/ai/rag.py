
from dataclasses import dataclass

from app.ai.llm import generate_answer
from app.ai.safety import (
    abstention_message,
    filter_relevant_sources,
    validate_citations,
)
from app.knowledge.search import search_knowledge


MAX_CONTEXT_CHARS_PER_SOURCE = 3000


@dataclass
class RAGResult:
    question: str
    answer: str
    sources: list[dict]
    grounded: bool


def build_context(sources: list[dict]) -> str:
    """
    Format evidence for the language model.
    """
    sections = []

    for index, source in enumerate(sources, start=1):
        source_id = f"S{index}"

        content = source["content"][
            :MAX_CONTEXT_CHARS_PER_SOURCE
        ]

        sections.append(
            f"[{source_id}]\n"
            f"Document: {source['document_title']}\n"
            f"Source URI: {source['source_uri']}\n"
            f"Chunk: {source['chunk_index']}\n"
            f"Content:\n{content}"
        )

    return "\n\n---\n\n".join(sections)


def ask_knowledge(
    question: str,
    limit: int = 4,
) -> RAGResult:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty")

    if not 1 <= limit <= 20:
        raise ValueError("Limit must be between 1 and 20")

    # 1. Retrieve knowledge
    retrieved = search_knowledge(
        query=question,
        limit=limit,
    )

    # 2. Filter low-similarity evidence
    sources = filter_relevant_sources(retrieved)

    if not sources:
        return RAGResult(
            question=question,
            answer=abstention_message(),
            sources=[],
            grounded=False,
        )

    # 3. Assign stable source identifiers
    labeled_sources = [
        {"source_id": f"S{i}", **source}
        for i, source in enumerate(sources, start=1)
    ]

    # 4. Prepare context
    context = build_context(labeled_sources)

    # 5. Generate answer
    answer = generate_answer(
        question=question,
        context=context,
    )

    # 6. Validate source references
    citations_valid = validate_citations(
        answer,
        labeled_sources,
    )

    if not citations_valid:
        return RAGResult(
            question=question,
            answer=(
                "I couldn't verify the source references "
                "in the generated answer. "
                "Please consult the retrieved documents "
                "or try rephrasing your question."
            ),
            sources=labeled_sources,
            grounded=False,
        )

    return RAGResult(
        question=question,
        answer=answer,
        sources=labeled_sources,
        grounded=False,
    )
