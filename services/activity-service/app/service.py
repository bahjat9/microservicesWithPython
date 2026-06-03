import httpx
from sqlalchemy.orm import Session
from app import repository
from app.schemas import ActivityCreate, ActivityOut, ActivityList, GameOut
from app.config import settings

async def validate_user(user_id: str) -> bool:
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.user_service_url}/v1/users/{user_id}")
                return resp.status_code == 200
        except httpx.RequestError:
            if attempt == 2:
                raise
    return False

async def fetch_game(game_id: str) -> GameOut | None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.game_service_url}/v1/games/{game_id}")
            if resp.status_code == 200:
                data = resp.json()
                return GameOut(
                    id=data["id"],
                    title=data["title"],
                    genre=data["genre"],
                    description=data.get("description"),
                )
    except httpx.RequestError:
        pass
    return None

async def add_activity(db: Session, data: ActivityCreate) -> ActivityOut:
    from app.infrastructure.rabbitmq_publisher import publish_activity_event

    user_exists = await validate_user(data.user_id)
    if not user_exists:
        raise ValueError(f"User {data.user_id} not found")

    activity = repository.create_activity(db, data)
    game = await fetch_game(data.game_id)

    game_title = game.title if game else None
    print(f"[DEBUG] About to publish for user {activity.user_id}")
    await publish_activity_event(
        user_id=activity.user_id,
        game_id=activity.game_id,
        action=activity.action,
        game_title=game_title,
    )
    print("[DEBUG] Publish done")

    result = ActivityOut.model_validate(activity)
    result.game = game
    return result

async def fetch_all_activities(db: Session, limit: int = 20, offset: int = 0) -> ActivityList:
    items, total = repository.list_activities(db, limit, offset)
    enriched = []
    for a in items:
        game = await fetch_game(a.game_id)
        out = ActivityOut.model_validate(a)
        out.game = game
        enriched.append(out)
    return ActivityList(items=enriched, total=total, limit=limit, offset=offset)

async def fetch_user_activities(db: Session, user_id: str, limit: int = 20, offset: int = 0) -> ActivityList:
    items, total = repository.list_activities_by_user(db, user_id, limit, offset)
    enriched = []
    for a in items:
        game = await fetch_game(a.game_id)
        out = ActivityOut.model_validate(a)
        out.game = game
        enriched.append(out)
    return ActivityList(items=enriched, total=total, limit=limit, offset=offset)