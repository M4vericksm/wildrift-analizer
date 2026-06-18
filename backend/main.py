from fastapi import FastAPI

from backend.routers import matches, meta

app = FastAPI(title="wildrift-analizer", version="0.1.0")
app.include_router(matches.router)
app.include_router(meta.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
