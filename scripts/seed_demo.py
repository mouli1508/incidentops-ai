
import time

from sqlalchemy import select

from app.db.models import Employee, Incident, Ticket
from app.db.session import SessionLocal


def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def main():
    log("Starting seed script")

    with SessionLocal() as session:
        log("Session created")

        log("Querying employee...")
        employee = session.scalar(
            select(Employee).where(
                Employee.email == "alice@cmenterprise.example"
            )
        )
        log("Employee query completed")

        if employee is None:
            log("Creating employee")
            employee = Employee(
                name="Alice",
                email="alice@cmenterprise.example",
                department="Finance",
            )
            session.add(employee)
            session.flush()
            log("Employee inserted")

        log("Querying incident...")
        incident = session.scalar(
            select(Incident).where(
                Incident.title == "Demo Teams Outage"
            )
        )
        log("Incident query completed")

        if incident is None:
            log("Creating incident")
            incident = Incident(
                title="Demo Teams Outage",
                description="Synthetic incident for development",
            )
            session.add(incident)
            session.flush()
            log("Incident inserted")

        log("Querying ticket...")
        ticket = session.scalar(
            select(Ticket).where(
                Ticket.title == "Teams connection failure"
            )
        )
        log("Ticket query completed")

        if ticket is None:
            log("Creating ticket")
            ticket = Ticket(
                title="Teams connection failure",
                description="Cannot connect to Teams meetings.",
                employee_id=employee.id,
                incident_id=incident.id,
            )
            session.add(ticket)
            session.flush()
            log("Ticket inserted")

        log("Committing transaction...")
        session.commit()
        log("Transaction committed")

        log(f"Employee: {employee.id}")
        log(f"Incident: {incident.id}")
        log(f"Ticket:   {ticket.id}")


if __name__ == "__main__":
    main()
