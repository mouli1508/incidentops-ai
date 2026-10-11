from fastapi import FastAPI

app = FastAPI(
    title="CM Enterprise IncidentOps API",
    version="0.1.0",
)

@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "CM Enterprise IncidentOps API"
    }