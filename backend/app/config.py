"""
Configuration settings for Zava Capacity Planner.
Loads from environment variables with sensible defaults.

AUTHENTICATION MODES:
- Managed Identity (production): Set USE_MANAGED_IDENTITY=true
  - No password needed, uses Azure AD tokens automatically
  - POSTGRES_USER should be the Container App name
- Password-based (development): Set USE_MANAGED_IDENTITY=false
  - Traditional username/password authentication
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Zava Capacity Planner"
    debug: bool = False
    demo_mode: bool = Field(default=True, description="Run in demo mode without Azure services")

    # Azure AI Foundry V1 (Classic)
    azure_ai_project_endpoint: str = ""
    azure_ai_model_deployment_name: str = "gpt-5-mini"

    # Authentication Mode
    use_managed_identity: bool = Field(
        default=False,
        description="Use Azure AD Managed Identity for PostgreSQL authentication"
    )

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "zava_admin"
    postgres_password: Optional[str] = Field(
        default="",
        description="PostgreSQL password (not used when use_managed_identity=true)"
    )
    postgres_database: str = "zava_logistics"

    @property
    def postgres_connection_string(self) -> str:
        """Get connection string for synchronous PostgreSQL driver."""
        if self.use_managed_identity:
            # When using MI, password will be obtained via token at runtime
            return f"postgresql://{self.postgres_user}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}?sslmode=require"
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"

    @property
    def postgres_async_connection_string(self) -> str:
        """Get connection string for async PostgreSQL driver."""
        if self.use_managed_identity:
            return f"postgresql+asyncpg://{self.postgres_user}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}?ssl=require"
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"

    # Application Insights
    applicationinsights_connection_string: str = ""

    # APIM
    apim_gateway_url: str = ""
    apim_subscription_key: str = ""

    # Vector Store (for File Search)
    vector_store_id: str = ""

    # Cost calculation (GPT-5-mini pricing per million tokens)
    gpt5_mini_input_cost_per_million: float = 0.30
    gpt5_mini_output_cost_per_million: float = 1.25

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
