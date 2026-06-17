from sqlalchemy.orm import Session
from app import repository
from app.schemas import GameCreate, GameOut, GameList
from app.infrastructure.cache import cache_game, get_cached_game

def add_game(db: Session, data: GameCreate) -> GameOut:
    game = repository.create_game(db, data)
    cache_game(game)
    return GameOut.model_validate(game)

def fetch_game(db: Session, game_id: str) -> GameOut:
    game = repository.get_game(db, game_id)
    if game is None:
        raise ValueError(f"Game {game_id} not found")
    return GameOut.model_validate(game)

def fetch_game_summary(game_id: str) -> dict | None:
    return get_cached_game(game_id)

def fetch_all_games(db: Session, limit: int = 20, offset: int = 0) -> GameList:
    games, total = repository.list_games(db, limit=limit, offset=offset)
    return GameList(
        items=[GameOut.model_validate(g) for g in games],
        total=total,
        limit=limit,
        offset=offset,
    )

def remove_game(db: Session, game_id: str) -> None:
    deleted = repository.delete_game(db, game_id)
    if not deleted:
        raise ValueError(f"Game {game_id} not found")