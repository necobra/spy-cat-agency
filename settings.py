from pydantic.v1 import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Spy Cat Agency project"
    DATABASE_URL: str | None = "sqlite+aiosqlite:///./spy_cat_agency.db"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
