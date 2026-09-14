from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:5173"
    # Only affects startup diagnostics (see app/main.py) - set it to
    # "production" on a deployed instance so an unchanged localhost
    # CORS_ORIGINS is reported as the misconfiguration it is.
    ENVIRONMENT: str = "development"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
