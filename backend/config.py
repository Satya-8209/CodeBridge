from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    hindsight_api_key: str
    hindsight_bank_id: str = "devops-incident-memory"

    # xAI (Grok) — set if you have credits
    xai_api_key: str = ""
    xai_model: str = "grok-3-mini"

    # Groq — free tier, used as active LLM
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    # Active LLM provider: "groq" or "xai"
    llm_provider: str = "groq"

    slack_bot_token: str = ""
    slack_app_token: str = ""
    slack_signing_secret: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
