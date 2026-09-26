from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexTour API"
    # Use SQLite for demo purposes to avoid requiring a running Postgres server during review,
    # but the architecture supports Postgres (just change this URL).
    DATABASE_URL: str = "sqlite:///./tour_ops.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        case_sensitive = True

settings = Settings()
