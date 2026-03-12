from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env"
    )

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DATABASE_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    BASE_URL: str
    X_API_KEY: str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE_NAME}"


settings = Settings()
