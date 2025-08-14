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

    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

# Load .env files early (.env.local then .env)
root = pathlib.Path(__file__).parents[3] if len(pathlib.Path(__file__).parents) >= 3 else pathlib.Path.cwd()
load_dotenv(dotenv_path=root / "server" / ".env.local")
load_dotenv(dotenv_path=root / "server" / ".env")

settings = Settings()
