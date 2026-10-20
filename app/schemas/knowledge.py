
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeAskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="IT support question",
    )

    limit: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Maximum knowledge chunks to retrieve",
    )


class KnowledgeSource(BaseModel):
    source_id: str
    document_title: str
    source_uri: str
    chunk_index: int
    content: str
    similarity: float


class KnowledgeAskResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    question: str
    answer: str
    sources: list[KnowledgeSource]
    grounded: bool
