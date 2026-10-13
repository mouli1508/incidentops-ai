
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import Incident, Ticket
from app.schemas.ticket import TicketResponse


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/{incident_id}/tickets",
    response_model=list[TicketResponse],
)
def get_incident_tickets(
    incident_id: UUID,
    db: DbSession,
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    statement = (
        select(Ticket)
        .where(Ticket.incident_id == incident_id)
        .order_by(Ticket.created_at.desc(), Ticket.id.desc())
        .limit(100)
    )

    return db.scalars(statement).all()
