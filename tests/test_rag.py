
from unittest.mock import patch

import pytest

from app.ai.rag import ask_knowledge, build_context


SAMPLE_SOURCE = {
    "document_title": "VPN Troubleshooting",
    "source_uri": "knowledge://runbooks/vpn.md",
    "chunk_index": 0,
    "content": "Check the VPN gateway status.",
    "similarity": 0.85,
}


def test_build_context():
    context = build_context([SAMPLE_SOURCE])

    assert "[S1]" in context
    assert "VPN Troubleshooting" in context
    assert "Check the VPN gateway status." in context


def test_rag_returns_answer_and_sources():
    with (
        patch(
            "app.ai.rag.search_knowledge",
            return_value=[SAMPLE_SOURCE],
        ) as search_mock,
        patch(
            "app.ai.rag.generate_answer",
            return_value="Check the VPN gateway. [S1]",
        ) as llm_mock,
    ):
        result = ask_knowledge(
            "Why is my VPN failing?"
        )

    assert result.answer == "Check the VPN gateway. [S1]"
    assert len(result.sources) == 1
    assert result.sources[0]["source_id"] == "S1"
    assert result.grounded is False

    search_mock.assert_called_once()
    llm_mock.assert_called_once()


def test_no_sources_skips_llm():
    with (
        patch(
            "app.ai.rag.search_knowledge",
            return_value=[],
        ),
        patch("app.ai.rag.generate_answer") as llm_mock,
    ):
        result = ask_knowledge(
            "How do I fix an unknown issue?"
        )

    assert result.sources == []
    assert result.grounded is False
    assert "couldn't find" in result.answer.lower()

    llm_mock.assert_not_called()


def test_empty_question():
    with pytest.raises(ValueError):
        ask_knowledge("   ")


def test_retrieval_failure_propagates():
    with patch(
        "app.ai.rag.search_knowledge",
        side_effect=RuntimeError("Database unavailable"),
    ):
        with pytest.raises(
            RuntimeError,
            match="Database unavailable",
        ):
            ask_knowledge("VPN is not working")


def test_source_identifiers():
    context = build_context([
        SAMPLE_SOURCE,
        {**SAMPLE_SOURCE, "chunk_index": 1},
    ])

    assert "[S1]" in context
    assert "[S2]" in context
