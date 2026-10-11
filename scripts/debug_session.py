
import time

from sqlalchemy import text

from app.db.session import SessionLocal, engine


def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def main():
    log("Starting")

    log("Connecting using engine...")
    with engine.connect() as connection:
        log("Engine connected")

        result = connection.execute(text("SELECT 1")).scalar()
        log(f"Engine query result: {result}")

    log("Creating ORM session...")
    with SessionLocal() as session:
        log("Executing ORM session query...")

        result = session.execute(text("SELECT 1")).scalar()
        log(f"Session query result: {result}")

    log("Finished")


if __name__ == "__main__":
    main()
