async def add_activity(db: Session, data: ActivityCreate) -> ActivityOut:
    from app.infrastructure.rabbitmq_publisher import publish_activity_event

    user_exists = await validate_user(data.user_id)
    if not user_exists:
        raise ValueError(f"User {data.user_id} not found")

    activity = repository.create_activity(db, data)
    game = await fetch_game(data.game_id)

    game_title = game.title if game else None
    await publish_activity_event(
        user_id=activity.user_id,
        game_id=activity.game_id,
        action=activity.action,
        game_title=game_title,
    )

    result = ActivityOut.model_validate(activity)
    result.game = game
    return result