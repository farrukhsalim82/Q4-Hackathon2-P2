"""
[Task]: T-B005
[From]: speckit.plan §4.2
[Purpose]: Pydantic Settings configuration — loads env vars from .env
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    frontend_url: str = "http://localhost:3000"
    debug: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
