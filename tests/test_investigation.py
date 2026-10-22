from uuid import uuid4
from unittest.mock import patch

import pytest

from app.ai.rag import RAGResult
from app.investigation.context import TicketContext
from app.investigation.service import (
    build_investigation_question,
    investigate_ticket,
)


TICKET_ID = uuid4()


def sample_context():
    return TicketContext(
        ticket_id=str(TICKET_ID),
        title="VPN Connection Failure",
        description="VPN error 809 after authentication",
        status="open",
        employee_department="Finance",
        asset_hostname="LAPTOP-1042",
        asset_type="laptop",
        incident_id=None,
        incident_title=None,
        incident_severity=None,
        incident_status=None,
    )


def sample_rag_result():
    return RAGResult(
        question="Investigate VPN connection failure",
        answer="Check VPN gateway health. [S1]",
        sources=[
            {
                "source_id": "S1",
                "document_title": "VPN Troubleshooting",
                "source_uri": "knowledge://runbooks/vpn.md",
                "chunk_index": 0,
                "content": "Check VPN gateway health.",
                "similarity": 0.85,
            }
        ],
        grounded=False,
    )


def test_investigation_question():
    question = build_investigation_question(
        sample_context()
    )

    assert "VPN Connection Failure" in question
    assert "VPN error 809" in question
    assert "LAPTOP-1042" in question
    assert "Finance" in question


def test_missing_optional_relationships():
    question = build_investigation_question(
        sample_context()
    )

    assert "Related incident: None" in question
    assert "Incident severity: Unknown" in question


def test_investigation_success():
    with (
        patch(
            "app.investigation.service.get_ticket_context",
            return_value=sample_context(),
        ),
        patch(
            "app.investigation.service.ask_knowledge",
            return_value=sample_rag_result(),
        ) as rag_mock,
    ):
        result = investigate_ticket(TICKET_ID)

    assert result.ticket_id == str(TICKET_ID)
    assert result.status == "draft"
    assert result.grounded is False
    assert len(result.sources) == 1
    assert "[S1]" in result.summary
    rag_mock.assert_called_once()


def test_ticket_not_found():
    with patch(
        "app.investigation.service.get_ticket_context",
        return_value=None,
    ):
        with pytest.raises(LookupError):
            investigate_ticket(TICKET_ID)


def test_insufficient_evidence():
    empty_result = RAGResult(
        question="Unknown issue",
        answer="Insufficient enterprise knowledge.",
        sources=[],
        grounded=False,
    )

    with (
        patch(
            "app.investigation.service.get_ticket_context",
            return_value=sample_context(),
        ),
        patch(
            "app.investigation.service.ask_knowledge",
            return_value=empty_result,
        ),
    ):
        result = investigate_ticket(TICKET_ID)

    assert result.status == "insufficient_evidence"
    assert result.sources == []


def test_llm_failure_propagates():
    with (
        patch(
            "app.investigation.service.get_ticket_context",
            return_value=sample_context(),
        ),
        patch(
            "app.investigation.service.ask_knowledge",
            side_effect=RuntimeError("LLM unavailable"),
        ),
    ):
        with pytest.raises(RuntimeError):
            investigate_ticket(TICKET_ID)
