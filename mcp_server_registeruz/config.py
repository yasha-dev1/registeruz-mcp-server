"""Configuration module for RegisterUZ MCP Server."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl, field_validator

# Load environment variables from .env file
load_dotenv()


class RegisterUZConfig(BaseModel):
    """Configuration for RegisterUZ API client."""
    
    base_url: HttpUrl = Field(
        default="https://www.registeruz.sk/cruz-public/api",
        description="Base URL for RegisterUZ API"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds"
    )
    max_records: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum records per request"
    )
    default_from_date: str = Field(
        default="2000-01-01",
        description="Default date for initial data fetch (YYYY-MM-DD)"
    )
    
    @field_validator("default_from_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM-DD."""
        import re
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern, v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v
    
    @field_validator("base_url")
    @classmethod
    def ensure_base_url_format(cls, v: HttpUrl) -> HttpUrl:
        """Ensure base URL doesn't end with slash."""
        url_str = str(v)
        if url_str.endswith("/"):
            url_str = url_str.rstrip("/")
        return HttpUrl(url_str)
    
    class Config:
        """Pydantic config."""
        env_prefix = "REGISTERUZ_"
        str_strip_whitespace = True


def get_config() -> RegisterUZConfig:
    """Get configuration from environment variables."""
    return RegisterUZConfig(
        base_url=os.getenv("REGISTERUZ_BASE_URL", "https://www.registeruz.sk/cruz-public/api"),
        timeout=int(os.getenv("REGISTERUZ_TIMEOUT", "30")),
        max_records=int(os.getenv("REGISTERUZ_MAX_RECORDS", "1000")),
        default_from_date=os.getenv("REGISTERUZ_DEFAULT_FROM_DATE", "2000-01-01")
    )