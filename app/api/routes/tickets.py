
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import Asset, Employee, Incident, Ticket
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketStatusValue,
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(payload: TicketCreate, db: DbSession):

    # An employee must exist before we create their ticket.
    if db.get(Employee, payload.employee_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    # Optional asset and incident IDs must also be valid.
    if (
        payload.asset_id is not None
        and db.get(Asset, payload.asset_id) is None
    ):
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    if (
        payload.incident_id is not None
        and db.get(Incident, payload.incident_id) is None
    ):
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        status="open",
        employee_id=payload.employee_id,
        asset_id=payload.asset_id,
        incident_id=payload.incident_id,
    )

    db.add(ticket)

    try:
        db.commit()
        db.refresh(ticket)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ticket could not be created because "
                   "a database constraint was violated",
        )

    return ticket


@router.get(
    "",
    response_model=list[TicketResponse],
)
def list_tickets(
    db: DbSession,
    ticket_status: Annotated[
        TicketStatusValue | None,
        Query(alias="status"),
    ] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    statement = select(Ticket)

    if ticket_status is not None:
        statement = statement.where(
            Ticket.status == ticket_status
        )

    statement = (
        statement
        .order_by(Ticket.created_at.desc(), Ticket.id.desc())
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(statement).all()


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(ticket_id: UUID, db: DbSession):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def update_ticket(
    ticket_id: UUID,
    payload: TicketUpdate,
    db: DbSession,
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    changes = payload.model_dump(exclude_unset=True)

    if not changes or changes.get("status") is None:
        raise HTTPException(
            status_code=422,
            detail="A non-null status is required",
        )

    ticket.status = changes["status"]

    try:
        db.commit()
        db.refresh(ticket)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ticket update violated a database constraint",
        )

    return ticket
