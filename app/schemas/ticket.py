
from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


TicketStatusValue = Literal[
    "open",
    "in_progress",
    "resolved",
    "closed",
]


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=1)
    employee_id: UUID
    asset_id: UUID | None = None
    incident_id: UUID | None = None


class TicketUpdate(BaseModel):
    status: TicketStatusValue | None = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    status: str
    employee_id: UUID
    asset_id: UUID | None
    incident_id: UUID | None
    created_at: datetime

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value):
        # SQLAlchemy may return a Python Enum instance.
        if isinstance(value, Enum):
            return value.value
        return value
