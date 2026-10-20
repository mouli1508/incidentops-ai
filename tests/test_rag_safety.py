from unittest.mock import patch

from app.ai.rag import ask_knowledge
from app.ai.safety import (
    filter_relevant_sources,
    validate_citations,
)


SAMPLE_SOURCE = {
    "document_title": "VPN Troubleshooting",
    "source_uri": "knowledge://runbooks/vpn.md",
    "chunk_index": 0,
    "content": "Check the VPN gateway status.",
    "similarity": 0.85,
}


def test_relevant_source_is_kept():
    result = filter_relevant_sources(
        [SAMPLE_SOURCE]
    )

    assert len(result) == 1


def test_irrelevant_source_is_rejected():
    source = {
        **SAMPLE_SOURCE,
        "similarity": 0.15,
    }

    result = filter_relevant_sources([source])

    assert result == []


def test_valid_citation():
    sources = [
        {"source_id": "S1"}
    ]

    answer = "Check the gateway. [S1]"

    assert validate_citations(answer, sources)


def test_invalid_citation():
    sources = [
        {"source_id": "S1"}
    ]

    answer = "Check the gateway. [S9]"

    assert not validate_citations(answer, sources)


def test_missing_citation():
    sources = [
        {"source_id": "S1"}
    ]

    answer = "Check the gateway."

    assert not validate_citations(answer, sources)


def test_low_relevance_skips_llm():
    irrelevant = {
        **SAMPLE_SOURCE,
        "similarity": 0.10,
    }

    with (
        patch(
            "app.ai.rag.search_knowledge",
            return_value=[irrelevant],
        ),
        patch("app.ai.rag.generate_answer") as llm,
    ):
        result = ask_knowledge(
            "What is the Wi-Fi password?"
        )

    assert result.sources == []
    assert result.grounded is False
    assert "couldn't find" in result.answer.lower()

    llm.assert_not_called()


def test_invalid_generated_citation_is_rejected():
    with (
        patch(
            "app.ai.rag.search_knowledge",
            return_value=[SAMPLE_SOURCE],
        ),
        patch(
            "app.ai.rag.generate_answer",
            return_value="Check the gateway. [S99]",
        ),
    ):
        result = ask_knowledge(
            "Why is my VPN failing?"
        )

    assert result.grounded is False
    assert "couldn't verify" in result.answer.lower()
    assert len(result.sources) == 1


def test_valid_generated_citation():
    with (
        patch(
            "app.ai.rag.search_knowledge",
            return_value=[SAMPLE_SOURCE],
        ),
        patch(
            "app.ai.rag.generate_answer",
            return_value="Check the VPN gateway. [S1]",
        ),
    ):
        result = ask_knowledge(
            "Why is my VPN failing?"
        )

    assert result.answer == "Check the VPN gateway. [S1]"
    assert len(result.sources) == 1
    assert result.grounded is False


def test_multiple_citations():
    sources = [
        {"source_id": "S1"},
        {"source_id": "S2"},
    ]

    answer = (
        "Check connectivity. [S1] "
        "Then inspect the firewall. [S2]"
    )

    assert validate_citations(answer, sources)
