from pydantic import BaseModel
from dotenv import load_dotenv
import pathlib
import os


class Settings(BaseModel):
    provider: str = os.getenv("CVRGPT_PROVIDER", "fixtures")
    api_base_url: str | None = os.getenv("CVRGPT_API_BASE_URL")
    api_key: str | None = os.getenv("CVRGPT_API_KEY")
    api_user: str | None = os.getenv("CVRGPT_API_USER")
    api_password: str | None = os.getenv("CVRGPT_API_PASSWORD")
    mcp_mount_path: str = os.getenv("MCP_MOUNT_PATH", "/mcp")
    # CORS
    allowed_origins: str = os.getenv("CVRGPT_ALLOWED_ORIGINS", "http://localhost:3000")
    # API Key for endpoints
    endpoint_api_key: str = os.getenv("CVRGPT_ENDPOINT_API_KEY", "dev-key-change-me")
    # Redis
    redis_url: str = os.getenv("CVRGPT_REDIS_URL", "redis://localhost:6379/0")
    # HTTP client settings
    request_timeout_s: float = float(os.getenv("CVRGPT_REQUEST_TIMEOUT_S", "10.0"))
    provider_max_retries: int = int(os.getenv("CVRGPT_PROVIDER_MAX_RETRIES", "2"))

    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


# Load .env files early (.env.local then .env)
root = (
    pathlib.Path(__file__).parents[3]
    if len(pathlib.Path(__file__).parents) >= 3
    else pathlib.Path.cwd()
)
load_dotenv(dotenv_path=root / "server" / ".env.local")
load_dotenv(dotenv_path=root / "server" / ".env")

settings = Settings()
