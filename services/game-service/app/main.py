from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="game-service")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "game-service"}

app.include_router(router)