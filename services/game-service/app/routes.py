from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import service
from app.schemas import GameCreate, GameOut, GameList
from app.security import require_admin

router = APIRouter(prefix="/v1/games", tags=["games"])

@router.post("/", status_code=201, response_model=GameOut)
def create_game(data: GameCreate, db: Session = Depends(get_db)):
    return service.add_game(db, data)

@router.get("/", response_model=GameList)
def list_games(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    return service.fetch_all_games(db, limit=limit, offset=offset)

@router.get("/{game_id}/summary")
def get_game_summary(game_id: str):
    summary = service.fetch_game_summary(game_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Game summary not found in cache")
    return summary

@router.get("/{game_id}", response_model=GameOut)
def get_game(game_id: str, db: Session = Depends(get_db)):
    try:
        return service.fetch_game(db, game_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{game_id}", dependencies=[Depends(require_admin)])
def delete_game(game_id: str, db: Session = Depends(get_db)):
    try:
        service.remove_game(db, game_id)
        return {"detail": "Game deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))