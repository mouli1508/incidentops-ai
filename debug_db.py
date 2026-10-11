
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from app.config import settings

url = make_url(settings.database_url)

print("Driver:", url.drivername, flush=True)
print("Host:", url.host, flush=True)
print("Port:", url.port, flush=True)
print("Database:", url.database, flush=True)

print("Creating engine...", flush=True)

engine = create_engine(
    settings.database_url,
    connect_args={"connect_timeout": 5},
    pool_timeout=5,
)

print("Engine created.", flush=True)
print("Connecting to PostgreSQL...", flush=True)

try:
    with engine.connect() as connection:
        print("Connected!", flush=True)

        result = connection.execute(
            text("SELECT 1")
        ).scalar()

        print("Query result:", result, flush=True)

except Exception as exc:
    print(
        f"Connection failed: {type(exc).__name__}: {exc}",
        flush=True,
    )

finally:
    engine.dispose()
