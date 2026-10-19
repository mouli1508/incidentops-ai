
from dataclasses import dataclass

from app.ai.llm import generate_answer
from app.knowledge.search import search_knowledge


@dataclass
class RAGResult:
    question: str
    answer: str
    sources: list[dict]
    grounded: bool


def build_context(sources: list[dict]) -> str:
    """
    Format retrieved chunks so the LLM
    can refer to them using source IDs.
    """
    sections = []

    for index, source in enumerate(sources, start=1):
        source_id = f"S{index}"

        sections.append(
            f"[{source_id}]\n"
            f"Document: {source['document_title']}\n"
            f"Source URI: {source['source_uri']}\n"
            f"Chunk: {source['chunk_index']}\n"
            f"Content:\n{source['content']}"
        )

    return "\n\n---\n\n".join(sections)


def ask_knowledge(
    question: str,
    limit: int = 4,
) -> RAGResult:
    """
    Retrieve evidence, then generate an answer.
    """

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty")

    # Step 1: Retrieve relevant chunks.
    sources = search_knowledge(
        query=question,
        limit=limit,
    )

    # Step 2: Don't call the LLM without evidence.
    if not sources:
        return RAGResult(
            question=question,
            answer=(
                "I couldn't find relevant enterprise knowledge "
                "to answer this question."
            ),
            sources=[],
            grounded=False,
        )

    # Step 3: Build the LLM context.
    context = build_context(sources)

    # Step 4: Generate an answer.
    answer = generate_answer(
        question=question,
        context=context,
    )

    # Step 5: Attach source identifiers.
    labeled_sources = []

    for index, source in enumerate(sources, start=1):
        labeled_sources.append(
            {
                "source_id": f"S{index}",
                **source,
            }
        )

    return RAGResult(
        question=question,
        answer=answer,
        sources=labeled_sources,
        grounded=False,  # Not verified yet
    )
