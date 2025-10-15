#!/usr/bin/env python
"""Example implementation of refactored settings using Pydantic Settings v2.

This demonstrates how the settings module could be refactored to use
pydantic-settings for better environment variable support, validation,
and configuration management.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


# ============================================================================
# Custom Settings Source for YAML Configuration
# ============================================================================


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """Custom settings source for YAML configuration files."""

    def __init__(self, settings_cls: type[BaseSettings], yaml_file: Path | None = None):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file or self._find_config_file()

    def _find_config_file(self) -> Path:
        """Find .ooai/config.yaml in project or home directory."""
        # Check project directory
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            config_file = parent / ".ooai" / "config.yaml"
            if config_file.exists():
                return config_file

        # Fallback to home directory
        return Path.home() / ".ooai" / "config.yaml"

    def get_field_value(self, field_name: str, field: Any) -> Tuple[Any, str, bool]:
        """Get field value from YAML file."""
        if self.yaml_file and self.yaml_file.exists():
            try:
                with open(self.yaml_file) as f:
                    data = yaml.safe_load(f) or {}

                # Handle nested fields (e.g., llm.model)
                if "." in field_name:
                    parts = field_name.split(".")
                    value = data
                    for part in parts:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            value = None
                            break
                else:
                    value = data.get(field_name)

                if value is not None:
                    return value, str(self.yaml_file), False
            except Exception:
                pass

        return None, "", False

    def __call__(self) -> Dict[str, Any]:
        """Load all settings from YAML."""
        if self.yaml_file and self.yaml_file.exists():
            try:
                with open(self.yaml_file) as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        return {}


# ============================================================================
# Settings Models with Pydantic Settings v2
# ============================================================================


class CacheSettings(BaseSettings):
    """Cache configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="OOAI_CACHE_", env_nested_delimiter="__", case_sensitive=False
    )

    enabled: bool = Field(True, description="Enable caching")
    dir: Path = Field(
        default_factory=lambda: Path.home() / ".ooai" / "cache",
        description="Cache directory",
    )
    max_size_mb: int = Field(500, ge=10, le=10000, description="Maximum cache size in MB")
    ttl_seconds: int = Field(3600, ge=0, description="Default TTL in seconds")
    compression: bool = Field(True, description="Enable compression")

    @field_validator("dir")
    @classmethod
    def ensure_dir_exists(cls, v: Path) -> Path:
        """Ensure cache directory exists."""
        v = v.expanduser().resolve()
        v.mkdir(parents=True, exist_ok=True)
        return v


class LLMSettings(BaseSettings):
    """LLM configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="OOAI_LLM_", env_nested_delimiter="__", case_sensitive=False
    )

    provider: str = Field("openai", description="LLM provider")
    model: str = Field("gpt-4", description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens")
    timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    streaming: bool = Field(False, description="Enable streaming")

    # API Keys - loaded from standard environment variables
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(None, alias="GOOGLE_API_KEY")

    @property
    def api_key(self) -> Optional[str]:
        """Get API key for current provider."""
        key_mapping = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
        }
        return key_mapping.get(self.provider.lower())


class ProjectSettings(BaseSettings):
    """Project-specific settings."""

    model_config = SettingsConfigDict(
        env_prefix="OOAI_PROJECT_", env_nested_delimiter="__", case_sensitive=False
    )

    name: Optional[str] = Field(None, description="Project name")
    path: Optional[Path] = Field(None, description="Project path")
    environment: str = Field("development", description="Environment (dev/staging/prod)")
    debug: bool = Field(False, description="Debug mode")


class Settings(BaseSettings):
    """Main application settings with nested configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OOAI_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Nested settings
    cache: CacheSettings = Field(default_factory=CacheSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    project: ProjectSettings = Field(default_factory=ProjectSettings)

    # Global settings
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".ooai", description="Configuration directory"
    )
    auto_save: bool = Field(True, description="Auto-save configuration changes")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Add custom YAML source to configuration sources."""
        yaml_source = YamlConfigSettingsSource(settings_cls)
        return (
            init_settings,  # Highest priority: constructor args
            env_settings,  # Environment variables
            dotenv_settings,  # .env file
            yaml_source,  # Custom YAML config
            file_secret_settings,  # Lowest priority: file secrets
        )

    @field_validator("config_dir")
    @classmethod
    def ensure_config_dir(cls, v: Path) -> Path:
        """Ensure config directory exists."""
        v = v.expanduser().resolve()
        v.mkdir(parents=True, exist_ok=True)
        return v

    @model_validator(mode="after")
    def post_validation(self) -> Settings:
        """Post-validation processing."""
        # Set project path if not specified
        if not self.project.path:
            self.project.path = Path.cwd()

        # Set project name from directory if not specified
        if not self.project.name:
            self.project.name = self.project.path.name

        return self

    def save_to_yaml(self, path: Optional[Path] = None) -> None:
        """Save current settings to YAML file."""
        path = path or self.config_dir / "config.yaml"
        data = self.model_dump(exclude_unset=True, exclude_none=True)

        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=True, indent=2)

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for engine creation."""
        return {
            "provider": self.llm.provider,
            "model": self.llm.model,
            "temperature": self.llm.temperature,
            "max_tokens": self.llm.max_tokens,
            "api_key": self.llm.api_key,
            "timeout": self.llm.timeout,
            "streaming": self.llm.streaming,
        }

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            "enabled": self.cache.enabled,
            "directory": str(self.cache.dir),
            "max_size_mb": self.cache.max_size_mb,
            "ttl_seconds": self.cache.ttl_seconds,
            "compression": self.cache.compression,
        }


# ============================================================================
# Singleton Pattern for Global Settings
# ============================================================================


_settings: Optional[Settings] = None


def get_settings(**overrides) -> Settings:
    """Get global settings instance with optional overrides.

    Args:
        **overrides: Setting overrides (e.g., llm__model="gpt-3.5-turbo")

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None or overrides:
        _settings = Settings(**overrides)
    return _settings


def reset_settings() -> None:
    """Reset global settings (useful for testing)."""
    global _settings
    _settings = None


# ============================================================================
# Backward Compatibility Layer
# ============================================================================


def get_local_settings() -> Settings:
    """Backward compatibility for old API."""
    import warnings

    warnings.warn(
        "get_local_settings() is deprecated, use get_settings() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_settings()


def get_llm_settings() -> LLMSettings:
    """Backward compatibility for LLM settings."""
    return get_settings().llm


def get_cache_settings() -> CacheSettings:
    """Backward compatibility for cache settings."""
    return get_settings().cache


# ============================================================================
# Example Usage and Testing
# ============================================================================


def main():
    """Demonstrate the refactored settings system."""
    print("Pydantic Settings v2 Refactoring Example")
    print("=" * 50)

    # 1. Load settings with automatic environment variable support
    settings = get_settings()

    print("\n1. Default Settings:")
    print(f"   LLM Provider: {settings.llm.provider}")
    print(f"   LLM Model: {settings.llm.model}")
    print(f"   Cache Enabled: {settings.cache.enabled}")
    print(f"   Environment: {settings.project.environment}")

    # 2. Override with environment variables
    os.environ["OOAI_LLM_MODEL"] = "gpt-3.5-turbo"
    os.environ["OOAI_CACHE_ENABLED"] = "false"
    os.environ["OOAI_PROJECT_ENVIRONMENT"] = "production"

    # Reset and reload
    reset_settings()
    settings = get_settings()

    print("\n2. After Environment Variables:")
    print(f"   LLM Model: {settings.llm.model}")
    print(f"   Cache Enabled: {settings.cache.enabled}")
    print(f"   Environment: {settings.project.environment}")

    # 3. Override with constructor args (highest priority)
    settings = get_settings(llm__temperature=0.5, cache__ttl_seconds=7200)

    print("\n3. With Constructor Overrides:")
    print(f"   LLM Temperature: {settings.llm.temperature}")
    print(f"   Cache TTL: {settings.cache.ttl_seconds} seconds")

    # 4. Get configuration for components
    print("\n4. Component Configurations:")
    llm_config = settings.get_llm_config()
    print(f"   LLM Config: {llm_config}")

    cache_config = settings.get_cache_config()
    print(f"   Cache Config: {cache_config}")

    # 5. Save to YAML
    yaml_path = Path("/tmp/ooai_settings.yaml")
    settings.save_to_yaml(yaml_path)
    print(f"\n5. Settings saved to: {yaml_path}")

    # 6. Environment variable documentation
    print("\n6. Supported Environment Variables:")
    env_vars = [
        "OOAI_LLM_PROVIDER        - LLM provider (openai, anthropic, etc.)",
        "OOAI_LLM_MODEL           - Model name",
        "OOAI_LLM_TEMPERATURE     - Sampling temperature (0.0-2.0)",
        "OOAI_CACHE_ENABLED       - Enable/disable caching",
        "OOAI_CACHE_DIR           - Cache directory path",
        "OOAI_PROJECT_ENVIRONMENT - Environment (development/production)",
        "OPENAI_API_KEY           - OpenAI API key",
        "ANTHROPIC_API_KEY        - Anthropic API key",
    ]
    for var in env_vars:
        print(f"   {var}")

    # 7. Priority demonstration
    print("\n7. Configuration Priority (highest to lowest):")
    print("   1. Constructor arguments: Settings(llm__model='claude')")
    print("   2. Environment variables: OOAI_LLM_MODEL=gpt-4")
    print("   3. .env file: OOAI_LLM_MODEL=gpt-3.5-turbo")
    print("   4. YAML config: llm.model: 'gpt-3.5-turbo'")
    print("   5. Default values: model='gpt-4'")


if __name__ == "__main__":
    main()

    # Clean up environment
    for key in list(os.environ.keys()):
        if key.startswith("OOAI_"):
            del os.environ[key]