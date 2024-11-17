from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    class ConfigDict:
        env_file = "../.env"
    
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DB_URL: str
    TEST_DB_URL: str = "sqlite+aiosqlite:///test.db"

settings = Settings()