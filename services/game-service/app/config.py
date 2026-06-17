from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    auth_secret_key: str = "dev-secret-change-in-production"

    class Config:
        env_file = ".env"

settings = Settings()