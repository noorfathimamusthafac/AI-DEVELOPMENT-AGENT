import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_REPO_DIR = BASE_DIR / "test-repository"

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Dev Agent"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-dev-agent-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'backend' / 'dev_agent.db'}")

    # OpenProject Settings
    OPENPROJECT_URL: str = os.getenv("OPENPROJECT_URL", "https://openproject.example.com")
    OPENPROJECT_API_KEY: str = os.getenv("OPENPROJECT_API_KEY", "")
    OPENPROJECT_MOCK_MODE: bool = os.getenv("OPENPROJECT_MOCK_MODE", "true").lower() in ("true", "1", "yes")

    # Target Repository
    TARGET_REPO_PATH: str = os.getenv("TARGET_REPO_PATH", str(DEFAULT_REPO_DIR))

    # AI Model Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")  # 'openai', 'gemini', 'anthropic', 'auto'
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
