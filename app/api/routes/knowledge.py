import logging

from fastapi import APIRouter, HTTPException

from app.ai.rag import ask_knowledge
from app.schemas.knowledge import (
    KnowledgeAskRequest,
    KnowledgeAskResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge AI"],
)


@router.post(
    "/ask",
    response_model=KnowledgeAskResponse,
    summary="Ask enterprise knowledge",
    description=(
        "Search internal knowledge and generate "
        "an AI answer supported by retrieved documents."
    ),
)
def ask_enterprise_knowledge(
    request: KnowledgeAskRequest,
) -> KnowledgeAskResponse:
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty or whitespace.",
        )

    try:
        result = ask_knowledge(
            question=question,
            limit=request.limit,
        )

        return KnowledgeAskResponse(
            question=result.question,
            answer=result.answer,
            sources=result.sources,
            grounded=result.grounded,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception("Knowledge API request failed")

        raise HTTPException(
            status_code=503,
            detail=(
                "Knowledge assistant is temporarily unavailable."
            ),
        )
