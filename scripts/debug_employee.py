
import time

from sqlalchemy import select, text

from app.db.models import Employee
from app.db.session import SessionLocal


def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def main():
    with SessionLocal() as session:
        log("1. Running SELECT 1")
        session.execute(text("SELECT 1"))
        log("2. SELECT 1 succeeded")

        log("3. Running raw SQL against employees")
        rows = session.execute(
            text("SELECT id, email FROM employees LIMIT 5")
        ).all()
        log(f"4. Raw SQL succeeded: {len(rows)} rows")

        log("5. Running ORM Employee query")
        employee = session.scalar(
            select(Employee).where(
                Employee.email == "alice@cmenterprise.example"
            )
        )
        log(f"6. ORM query succeeded: {employee is not None}")


if __name__ == "__main__":
    main()
