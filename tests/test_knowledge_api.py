
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.ai.rag import RAGResult


client = TestClient(app)

ENDPOINT = "/api/v1/knowledge/ask"


def sample_rag_result():
    return RAGResult(
        question="How do I fix VPN error 809?",
        answer="Check the VPN gateway. [S1]",
        sources=[
            {
                "source_id": "S1",
                "document_title": "VPN Troubleshooting",
                "source_uri": "knowledge://runbooks/vpn.md",
                "chunk_index": 0,
                "content": "Check the VPN gateway.",
                "similarity": 0.85,
            }
        ],
        grounded=False,
    )


def test_knowledge_endpoint_success():
    with patch(
        "app.api.routes.knowledge.ask_knowledge",
        return_value=sample_rag_result(),
    ) as rag_mock:
        response = client.post(
            ENDPOINT,
            json={
                "question": "How do I fix VPN error 809?",
                "limit": 4,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Check the VPN gateway. [S1]"
    assert data["grounded"] is False
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source_id"] == "S1"

    rag_mock.assert_called_once_with(
        question="How do I fix VPN error 809?",
        limit=4,
    )


def test_missing_question():
    response = client.post(
        ENDPOINT,
        json={"limit": 4},
    )

    assert response.status_code == 422


def test_empty_question():
    response = client.post(
        ENDPOINT,
        json={
            "question": "   ",
            "limit": 4,
        },
    )

    assert response.status_code == 422


def test_invalid_limit():
    response = client.post(
        ENDPOINT,
        json={
            "question": "VPN not working",
            "limit": 100,
        },
    )

    assert response.status_code == 422


def test_invalid_question_type():
    response = client.post(
        ENDPOINT,
        json={
            "question": 12345,
            "limit": 4,
        },
    )

    assert response.status_code == 422


def test_rag_service_failure():
    with patch(
        "app.api.routes.knowledge.ask_knowledge",
        side_effect=RuntimeError("LLM unavailable"),
    ):
        response = client.post(
            ENDPOINT,
            json={
                "question": "VPN is not working",
            },
        )

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "Knowledge assistant is temporarily unavailable."
    )


def test_no_sources():
    empty_result = RAGResult(
        question="Unknown issue",
        answer="I couldn't find relevant enterprise knowledge.",
        sources=[],
        grounded=False,
    )

    with patch(
        "app.api.routes.knowledge.ask_knowledge",
        return_value=empty_result,
    ):
        response = client.post(
            ENDPOINT,
            json={"question": "Unknown issue"},
        )

    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert response.json()["grounded"] is False
