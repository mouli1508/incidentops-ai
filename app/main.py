from fastapi import FastAPI

from app.api.routes import incidents, tickets


app = FastAPI(
    title="CM Enterprise — IncidentOps AI",
    version="0.3.0",
    description="Enterprise incident intelligence and resolution API",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "CM Enterprise IncidentOps API"
    }


app.include_router(
    tickets.router,
    prefix="/api/v1",
)

app.include_router(
    incidents.router,
    prefix="/api/v1",
)
