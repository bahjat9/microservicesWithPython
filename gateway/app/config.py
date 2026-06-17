from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    user_service_url: str = "http://localhost:8001"
    game_service_url: str = "http://localhost:8002"
    activity_service_url: str = "http://localhost:8003"
    notification_service_url: str = "http://localhost:8004"
    logging_service_url: str = "http://localhost:8006"
    auth_service_url: str = "http://localhost:8005"
    secret_key: str = "dev-secret-change-in-production"

    class Config:
        env_file = ".env"

settings = Settings()