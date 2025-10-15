# Settings Refactoring to Pydantic Settings

## Current State Analysis

### Current Implementation
The settings module currently uses plain Pydantic models (`BaseModel`) with custom loading/saving logic:

```
src/ooai/core/settings/
├── __init__.py         # Exports all settings
├── local.py           # LocalSettings - main config manager
├── cache.py           # CacheSettings - cache configuration
└── llm/
    ├── settings.py    # LLMSettings - LLM configuration
    └── providers.py   # Provider enums and models
```

### Key Characteristics
1. **Plain Pydantic Models**: Using `BaseModel`, not `BaseSettings`
2. **Custom File I/O**: Manual YAML/JSON loading and saving
3. **Custom Environment Variable Loading**: Manual `os.getenv()` calls
4. **Project-Local Config**: Supports `.ooai/` directory in project root
5. **Nested Configuration**: Settings contain other settings models

## Proposed Refactoring

### 1. Use Pydantic Settings v2

Convert to `pydantic-settings` (v2) for better environment variable support:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from pathlib import Path

class CoreSettings(BaseSettings):
    """Core application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',  # Allows OOAI__LLM__MODEL=gpt-4
        case_sensitive=False,
        extra='ignore'
    )

    # Project configuration
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / '.ooai',
        alias='OOAI_CONFIG_DIR'
    )
    environment: str = Field(
        default='development',
        alias='OOAI_ENV'
    )
```

### 2. Hierarchical Settings Structure

```python
# cache_settings.py
class CacheSettings(BaseSettings):
    """Cache-specific settings."""
    model_config = SettingsConfigDict(env_prefix='OOAI_CACHE_')

    enabled: bool = True
    dir: Path = Field(default_factory=lambda: Path.home() / '.ooai/cache')
    max_size_mb: int = Field(500, ge=10, le=10000)
    ttl_seconds: int = Field(3600, ge=0)
    compression: bool = True

# llm_settings.py
class LLMSettings(BaseSettings):
    """LLM-specific settings."""
    model_config = SettingsConfigDict(env_prefix='OOAI_LLM_')

    provider: str = 'openai'
    model: str = 'gpt-4'
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    timeout: int = Field(30, ge=1, le=300)

    # API keys from environment
    openai_api_key: Optional[str] = Field(default=None, alias='OPENAI_API_KEY')
    anthropic_api_key: Optional[str] = Field(default=None, alias='ANTHROPIC_API_KEY')

    @property
    def api_key(self) -> Optional[str]:
        """Get API key for current provider."""
        return getattr(self, f"{self.provider}_api_key", None)

# main_settings.py
class Settings(BaseSettings):
    """Main application settings."""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='OOAI_',
        env_nested_delimiter='__',
        case_sensitive=False
    )

    # Nested settings
    cache: CacheSettings = Field(default_factory=CacheSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)

    # Project overrides
    project_config_file: Optional[Path] = Field(
        default=None,
        description="Path to project-specific config"
    )

    @model_validator(mode='after')
    def load_project_config(self) -> 'Settings':
        """Load project-specific overrides if available."""
        if self.project_config_file and self.project_config_file.exists():
            # Load and apply overrides
            pass
        return self
```

### 3. Configuration Sources Priority

Pydantic Settings v2 supports multiple configuration sources with built-in priority:

1. **Environment Variables** (highest priority)
2. **`.env` file** in project root
3. **`.ooai/config.yaml`** project config
4. **`~/.ooai/config.yaml`** user config
5. **Default values** (lowest priority)

### 4. Custom Settings Sources

```python
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from typing import Dict, Any, Tuple

class YamlSettingsSource(PydanticBaseSettingsSource):
    """Custom YAML settings source for .ooai/config.yaml."""

    def __init__(self, settings_cls: type[BaseSettings], yaml_file: Path):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file

    def get_field_value(
        self, field_name: str, field: FieldInfo
    ) -> Tuple[Any, str, bool]:
        # Load from YAML file
        if self.yaml_file.exists():
            with open(self.yaml_file) as f:
                data = yaml.safe_load(f)
                # Return (value, source_name, is_complex)
                return data.get(field_name), 'yaml', False
        return None, '', False

    def __call__(self) -> Dict[str, Any]:
        if self.yaml_file.exists():
            with open(self.yaml_file) as f:
                return yaml.safe_load(f) or {}
        return {}

class Settings(BaseSettings):
    """Main settings with custom sources."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Add custom YAML source
        yaml_source = YamlSettingsSource(
            settings_cls,
            Path.home() / '.ooai/config.yaml'
        )
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            yaml_source,  # Custom source
            file_secret_settings,
        )
```

## Benefits of Refactoring

### 1. **Automatic Environment Variable Handling**
- No manual `os.getenv()` calls
- Automatic type conversion and validation
- Nested environment variable support (`OOAI__LLM__MODEL`)

### 2. **Better Validation**
- Environment variables validated on load
- Type coercion with proper error messages
- Field aliases for flexibility

### 3. **Multiple Configuration Sources**
- Built-in `.env` file support
- Custom sources (YAML, JSON, TOML)
- Automatic priority resolution

### 4. **Improved Testing**
```python
def test_with_settings():
    # Easy to override for tests
    settings = Settings(
        llm__provider="mock",
        cache__enabled=False
    )
```

### 5. **Better Documentation**
- Settings are self-documenting
- JSON Schema generation
- Environment variable documentation

## Migration Plan

### Phase 1: Create New Settings Module (Non-Breaking)
1. Create `settings_v2/` directory
2. Implement new Pydantic Settings classes
3. Add compatibility layer

```python
# settings/__init__.py (compatibility)
from .settings_v2 import Settings as NewSettings
from .local import LocalSettings  # Keep old for backward compat

def get_settings() -> NewSettings:
    """Get settings (new implementation)."""
    return NewSettings()

def get_local_settings() -> LocalSettings:
    """Backward compatibility."""
    # Convert new to old format
    new = get_settings()
    return LocalSettings(...)
```

### Phase 2: Gradual Migration
1. Update new code to use `get_settings()`
2. Add deprecation warnings to old functions
3. Migrate existing code gradually

### Phase 3: Cleanup (Breaking)
1. Remove old settings module
2. Update all imports
3. Remove compatibility layer

## Impact Analysis

### Code Changes Required

1. **Import Changes**:
```python
# Old
from ooai.core.settings import get_local_settings
settings = get_local_settings()

# New
from ooai.core.settings import get_settings
settings = get_settings()
```

2. **Access Pattern Changes**:
```python
# Old
settings.llm_settings.default_model

# New
settings.llm.model
```

3. **Environment Variables**:
```bash
# Old (manual handling)
export OPENAI_API_KEY=sk-...

# New (automatic)
export OPENAI_API_KEY=sk-...
export OOAI__LLM__MODEL=gpt-4
export OOAI__CACHE__ENABLED=false
```

### Files Affected
- All files importing from `settings/`
- Test files using settings
- Documentation mentioning configuration

## Example Implementation

```python
# src/ooai/core/settings_v2/__init__.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional
from pathlib import Path
import yaml

class Settings(BaseSettings):
    """Unified settings with Pydantic Settings v2."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='OOAI_',
        env_nested_delimiter='__',
        case_sensitive=False,
        # Custom config file
        json_file='ooai.config.json',
        yaml_file='ooai.config.yaml',
        toml_file='ooai.config.toml',
    )

    # LLM Configuration
    llm_provider: str = Field('openai', alias='OOAI_LLM_PROVIDER')
    llm_model: str = Field('gpt-4', alias='OOAI_LLM_MODEL')
    llm_temperature: float = Field(0.7, ge=0.0, le=2.0)
    llm_max_tokens: Optional[int] = None

    # API Keys (from environment)
    openai_api_key: Optional[str] = Field(default=None, alias='OPENAI_API_KEY')
    anthropic_api_key: Optional[str] = Field(default=None, alias='ANTHROPIC_API_KEY')

    # Cache Configuration
    cache_enabled: bool = Field(True, alias='OOAI_CACHE_ENABLED')
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / '.ooai/cache',
        alias='OOAI_CACHE_DIR'
    )
    cache_ttl: int = Field(3600, alias='OOAI_CACHE_TTL')

    # Project Configuration
    project_name: Optional[str] = Field(None, alias='OOAI_PROJECT')
    environment: str = Field('development', alias='OOAI_ENV')

    @field_validator('cache_dir')
    @classmethod
    def ensure_cache_dir(cls, v: Path) -> Path:
        """Ensure cache directory exists."""
        v = v.expanduser().resolve()
        v.mkdir(parents=True, exist_ok=True)
        return v

    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for provider."""
        provider = provider or self.llm_provider
        return getattr(self, f"{provider}_api_key", None)

    def to_yaml(self, path: Path) -> None:
        """Export settings to YAML."""
        with open(path, 'w') as f:
            yaml.dump(self.model_dump(exclude_unset=True), f)

# Usage
settings = Settings()  # Loads from env, .env, config files
print(settings.llm_model)  # Automatic env var: OOAI__LLM__MODEL
print(settings.get_api_key())  # Gets key for current provider
```

## Recommendations

1. **Start with Phase 1**: Create parallel implementation
2. **Test thoroughly**: Ensure backward compatibility
3. **Document changes**: Update all configuration docs
4. **Provide migration tools**: Script to convert old configs
5. **Use feature flags**: Allow switching between old/new

## Next Steps

1. Review this proposal
2. Create `settings_v2/` with new implementation
3. Add tests for new settings
4. Create migration guide
5. Implement compatibility layer