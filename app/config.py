from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str
    tavily_api_key: str | None = None
    cases_api_url: str = "https://ai-stance.vercel.app/api/cases"
    groq_model: str = "llama-3.1-8b-instant"
    confidence_threshold: float = 0.75
    cases_fetch_limit: int = 100

    @field_validator("groq_api_key", "tavily_api_key", mode="before")
    @classmethod
    def strip_api_keys(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


settings = Settings()
print("Groq key loaded:", bool(settings.groq_api_key))
print("Groq key prefix:", settings.groq_api_key[:8])