import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def cache_game(game) -> None:
    key = f"game:summary:{game.id}"
    data = {
        "id": game.id,
        "title": game.title,
        "genre": game.genre,
        "description": game.description,
    }
    r.set(key, json.dumps(data), ex=3600)

def get_cached_game(game_id: str) -> dict | None:
    key = f"game:summary:{game_id}"
    data = r.get(key)
    if data:
        return json.loads(data)
    return None