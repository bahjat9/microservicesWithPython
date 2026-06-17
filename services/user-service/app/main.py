from fastapi import FastAPI
from app.database import Base, engine
from app.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="user-service")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "user-service"}

app.include_router(router)
