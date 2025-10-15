# Direct Overwrite Plan: Pydantic Settings v2

## Approach: Replace Existing Implementation

Instead of creating a parallel `settings_v2/` module, we'll directly replace the current implementation while preserving the exact same API where possible.

## Implementation Strategy

### Step 1: Backup Current Implementation

```bash
# Create backup branch
git checkout -b backup/original-settings

# Or create backup directory
cp -r src/ooai/core/settings src/ooai/core/settings_backup
```

### Step 2: Modify Existing Files In-Place

#### 2.1 Update `settings/base.py` (NEW FILE)
Create a base settings class with Pydantic Settings v2:

```python
# src/ooai/core/settings/base.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Optional

class OOAIBaseSettings(BaseSettings):
    """Base settings class with common configuration."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore'
    )

    @classmethod
    def _get_config_dir(cls) -> Path:
        """Get config directory (same logic as current)."""
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            project_ooai = parent / ".ooai"
            if project_ooai.exists() and project_ooai.is_dir():
                return project_ooai
        return Path.home() / ".ooai"
```

#### 2.2 Update `settings/local.py`
Keep the same class name and most methods, but inherit from BaseSettings:

```python
# src/ooai/core/settings/local.py
from __future__ import annotations
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .base import OOAIBaseSettings
from .cache import CacheSettings
from .llm import LLMSettings

class LocalSettings(OOAIBaseSettings):
    """Local configuration settings - SAME API as before."""

    # Keep exact same fields
    config_dir: Path = Field(
        default_factory=OOAIBaseSettings._get_config_dir,
        description="Configuration directory path"
    )
    config_file: str = Field(
        default="config.yaml",
        description="Configuration file name"
    )
    config_format: str = Field(
        default="yaml",
        description="Configuration file format"
    )
    auto_save: bool = Field(
        default=True,
        description="Auto-save changes to disk"
    )
    create_if_missing: bool = Field(
        default=True,
        description="Create config if missing"
    )

    # Component settings - same as before
    llm_settings: LLMSettings = Field(
        default_factory=LLMSettings,
        description="LLM configuration"
    )
    cache_settings: CacheSettings = Field(
        default_factory=CacheSettings,
        description="Cache configuration"
    )

    # Keep these exactly the same
    user_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User preferences"
    )
    project_overrides: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Project-specific overrides"
    )

    # Keep ALL existing methods unchanged
    def load_from_file(self) -> None:
        """Same implementation as before."""
        # ... existing code ...

    def save_to_file(self) -> None:
        """Same implementation as before."""
        # ... existing code ...

    def get_project_config(self, project_path) -> Dict[str, Any]:
        """Same implementation as before."""
        # ... existing code ...

    # etc - all methods stay the same
```

#### 2.3 Update `settings/cache.py`
Convert to Pydantic Settings but keep same interface:

```python
# src/ooai/core/settings/cache.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path

from .base import OOAIBaseSettings

class CacheSettings(BaseSettings):
    """Cache settings - SAME FIELDS as before."""

    model_config = SettingsConfigDict(
        env_prefix='OOAI_CACHE_',
        env_nested_delimiter='__',
        case_sensitive=False
    )

    # Keep exact same fields with same names
    cache_dir: Path = Field(
        default_factory=lambda: OOAIBaseSettings._get_config_dir() / "cache",
        description="Cache directory path"
    )
    max_cache_size_mb: int = Field(
        default=500,
        ge=10,
        le=10000,
        description="Maximum cache size in MB"
    )
    default_ttl: int = Field(
        default=3600,
        ge=0,
        description="Default TTL in seconds"
    )
    # ... rest of fields stay the same
```

#### 2.4 Update `settings/llm/settings.py`
Same approach - BaseSettings but keep interface:

```python
# src/ooai/core/settings/llm/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator
from typing import Optional, Dict, Any

from .providers import LLMProvider

class LLMSettings(BaseSettings):
    """LLM settings - SAME API as before."""

    model_config = SettingsConfigDict(
        env_prefix='OOAI_LLM_',
        env_nested_delimiter='__',
        case_sensitive=False
    )

    # Keep exact same field names
    default_provider: LLMProvider = Field(
        default=LLMProvider.MOCK,
        description="Default LLM provider"
    )
    default_model: str = Field(
        default="mock-model",
        description="Default model name"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default sampling temperature"
    )

    # API keys - now automatically loaded from env
    api_keys: Dict[LLMProvider, Optional[str]] = Field(
        default_factory=dict,
        description="Provider API keys"
    )

    # Keep this for backward compatibility
    @model_validator(mode='after')
    def validate_provider_settings(self):
        """Load API keys from environment - AUTOMATIC now."""
        # This now happens automatically!
        # But keep the method for compatibility
        return self

    def _load_api_keys_from_env(self) -> None:
        """Keep for backward compatibility but now automatic."""
        # Environment variables are loaded automatically
        # This method kept for compatibility
        pass

    # Keep all other methods unchanged
    def get_api_key(self, provider: LLMProvider) -> Optional[str]:
        """Same implementation."""
        return self.api_keys.get(provider)
```

### Step 3: Update `__init__.py` - Keep Same Exports

```python
# src/ooai/core/settings/__init__.py
"""Settings module - SAME EXPORTS as before."""

from .cache import CacheSettings, get_cache_settings, init_cache_system
from .llm import (
    LLMModel,
    LLMProvider,
    LLMSettings,
    get_llm_config_for_engine,
    get_llm_settings,
)
from .local import LocalSettings, get_local_settings, get_project_config

# EXACT SAME exports - no breaking changes
__all__ = [
    # Cache settings
    "CacheSettings",
    "get_cache_settings",
    "init_cache_system",
    # LLM settings
    "LLMSettings",
    "LLMProvider",
    "LLMModel",
    "get_llm_settings",
    "get_llm_config_for_engine",
    # Local settings
    "LocalSettings",
    "get_local_settings",
    "get_project_config",
]
```

## Key Preservation Points

### 1. Keep ALL Function Names
```python
# These stay exactly the same:
get_local_settings()
get_llm_settings()
get_cache_settings()
get_project_config()
```

### 2. Keep ALL Class Names
```python
# These stay exactly the same:
LocalSettings
LLMSettings
CacheSettings
```

### 3. Keep ALL Field Names
```python
# Don't rename any fields:
llm_settings  # NOT llm
default_model  # NOT model
max_cache_size_mb  # NOT max_size_mb
```

### 4. Keep ALL Method Signatures
```python
# These stay exactly the same:
def get_project_config(self, project_path: Union[str, Path] | None = None) -> dict[str, Any]:
def set_user_preference(self, key: str, value: Any) -> None:
```

## What Changes Under the Hood

### Automatic Environment Variable Loading
```python
# OLD: Manual loading
def _load_api_keys_from_env(self):
    for provider, env_var in env_key_map.items():
        env_value = os.getenv(env_var)
        if env_value:
            self.api_keys[provider] = env_value

# NEW: Automatic (but method kept for compatibility)
# Environment variables are loaded automatically by Pydantic Settings
```

### Validation at Load Time
```python
# OLD: No validation on environment variables
# NEW: Automatic validation when loading from env
OOAI_LLM_TEMPERATURE=3.0  # Would raise ValidationError
```

### Built-in .env Support
```python
# OLD: Manual .env loading if implemented
# NEW: Automatic .env file support
```

## Testing Updates Required

### Minimal Changes - Same API
```python
# Tests mostly stay the same!
def test_local_settings(tmp_path):
    # This still works exactly the same:
    settings = LocalSettings(
        config_dir=tmp_path / ".ooai",
        llm_settings=LLMSettings(
            default_provider=LLMProvider.OPENAI,
            default_model="gpt-4"
        )
    )

    # These assertions stay the same:
    assert settings.llm_settings.default_model == "gpt-4"
    assert settings.config_dir == tmp_path / ".ooai"

    # Methods work the same:
    settings.save_to_file()
    settings.load_from_file()
```

### New Testing Capabilities
```python
# But now you CAN also test with env vars:
def test_with_env_vars(monkeypatch):
    monkeypatch.setenv("OOAI_LLM_DEFAULT_MODEL", "claude-3")
    monkeypatch.setenv("OOAI_CACHE_MAX_CACHE_SIZE_MB", "1000")

    settings = LocalSettings()
    # Automatically loaded!
    assert settings.llm_settings.default_model == "claude-3"
    assert settings.cache_settings.max_cache_size_mb == 1000
```

## Migration Steps

### 1. Add Dependency
```toml
# pyproject.toml
[tool.pdm.dependencies]
pydantic-settings = "^2.0.0"
```

### 2. Update Files In Order
1. Create `settings/base.py`
2. Update `settings/cache.py`
3. Update `settings/llm/settings.py`
4. Update `settings/local.py`
5. Keep `settings/__init__.py` the same

### 3. Run Tests
```bash
pdm run pytest tests/settings/
```

### 4. Fix Any Issues
- Most tests should pass unchanged
- Add environment variable cleanup in tests if needed

## Advantages of Direct Overwrite

### ✅ Pros
1. **No duplicate code** - cleaner codebase
2. **No migration needed** - same API
3. **Immediate benefits** - env vars work right away
4. **Simpler maintenance** - one implementation

### ⚠️ Cons
1. **Riskier** - changing production code
2. **No fallback** - can't easily switch back
3. **All-or-nothing** - must update everything

### Mitigation
1. **Git branch** - easy rollback if needed
2. **Thorough testing** - ensure all tests pass
3. **Keep backup** - `settings_backup/` directory

## Recommendation

**Direct overwrite is feasible** because:
- We're keeping the exact same API
- All field names stay the same
- All methods stay the same
- Only the base class changes

This is essentially an **internal refactoring** that doesn't break the public API.