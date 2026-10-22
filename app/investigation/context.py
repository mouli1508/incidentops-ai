from dataclasses import asdict, dataclass
from uuid import UUID

from sqlalchemy import select

from app.db.models import (
    Ticket,
    Employee,
    Asset,
    Incident,
)
from app.db.session import SessionLocal


def enum_value(value):
    """
    Convert enum values into regular strings.
    """
    return value.value if hasattr(value, "value") else value


@dataclass
class TicketContext:
    ticket_id: str
    title: str
    description: str
    status: str
    employee_department: str | None
    asset_hostname: str | None
    asset_type: str | None
    incident_id: str | None
    incident_title: str | None
    incident_severity: str | None
    incident_status: str | None

    def to_dict(self) -> dict:
        return asdict(self)


def get_ticket_context(
    ticket_id: UUID,
) -> TicketContext | None:
    """
    Retrieve ticket context without modifying
    any database records.
    """

    with SessionLocal() as db:
        ticket = db.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if ticket is None:
            return None

        employee = db.scalar(
            select(Employee).where(
                Employee.id == ticket.employee_id
            )
        )

        asset = None
        if ticket.asset_id is not None:
            asset = db.scalar(
                select(Asset).where(
                    Asset.id == ticket.asset_id
                )
            )

        incident = None
        if ticket.incident_id is not None:
            incident = db.scalar(
                select(Incident).where(
                    Incident.id == ticket.incident_id
                )
            )

        return TicketContext(
            ticket_id=str(ticket.id),
            title=ticket.title,
            description=ticket.description,
            status=enum_value(ticket.status),
            employee_department=(
                employee.department if employee else None
            ),
            asset_hostname=(
                asset.hostname if asset else None
            ),
            asset_type=(
                enum_value(asset.asset_type)
                if asset else None
            ),
            incident_id=(
                str(incident.id) if incident else None
            ),
            incident_title=(
                incident.title if incident else None
            ),
            incident_severity=(
                enum_value(incident.severity)
                if incident else None
            ),
            incident_status=(
                enum_value(incident.status)
                if incident else None
            ),
        )
