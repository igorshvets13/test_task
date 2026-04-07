from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Custom Auth API"
    secret_key: str = "my-very-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./app.db"

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()