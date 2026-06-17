from sqlalchemy.orm import Session
from app.models import Game
from app.schemas import GameCreate

def create_game(db: Session, data: GameCreate) -> Game:
    game = Game(
        title=data.title,
        genre=data.genre,
        description=data.description,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

def get_game(db: Session, game_id: str) -> Game | None:
    return db.query(Game).filter(Game.id == game_id).first()

def list_games(db: Session, limit: int = 20, offset: int = 0) -> tuple[list[Game], int]:
    total = db.query(Game).count()
    games = db.query(Game).offset(offset).limit(limit).all()
    return games, total

def delete_game(db: Session, game_id: str) -> bool:
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        return False
    db.delete(game)
    db.commit()
    return True