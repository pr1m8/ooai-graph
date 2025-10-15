# Comprehensive Code Standards & Documentation Guide

## Table of Contents

1. [Google-Style Docstrings](#google-style-docstrings)
2. [Fixture Architecture for Large Codebases](#fixture-architecture-for-large-codebases)
3. [Package Organization & Mirroring](#package-organization--mirroring)
4. [Code Writing Process](#code-writing-process)
5. [Reference Formatting](#reference-formatting)
6. [Examples & Best Practices](#examples--best-practices)

---

## Google-Style Docstrings

### Configuration for Sphinx

```python
# docs/conf.py
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_preprocess_types = True
napoleon_type_aliases = {
    "BaseEngine": "ooai.core.engine.base.BaseEngine",
    "DynamicBaseModel": "ooai.core.models.DynamicBaseModel",
}
napoleon_attr_annotations = True
```

### Module-Level Documentation

```python
"""Module for dynamic base model composition and analysis.

This module provides comprehensive functionality for creating, composing,
and analyzing dynamic Pydantic models at runtime. It implements various
composition patterns including IS-A, HAS-A, USES-A, and CONTAINS-A relationships.

The module is designed to work with large-scale applications requiring
flexible model composition and type-safe operations.

Example:
    Basic usage of the module::

        from ooai.core.models import DynamicBaseModel
        from ooai.core.models.protocols import IsAProtocol

        # Create base model
        class User(DynamicBaseModel):
            name: str
            email: str

        # Create extension
        class Employee(DynamicBaseModel):
            employee_id: str
            department: str

        # Compose models
        protocol = IsAProtocol()
        EmployeeUser = protocol.compose(Employee, User)

Note:
    This module requires Python 3.10+ and Pydantic 2.0+.
    All models inherit from `DynamicBaseModel` which extends
    Pydantic's BaseModel with composition capabilities.

Attributes:
    DEFAULT_CACHE_SIZE (int): Maximum number of composed models to cache (default: 1000)
    COMPOSITION_MODES (Enum): Available composition modes
    RELATIONSHIP_TYPES (Enum): Supported relationship types

Todo:
    * Add support for circular dependency detection
    * Implement lazy loading for large model hierarchies
    * Add composition visualization tools

See Also:
    `ooai.core.models.protocols`: Protocol implementations
    `ooai.core.models.strategies`: Composition strategies
    `ooai.core.models.analyzers`: Model analysis tools

References:
    Pydantic Documentation: https://docs.pydantic.dev/
    Composition Patterns: https://en.wikipedia.org/wiki/Object_composition

.. versionadded:: 0.1.0
    Initial implementation of dynamic model composition

.. versionchanged:: 0.2.0
    Added caching and performance optimizations

.. deprecated:: 0.3.0
    The `compose_simple` function is deprecated, use `compose` instead
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union
from enum import Enum
import logging

if TYPE_CHECKING:
    from ooai.core.engine import BaseEngine

__all__ = [
    "DynamicBaseModel",
    "CompositionMode",
    "compose_models",
    "analyze_model",
]

__version__ = "0.3.0"
__author__ = "OOAI Team"

logger = logging.getLogger(__name__)
```

### Class Documentation

```python
class DynamicBaseModel(BaseModel):
    """Base class for all dynamic models with composition capabilities.

    This class extends Pydantic's BaseModel to provide dynamic field
    management, composition protocols, and advanced validation features.
    It serves as the foundation for all composable models in the system.

    The class maintains an internal cache of composed models to optimize
    performance and provides hooks for custom validation and serialization.

    Args:
        **data: Keyword arguments for field values. Fields are validated
            according to their type annotations and validators.

    Attributes:
        _cache (Dict[str, Type]): Class-level cache for composed models
        _composition_metadata (Dict[str, Any]): Metadata about model composition
        _field_validators (Dict[str, Callable]): Custom field validators
        _model_config (ConfigDict): Pydantic model configuration

    Example:
        Creating a simple dynamic model::

            class User(DynamicBaseModel):
                name: str
                email: EmailStr
                age: Optional[int] = None

            user = User(name="John", email="john@example.com")
            print(user.model_dump())
            # {'name': 'John', 'email': 'john@example.com', 'age': None}

        Using with composition::

            class Address(DynamicBaseModel):
                street: str
                city: str
                country: str = "USA"

            # Compose User with Address
            UserWithAddress = compose_models(User, Address, mode="HAS_A")

            instance = UserWithAddress(
                name="Jane",
                email="jane@example.com",
                address={"street": "123 Main St", "city": "NYC"}
            )

    Note:
        - All fields must have type annotations
        - Validators are inherited through composition
        - The class uses `__slots__` for memory efficiency
        - Thread-safe caching is implemented for composed models

    Raises:
        ValidationError: If field validation fails
        CompositionError: If model composition is invalid
        TypeError: If invalid types are provided

    See Also:
        `BaseModel`: Pydantic's base model class
        `compose_models`: Function for composing models
        `CompositionProtocol`: Protocol interface for composition

    .. versionadded:: 0.1.0
        Initial implementation

    .. versionchanged:: 0.2.0
        Added caching and performance improvements

    """

    # Class variables with type hints
    _cache: ClassVar[Dict[str, Type["DynamicBaseModel"]]] = {}
    _composition_metadata: ClassVar[Dict[str, Any]] = {}

    def __init__(self, **data: Any) -> None:
        """Initialize the dynamic base model with field values.

        Args:
            **data: Field values as keyword arguments. Each argument
                must correspond to a defined field in the model.

        Raises:
            ValidationError: If any field fails validation
            TypeError: If unknown fields are provided (when extra="forbid")

        Example:
            >>> model = DynamicBaseModel(field1="value", field2=42)
            >>> print(model.field1)
            'value'
        """
        super().__init__(**data)
        self._post_init_setup()

    def _post_init_setup(self) -> None:
        """Perform post-initialization setup.

        This method is called after the model is initialized and validated.
        Override this method in subclasses to add custom initialization logic.

        Note:
            This method should not modify field values directly.
            Use validators or computed fields for value transformations.
        """
        pass

    @classmethod
    def create_model(
        cls,
        name: str,
        *,
        __base__: Optional[Type["DynamicBaseModel"]] = None,
        __module__: Optional[str] = None,
        __validators__: Optional[Dict[str, Callable]] = None,
        **fields: Tuple[Type, Any]
    ) -> Type["DynamicBaseModel"]:
        """Dynamically create a new model class with specified fields.

        This method creates a new model class at runtime with the given
        name and field definitions. The created class inherits from
        DynamicBaseModel or a specified base class.

        Args:
            name: Name of the new model class
            __base__: Optional base class (defaults to cls)
            __module__: Optional module name for the class
            __validators__: Optional dictionary of validators
            **fields: Field definitions as (type, default) tuples

        Returns:
            A new model class with the specified fields

        Raises:
            TypeError: If field definitions are invalid
            ValueError: If the name conflicts with existing attributes

        Example:
            Creating a model dynamically::

                User = DynamicBaseModel.create_model(
                    "User",
                    name=(str, ...),
                    email=(EmailStr, ...),
                    age=(Optional[int], None),
                    is_active=(bool, True)
                )

                user = User(name="John", email="john@example.com")
                print(user.model_dump())

            With validators::

                def validate_age(cls, v):
                    if v < 0:
                        raise ValueError("Age must be positive")
                    return v

                Person = DynamicBaseModel.create_model(
                    "Person",
                    __validators__={"age": validate_age},
                    name=(str, ...),
                    age=(int, ...)
                )

        Note:
            - Field order is preserved in Python 3.7+
            - The `...` sentinel indicates a required field
            - Validators are applied in definition order

        See Also:
            `pydantic.create_model`: Underlying Pydantic function
            `Field`: For advanced field configuration
        """
        base = __base__ or cls
        namespace = {"__module__": __module__ or cls.__module__}

        # Add validators if provided
        if __validators__:
            for field_name, validator in __validators__.items():
                namespace[f"validate_{field_name}"] = field_validator(field_name)(validator)

        # Process field definitions
        annotations = {}
        defaults = {}
        for field_name, field_info in fields.items():
            if isinstance(field_info, tuple):
                field_type, default = field_info
                annotations[field_name] = field_type
                if default is not ...:
                    defaults[field_name] = default
            else:
                raise TypeError(f"Invalid field definition for {field_name}")

        namespace["__annotations__"] = annotations
        namespace.update(defaults)

        # Create the model class
        model_class = type(name, (base,), namespace)

        # Cache the created model
        cache_key = f"{name}_{id(fields)}"
        cls._cache[cache_key] = model_class

        return model_class
```

### Method Documentation

```python
def compose_models(
    base_model: Type[DynamicBaseModel],
    mixin_model: Type[DynamicBaseModel],
    mode: Union[str, CompositionMode],
    *,
    name: Optional[str] = None,
    conflict_resolution: str = "override",
    validators: Optional[Dict[str, Callable]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Type[DynamicBaseModel]:
    """Compose two models into a new model using the specified mode.

    This function is the primary interface for model composition. It supports
    multiple composition modes and provides fine-grained control over field
    conflicts, validation, and metadata handling.

    Args:
        base_model: The base model class to extend
        mixin_model: The model to compose with the base
        mode: Composition mode - either a string ("INGEST", "ADD", etc.)
            or a CompositionMode enum value
        name: Optional name for the composed model. If not provided,
            a name is generated as "{Base}{Mixin}{Mode}"
        conflict_resolution: Strategy for resolving field conflicts:
            - "override": Mixin fields override base fields
            - "keep": Base fields are kept, mixin fields ignored
            - "merge": Attempt to merge field definitions
            - "error": Raise an error on conflicts
        validators: Additional validators for the composed model
        metadata: Additional metadata to attach to the model

    Returns:
        A new model class combining both input models according
        to the specified composition mode.

    Raises:
        CompositionError: If the models cannot be composed
        ValueError: If an invalid mode or conflict resolution is specified
        TypeError: If the input models are not DynamicBaseModel subclasses

    Example:
        Basic composition::

            class Person(DynamicBaseModel):
                name: str
                age: int

            class Employee(DynamicBaseModel):
                employee_id: str
                salary: float

            # IS-A composition (inheritance-like)
            EmployeePerson = compose_models(
                Employee, Person,
                mode="INGEST",
                name="EmployeePerson"
            )

            emp = EmployeePerson(
                name="Alice",
                age=30,
                employee_id="E123",
                salary=75000.0
            )

        With conflict resolution::

            class Model1(DynamicBaseModel):
                field: str = "from_model1"
                unique1: int

            class Model2(DynamicBaseModel):
                field: str = "from_model2"
                unique2: float

            # Override strategy
            Composed1 = compose_models(
                Model1, Model2,
                mode="INGEST",
                conflict_resolution="override"
            )
            # field will be from Model2

            # Keep strategy
            Composed2 = compose_models(
                Model1, Model2,
                mode="INGEST",
                conflict_resolution="keep"
            )
            # field will be from Model1

    Note:
        - Composition is cached for performance
        - Validators are combined from both models
        - Field order is preserved where possible
        - Type annotations are properly maintained

    See Also:
        `CompositionMode`: Available composition modes
        `CompositionProtocol`: Protocol interface
        `analyze_models`: For analyzing composition compatibility

    .. versionadded:: 0.1.0
        Initial implementation

    .. versionchanged:: 0.2.0
        Added conflict resolution strategies
    """
    # Implementation details...
    pass
```

### Property Documentation

```python
class ModelAnalyzer:
    """Analyzer for model structure and relationships."""

    @property
    def field_count(self) -> int:
        """Get the total number of fields in the model.

        Returns:
            The count of all fields defined in the model,
            including inherited and composed fields.

        Example:
            >>> analyzer = ModelAnalyzer(MyModel)
            >>> print(f"Model has {analyzer.field_count} fields")
            Model has 5 fields

        Note:
            This includes optional fields and computed fields.

        .. versionadded:: 0.1.0
        """
        return len(self._model.model_fields)

    @property
    def required_fields(self) -> List[str]:
        """Get list of required field names.

        Returns:
            List of field names that are required (no default value).

        Example:
            >>> analyzer.required_fields
            ['name', 'email', 'employee_id']

        See Also:
            `optional_fields`: For fields with defaults
        """
        return [
            name for name, field in self._model.model_fields.items()
            if field.is_required()
        ]

    @field_count.setter
    def field_count(self, value: int) -> None:
        """Setter should not be used - field_count is read-only.

        Raises:
            AttributeError: Always raised as field_count is read-only

        Note:
            This setter exists only for documentation purposes.
            The field_count is computed dynamically and cannot be set.
        """
        raise AttributeError("field_count is read-only")
```

---

## Fixture Architecture for Large Codebases

### Directory Structure for Fixtures

```
project/
├── src/
│   └── ooai/
│       ├── core/
│       │   ├── models/
│       │   ├── engine/
│       │   └── utils/
│       └── __init__.py
│
├── tests/
│   ├── conftest.py              # Root fixtures (global)
│   ├── fixtures/                # Modular fixture organization
│   │   ├── __init__.py
│   │   ├── models.py            # Model-specific fixtures
│   │   ├── engines.py           # Engine-specific fixtures
│   │   ├── databases.py         # Database fixtures
│   │   ├── api_clients.py       # API client fixtures
│   │   └── factories.py         # Factory fixtures
│   │
│   ├── unit/
│   │   ├── conftest.py          # Unit test specific fixtures
│   │   ├── models/
│   │   │   ├── conftest.py      # Model test fixtures
│   │   │   └── test_*.py
│   │   └── engine/
│   │       ├── conftest.py      # Engine test fixtures
│   │       └── test_*.py
│   │
│   ├── integration/
│   │   ├── conftest.py          # Integration test fixtures
│   │   └── test_*.py
│   │
│   └── e2e/
│       ├── conftest.py          # E2E test fixtures
│       └── test_*.py
```

### Root conftest.py (Global Fixtures)

```python
"""Root test configuration and global fixtures.

This module provides fixtures available to all tests in the project.
It sets up the test environment, configures logging, and provides
access to commonly used resources.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Generator, Any, Dict, Optional
import pytest
from unittest.mock import Mock, MagicMock

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/test.log'),
        logging.StreamHandler()
    ]
)

# Load fixtures from modular files
pytest_plugins = [
    "tests.fixtures.models",
    "tests.fixtures.engines",
    "tests.fixtures.databases",
    "tests.fixtures.api_clients",
    "tests.fixtures.factories",
]


# =============================================================================
# Session-Scoped Fixtures (Expensive Setup)
# =============================================================================

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Provide test configuration loaded once per session.

    Returns:
        Dictionary containing test configuration values.

    Example:
        def test_with_config(test_config):
            api_key = test_config["api_key"]
            assert api_key is not None
    """
    return {
        "api_key": os.environ.get("TEST_API_KEY", "test-key"),
        "database_url": os.environ.get("TEST_DB_URL", "sqlite:///test.db"),
        "cache_dir": Path("tests/.cache"),
        "timeout": 30,
        "max_retries": 3,
    }


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide path to test data directory.

    Returns:
        Path to the test data directory.

    Note:
        Creates the directory if it doesn't exist.
    """
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


# =============================================================================
# Module-Scoped Fixtures (Shared Within Module)
# =============================================================================

@pytest.fixture(scope="module")
def shared_cache() -> Dict[str, Any]:
    """Provide a cache shared within a test module.

    Returns:
        Dictionary for caching expensive computations.

    Example:
        def test_with_cache(shared_cache):
            if "result" not in shared_cache:
                shared_cache["result"] = expensive_computation()
            assert shared_cache["result"] is not None
    """
    cache = {}
    yield cache
    # Cleanup after module
    cache.clear()


# =============================================================================
# Function-Scoped Fixtures (Fresh for Each Test)
# =============================================================================

@pytest.fixture
def temp_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary workspace for test files.

    Args:
        tmp_path: Pytest's built-in temp directory fixture

    Yields:
        Path to temporary workspace directory

    Example:
        def test_file_operations(temp_workspace):
            file_path = temp_workspace / "test.txt"
            file_path.write_text("content")
            assert file_path.exists()
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Setup workspace structure
    (workspace / "input").mkdir()
    (workspace / "output").mkdir()
    (workspace / "cache").mkdir()

    original_cwd = Path.cwd()
    os.chdir(workspace)

    yield workspace

    # Cleanup
    os.chdir(original_cwd)


@pytest.fixture
def mock_logger() -> Mock:
    """Provide a mock logger for testing logging behavior.

    Returns:
        Mock logger instance with common methods mocked.

    Example:
        def test_logging(mock_logger):
            my_function(logger=mock_logger)
            mock_logger.info.assert_called_once()
    """
    logger = Mock(spec=logging.Logger)
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


# =============================================================================
# Autouse Fixtures (Automatic Setup/Teardown)
# =============================================================================

@pytest.fixture(autouse=True)
def reset_singletons():
    """Automatically reset singleton instances between tests.

    This fixture runs before each test to ensure clean state.

    Note:
        This is an autouse fixture - no need to include in test parameters.
    """
    # Reset any singleton instances
    from ooai.core.models import DynamicBaseModel
    DynamicBaseModel.clear_cache()

    yield

    # Additional cleanup if needed
    DynamicBaseModel.clear_cache()


@pytest.fixture(autouse=True)
def capture_warnings():
    """Automatically capture and report warnings in tests.

    Note:
        Warnings are captured and can be inspected using pytest.warns()
    """
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("always")
        yield


# =============================================================================
# Parametrized Fixtures
# =============================================================================

@pytest.fixture(params=["json", "yaml", "xml"])
def data_format(request) -> str:
    """Provide different data formats for testing.

    Args:
        request: Pytest request object containing parameter

    Returns:
        Data format string

    Example:
        def test_serialization(data_format):
            # Test runs 3 times with different formats
            serialized = serialize(data, format=data_format)
            assert serialized is not None
    """
    return request.param


@pytest.fixture(params=[1, 10, 100, 1000])
def batch_size(request) -> int:
    """Provide different batch sizes for performance testing.

    Args:
        request: Pytest request object

    Returns:
        Batch size integer

    Example:
        def test_batch_processing(batch_size):
            results = process_batch(data[:batch_size])
            assert len(results) == batch_size
    """
    return request.param
```

### Modular Fixtures (tests/fixtures/models.py)

```python
"""Model-specific fixtures for testing.

This module provides fixtures for creating and managing test models,
including factories, builders, and common model configurations.
"""

from typing import Type, Dict, Any, List
import pytest
from ooai.core.models import DynamicBaseModel


class ModelFixtures:
    """Container for model fixture methods."""

    @staticmethod
    def create_simple_model() -> Type[DynamicBaseModel]:
        """Create a simple test model.

        Returns:
            A simple DynamicBaseModel subclass

        Example:
            model_class = ModelFixtures.create_simple_model()
            instance = model_class(name="test", value=42)
        """
        class SimpleModel(DynamicBaseModel):
            name: str
            value: int = 0

        return SimpleModel

    @staticmethod
    def create_complex_model() -> Type[DynamicBaseModel]:
        """Create a complex model with multiple field types.

        Returns:
            A complex DynamicBaseModel with various field types
        """
        from typing import Optional, List, Dict
        from datetime import datetime

        class ComplexModel(DynamicBaseModel):
            id: str
            name: str
            age: Optional[int] = None
            tags: List[str] = []
            metadata: Dict[str, Any] = {}
            created_at: datetime = None
            is_active: bool = True

        return ComplexModel


@pytest.fixture(scope="session")
def model_fixtures_factory() -> ModelFixtures:
    """Provide ModelFixtures factory.

    Returns:
        ModelFixtures instance for creating test models

    Example:
        def test_with_factory(model_fixtures_factory):
            model = model_fixtures_factory.create_simple_model()
            assert model.__name__ == "SimpleModel"
    """
    return ModelFixtures()


@pytest.fixture
def simple_model() -> Type[DynamicBaseModel]:
    """Provide a simple test model.

    Returns:
        Simple DynamicBaseModel class

    Example:
        def test_simple(simple_model):
            instance = simple_model(name="test", value=10)
            assert instance.name == "test"
    """
    return ModelFixtures.create_simple_model()


@pytest.fixture
def complex_model() -> Type[DynamicBaseModel]:
    """Provide a complex test model.

    Returns:
        Complex DynamicBaseModel class with multiple field types

    Example:
        def test_complex(complex_model):
            instance = complex_model(id="1", name="test")
            assert instance.is_active is True
    """
    return ModelFixtures.create_complex_model()


@pytest.fixture
def model_hierarchy() -> Dict[str, Type[DynamicBaseModel]]:
    """Provide a hierarchy of related models.

    Returns:
        Dictionary of related model classes

    Example:
        def test_hierarchy(model_hierarchy):
            base = model_hierarchy["base"]
            child = model_hierarchy["child"]
            assert issubclass(child, base)
    """
    class BaseModel(DynamicBaseModel):
        id: str
        created_at: str

    class ChildModel(BaseModel):
        name: str
        parent_id: str

    class GrandchildModel(ChildModel):
        detail: str
        level: int = 3

    return {
        "base": BaseModel,
        "child": ChildModel,
        "grandchild": GrandchildModel
    }


@pytest.fixture
def model_with_validators() -> Type[DynamicBaseModel]:
    """Provide a model with custom validators.

    Returns:
        Model class with field validators

    Example:
        def test_validation(model_with_validators):
            with pytest.raises(ValueError):
                model_with_validators(email="invalid", age=-1)
    """
    from pydantic import field_validator, EmailStr

    class ValidatedModel(DynamicBaseModel):
        email: EmailStr
        age: int
        score: float

        @field_validator("age")
        def validate_age(cls, v):
            if v < 0 or v > 150:
                raise ValueError("Age must be between 0 and 150")
            return v

        @field_validator("score")
        def validate_score(cls, v):
            if not 0 <= v <= 100:
                raise ValueError("Score must be between 0 and 100")
            return v

    return ValidatedModel
```

### Package Mirroring for Tests

```python
"""Test structure mirroring package structure.

tests/
├── unit/
│   ├── core/                    # Mirrors src/ooai/core/
│   │   ├── models/              # Mirrors src/ooai/core/models/
│   │   │   ├── conftest.py
│   │   │   ├── test_dynamic_base_model.py
│   │   │   └── test_protocols.py
│   │   ├── engine/              # Mirrors src/ooai/core/engine/
│   │   │   ├── conftest.py
│   │   │   └── test_base.py
│   │   └── utils/               # Mirrors src/ooai/core/utils/
│   │       ├── conftest.py
│   │       └── test_helpers.py
│   └── conftest.py
"""

# tests/unit/core/models/conftest.py
"""Fixtures specific to model unit tests."""

import pytest
from typing import Type
from ooai.core.models import DynamicBaseModel


@pytest.fixture
def isolated_model_class() -> Type[DynamicBaseModel]:
    """Provide an isolated model class for testing.

    This fixture creates a fresh model class for each test,
    ensuring no cross-test contamination.

    Returns:
        Fresh DynamicBaseModel subclass

    Example:
        def test_isolated(isolated_model_class):
            # This model is unique to this test
            isolated_model_class.add_field("test", str)
    """
    class IsolatedModel(DynamicBaseModel):
        pass

    # Clear any cached data
    IsolatedModel._cache.clear()

    return IsolatedModel


@pytest.fixture
def model_test_suite() -> Dict[str, Any]:
    """Provide a complete test suite for model testing.

    Returns:
        Dictionary containing test models, data, and validators

    Example:
        def test_suite(model_test_suite):
            model = model_test_suite["model"]
            data = model_test_suite["valid_data"]
            instance = model(**data)
    """
    from datetime import datetime

    class TestModel(DynamicBaseModel):
        name: str
        value: int
        timestamp: datetime

    return {
        "model": TestModel,
        "valid_data": {
            "name": "test",
            "value": 42,
            "timestamp": datetime.now()
        },
        "invalid_data": {
            "name": 123,  # Wrong type
            "value": "not an int",  # Wrong type
            "timestamp": "not a datetime"
        },
        "partial_data": {
            "name": "partial"
            # Missing required fields
        }
    }
```

---

## Package Organization & Mirroring

### Monorepo Structure

```
ooai-monorepo/
├── packages/
│   ├── ooai-core/              # Core functionality
│   │   ├── src/
│   │   ├── tests/
│   │   ├── docs/
│   │   └── pyproject.toml
│   │
│   ├── ooai-langchain/          # LangChain integration
│   │   ├── src/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   └── ooai-ui/                 # UI components
│       ├── src/
│       ├── tests/
│       └── package.json
│
├── shared/                      # Shared test utilities
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── common.py
│   └── conftest.py
│
├── integration/                 # Cross-package integration tests
│   ├── conftest.py
│   └── test_*.py
│
└── pyproject.toml              # Root configuration
```

### Shared Fixtures Across Packages

```python
# shared/conftest.py
"""Shared fixtures for all packages in the monorepo."""

import pytest
from pathlib import Path
from typing import Dict, Any

# Make shared fixtures available as a plugin
pytest_plugins = ["shared.fixtures.common"]


@pytest.fixture(scope="session")
def monorepo_root() -> Path:
    """Provide path to monorepo root.

    Returns:
        Path to the monorepo root directory

    Example:
        def test_with_root(monorepo_root):
            config = monorepo_root / "pyproject.toml"
            assert config.exists()
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def packages_dir(monorepo_root: Path) -> Path:
    """Provide path to packages directory.

    Args:
        monorepo_root: Root directory fixture

    Returns:
        Path to packages directory

    Example:
        def test_packages(packages_dir):
            core_package = packages_dir / "ooai-core"
            assert core_package.exists()
    """
    return monorepo_root / "packages"


@pytest.fixture
def cross_package_imports() -> Dict[str, Any]:
    """Provide imports from multiple packages.

    Returns:
        Dictionary of imported modules from different packages

    Example:
        def test_integration(cross_package_imports):
            core = cross_package_imports["core"]
            langchain = cross_package_imports["langchain"]
            # Test integration between packages
    """
    imports = {}

    try:
        from ooai.core import models
        imports["core"] = models
    except ImportError:
        imports["core"] = None

    try:
        from ooai.langchain import chains
        imports["langchain"] = chains
    except ImportError:
        imports["langchain"] = None

    return imports
```

### Package-Specific Test Organization

```python
# packages/ooai-core/tests/conftest.py
"""Test configuration for ooai-core package."""

import sys
from pathlib import Path

# Add package src to path
package_root = Path(__file__).parent.parent
src_path = package_root / "src"
sys.path.insert(0, str(src_path))

# Import shared fixtures if in monorepo
try:
    shared_path = package_root.parent.parent / "shared"
    sys.path.insert(0, str(shared_path))
    from shared.fixtures import common
    pytest_plugins = ["shared.fixtures.common"]
except ImportError:
    # Not in monorepo structure, use local fixtures only
    pass


# Package-specific fixtures
@pytest.fixture
def core_config() -> Dict[str, Any]:
    """Provide ooai-core specific configuration.

    Returns:
        Configuration dictionary for core package

    Example:
        def test_core(core_config):
            assert core_config["version"] == "0.1.0"
    """
    return {
        "version": "0.1.0",
        "package_name": "ooai-core",
        "features": ["models", "engine", "protocols"]
    }
```

---

## Code Writing Process

### Development Workflow

```python
"""Standard development workflow for writing production code.

Process:
1. Design Phase
2. Implementation Phase
3. Testing Phase
4. Documentation Phase
5. Review Phase
"""


class DevelopmentProcess:
    """Encapsulates the development workflow."""

    def design_phase(self) -> None:
        """Design phase: Plan before coding.

        Steps:
            1. Define clear requirements
            2. Create interface/API design
            3. Document expected behavior
            4. Plan test cases

        Example:
            # Before implementing a new feature
            '''
            Feature: Model Composition
            Requirements:
                - Support IS-A relationships
                - Support HAS-A relationships
                - Handle field conflicts
                - Maintain type safety

            API Design:
                compose_models(base, mixin, mode="IS-A")

            Test Cases:
                - Simple composition
                - Field conflict resolution
                - Validation preservation
                - Error handling
            '''

        Note:
            Always write the docstring first, then implement.
        """
        pass

    def implementation_phase(self) -> None:
        """Implementation phase: Write clean, documented code.

        Guidelines:
            1. Start with docstring
            2. Define types for all parameters
            3. Use descriptive variable names
            4. Add inline comments for complex logic
            5. Handle edge cases explicitly

        Example:
            def process_data(
                input_data: List[Dict[str, Any]],
                processor: Callable[[Dict], Dict],
                *,
                validate: bool = True,
                batch_size: int = 100
            ) -> List[Dict[str, Any]]:
                '''Process data in batches with optional validation.

                Args:
                    input_data: List of data dictionaries to process
                    processor: Function to process each item
                    validate: Whether to validate processed data
                    batch_size: Size of processing batches

                Returns:
                    List of processed data dictionaries

                Raises:
                    ValidationError: If validation fails
                    ProcessingError: If processor fails
                '''
                results = []

                # Process in batches for memory efficiency
                for i in range(0, len(input_data), batch_size):
                    batch = input_data[i:i + batch_size]

                    # Process each item with error handling
                    for item in batch:
                        try:
                            processed = processor(item)

                            # Validate if requested
                            if validate:
                                self._validate_item(processed)

                            results.append(processed)
                        except Exception as e:
                            # Log and re-raise with context
                            logger.error(f"Failed processing item: {item}")
                            raise ProcessingError(f"Processing failed: {e}") from e

                return results

        Note:
            Code should be self-documenting through good naming.
        """
        pass

    def testing_phase(self) -> None:
        """Testing phase: Comprehensive test coverage.

        Test Types:
            1. Unit tests for individual functions
            2. Integration tests for component interaction
            3. Property tests for edge cases
            4. Performance tests for benchmarks

        Example:
            class TestModelComposition:
                '''Test suite for model composition.'''

                def test_simple_composition(self, simple_model):
                    '''Test basic model composition.'''
                    composed = compose_models(
                        simple_model,
                        AnotherModel,
                        mode="IS-A"
                    )
                    assert "field" in composed.model_fields

                @pytest.mark.parametrize("mode", ["IS-A", "HAS-A"])
                def test_composition_modes(self, mode):
                    '''Test different composition modes.'''
                    result = compose_models(Base, Mixin, mode=mode)
                    assert result is not None

                @given(fields=field_strategy())
                def test_property_composition(self, fields):
                    '''Property test for composition.'''
                    # Test with random field configurations
                    pass

        Note:
            Always test both success and failure cases.
        """
        pass
```

---

## Reference Formatting

### Object References with Backticks

```python
"""Proper reference formatting in documentation.

When referencing code objects in docstrings, use backticks to create
proper references that tools can understand and link.

Formatting Rules:
    - Single backticks for inline code: `variable_name`
    - Double backticks for literals: ``None``, ``...``
    - Triple backticks for code blocks (in module docstrings)
    - Use full paths for cross-module references

Examples:
    Inline references::

        The `DynamicBaseModel` class provides composition.
        Returns `None` if not found.
        The ``...`` sentinel indicates required fields.

    Parameter references::

        Args:
            model (`Type[DynamicBaseModel]`): The model class
            data (`Dict[str, Any]`): Input data dictionary
            validate (`bool`, optional): Whether to validate. Defaults to `True`.

    Return references::

        Returns:
            `ModelInstance`: The created instance
            `Optional[str]`: The value or `None`
            `List[Type[DynamicBaseModel]]`: List of model classes

    Cross-references::

        See Also:
            `ooai.core.models.DynamicBaseModel`: Base model class
            `ooai.core.protocols.CompositionProtocol`: Protocol interface
            :class:`~ooai.core.engine.BaseEngine`: Engine base class
            :func:`~ooai.core.compose_models`: Composition function
            :mod:`ooai.core.validators`: Validation module

Notes:
    - Use `~` for abbreviated paths in Sphinx
    - Use full module paths for clarity
    - Link to related objects liberally
"""


def example_with_references(
    model: Type[DynamicBaseModel],
    config: Optional[Dict[str, Any]] = None
) -> Optional[DynamicBaseModel]:
    """Create model instance with configuration.

    This function creates an instance of the given `model` class
    using the provided `config` dictionary. If `config` is `None`,
    default values are used.

    Args:
        model (`Type[DynamicBaseModel]`): The model class to instantiate.
            Must be a subclass of `DynamicBaseModel`.
        config (`Optional[Dict[str, Any]]`, optional): Configuration dictionary
            containing field values. Defaults to `None`.

    Returns:
        `Optional[DynamicBaseModel]`: The created model instance, or `None`
            if instantiation fails.

    Raises:
        `ValidationError`: If the configuration contains invalid values.
        `TypeError`: If `model` is not a `DynamicBaseModel` subclass.

    Example:
        Using with configuration::

            from ooai.core.models import DynamicBaseModel

            class MyModel(DynamicBaseModel):
                name: str
                value: int = 0

            # Create with config
            instance = example_with_references(
                MyModel,
                config={"name": "test", "value": 42}
            )
            assert instance.name == "test"

            # Create with defaults
            instance = example_with_references(MyModel)
            assert instance is None  # Fails without required fields

    Note:
        The function validates all fields according to the model's
        validators. See `DynamicBaseModel.model_validate` for details.

    See Also:
        `DynamicBaseModel`: The base model class
        `DynamicBaseModel.model_validate`: Validation method
        `ValidationError`: Exception raised on validation failure

    .. versionadded:: 0.1.0
        Initial implementation

    .. versionchanged:: 0.2.0
        Added support for `None` config parameter
    """
    if not issubclass(model, DynamicBaseModel):
        raise TypeError(f"`model` must be a `DynamicBaseModel` subclass, got {model}")

    if config is None:
        # Try to create with defaults only
        try:
            return model()
        except ValidationError:
            return None

    try:
        return model(**config)
    except ValidationError as e:
        logger.warning(f"Validation failed for {model.__name__}: {e}")
        raise
```

---

## Examples & Best Practices

### Complete Module Example

```python
"""Advanced model composition module.

This module implements sophisticated model composition patterns
with full type safety, validation, and caching support.

The module provides:
    - Dynamic model composition
    - Protocol-based relationships
    - Conflict resolution strategies
    - Performance optimization through caching

Example:
    Basic usage::

        from ooai.core.advanced import AdvancedComposer

        composer = AdvancedComposer()

        # Compose with strategy
        Result = composer.compose(
            BaseModel,
            MixinModel,
            strategy="deep_merge"
        )

Note:
    This module requires Python 3.10+ for full type support.

.. moduleauthor:: OOAI Team <team@ooai.dev>
.. versionadded:: 0.3.0
"""

from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    overload,
    runtime_checkable
)
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache, wraps
import weakref

from pydantic import BaseModel, Field, field_validator, model_validator

if TYPE_CHECKING:
    from ooai.core.engine import BaseEngine

# Module level constants
DEFAULT_CACHE_SIZE: int = 1000
MAX_COMPOSITION_DEPTH: int = 10

# Type variables for generic types
T = TypeVar("T", bound=BaseModel)
M = TypeVar("M", bound="ModelProtocol")

# Module logger
logger = logging.getLogger(__name__)

__all__ = [
    "AdvancedComposer",
    "CompositionStrategy",
    "ModelProtocol",
    "compose_with_strategy",
    "AdvancedCompositionError",
]


# =============================================================================
# Exceptions
# =============================================================================

class AdvancedCompositionError(Exception):
    """Raised when advanced composition fails.

    This exception provides detailed information about composition
    failures, including the models involved and the specific issue.

    Attributes:
        base_model (`Type[BaseModel]`): The base model in composition
        mixin_model (`Type[BaseModel]`): The mixin model in composition
        strategy (`str`): The strategy that failed
        details (`Dict[str, Any]`): Additional error details

    Example:
        >>> try:
        ...     composer.compose(Model1, Model2, strategy="invalid")
        ... except AdvancedCompositionError as e:
        ...     print(f"Composition failed: {e}")
        ...     print(f"Base model: {e.base_model.__name__}")
        ...     print(f"Strategy: {e.strategy}")
    """

    def __init__(
        self,
        message: str,
        base_model: Type[BaseModel],
        mixin_model: Type[BaseModel],
        strategy: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the exception with context.

        Args:
            message: Error message
            base_model: Base model class
            mixin_model: Mixin model class
            strategy: Strategy name that failed
            details: Additional error details
        """
        super().__init__(message)
        self.base_model = base_model
        self.mixin_model = mixin_model
        self.strategy = strategy
        self.details = details or {}


# =============================================================================
# Protocols and Enums
# =============================================================================

@runtime_checkable
class ModelProtocol(Protocol):
    """Protocol defining the interface for composable models.

    Any class implementing this protocol can be used with
    the advanced composition system.

    Example:
        >>> class MyModel(BaseModel):
        ...     def get_field_names(self) -> List[str]:
        ...         return list(self.model_fields.keys())
        ...
        ...     def get_validators(self) -> Dict[str, Callable]:
        ...         return self.__validators__
        ...
        >>> assert isinstance(MyModel, ModelProtocol)
    """

    def get_field_names(self) -> List[str]:
        """Get list of field names.

        Returns:
            List of field name strings
        """
        ...

    def get_validators(self) -> Dict[str, Callable]:
        """Get field validators.

        Returns:
            Dictionary mapping field names to validator functions
        """
        ...


class CompositionStrategy(Enum):
    """Available composition strategies.

    Each strategy defines how fields from multiple models
    are combined into a single model.

    Attributes:
        SHALLOW_MERGE: Simple field merging, last wins
        DEEP_MERGE: Recursive merging of nested structures
        UNION: Create union types for conflicting fields
        INTERSECTION: Keep only common fields
        SYMMETRIC_DIFFERENCE: Keep only unique fields

    Example:
        >>> strategy = CompositionStrategy.DEEP_MERGE
        >>> composed = composer.compose(Base, Mixin, strategy=strategy)
    """

    SHALLOW_MERGE = auto()
    DEEP_MERGE = auto()
    UNION = auto()
    INTERSECTION = auto()
    SYMMETRIC_DIFFERENCE = auto()


# =============================================================================
# Main Composer Class
# =============================================================================

@dataclass
class CompositionConfig:
    """Configuration for model composition.

    Attributes:
        strategy (`CompositionStrategy`): Strategy to use
        cache_result (`bool`): Whether to cache the result
        preserve_validators (`bool`): Whether to preserve validators
        conflict_resolution (`str`): How to resolve conflicts
        metadata (`Dict[str, Any]`): Additional metadata

    Example:
        >>> config = CompositionConfig(
        ...     strategy=CompositionStrategy.DEEP_MERGE,
        ...     cache_result=True,
        ...     preserve_validators=True
        ... )
    """

    strategy: CompositionStrategy = CompositionStrategy.SHALLOW_MERGE
    cache_result: bool = True
    preserve_validators: bool = True
    conflict_resolution: str = "override"
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedComposer(Generic[T]):
    """Advanced model composer with caching and strategies.

    This class provides sophisticated model composition with
    multiple strategies, caching, and comprehensive error handling.

    The composer maintains an internal cache of composed models
    to optimize repeated compositions and supports various
    composition strategies for different use cases.

    Attributes:
        cache (`weakref.WeakValueDictionary`): Weak reference cache
        _cache_hits (`int`): Number of cache hits
        _cache_misses (`int`): Number of cache misses
        _composition_count (`int`): Total compositions performed

    Example:
        Creating and using a composer::

            composer = AdvancedComposer[DynamicBaseModel]()

            # Configure composition
            config = CompositionConfig(
                strategy=CompositionStrategy.DEEP_MERGE,
                cache_result=True
            )

            # Compose models
            Result = composer.compose_with_config(
                BaseModel,
                MixinModel,
                config=config
            )

            # Check statistics
            print(f"Cache hits: {composer.cache_hits}")
            print(f"Compositions: {composer.composition_count}")

    Note:
        The composer uses weak references for caching to prevent
        memory leaks with dynamically created classes.

    See Also:
        `CompositionStrategy`: Available strategies
        `CompositionConfig`: Configuration options

    .. versionadded:: 0.3.0
        Advanced composition with strategies
    """

    # Class-level cache shared across instances
    _global_cache: ClassVar[weakref.WeakValueDictionary] = weakref.WeakValueDictionary()

    def __init__(self, cache_size: int = DEFAULT_CACHE_SIZE) -> None:
        """Initialize the composer with cache configuration.

        Args:
            cache_size: Maximum number of cached compositions.
                Use 0 to disable caching entirely.

        Example:
            >>> composer = AdvancedComposer(cache_size=500)
            >>> # Or disable caching
            >>> composer = AdvancedComposer(cache_size=0)
        """
        self.cache = weakref.WeakValueDictionary() if cache_size > 0 else {}
        self.cache_size = cache_size
        self._cache_hits = 0
        self._cache_misses = 0
        self._composition_count = 0
        logger.info(f"Initialized AdvancedComposer with cache_size={cache_size}")

    @property
    def cache_hits(self) -> int:
        """Get number of cache hits.

        Returns:
            Number of times a cached result was used

        Example:
            >>> if composer.cache_hits > 100:
            ...     print("Cache is being effective")
        """
        return self._cache_hits

    @property
    def cache_misses(self) -> int:
        """Get number of cache misses.

        Returns:
            Number of times composition was computed

        Example:
            >>> hit_rate = composer.cache_hits / (
            ...     composer.cache_hits + composer.cache_misses
            ... )
        """
        return self._cache_misses

    @property
    def composition_count(self) -> int:
        """Get total number of compositions performed.

        Returns:
            Total composition operations (cached or computed)

        Example:
            >>> print(f"Total: {composer.composition_count}")
        """
        return self._composition_count

    @overload
    def compose(
        self,
        base: Type[T],
        mixin: Type[BaseModel],
        *,
        strategy: str = "shallow_merge"
    ) -> Type[T]:
        """Compose models with string strategy name."""
        ...

    @overload
    def compose(
        self,
        base: Type[T],
        mixin: Type[BaseModel],
        *,
        strategy: CompositionStrategy = CompositionStrategy.SHALLOW_MERGE
    ) -> Type[T]:
        """Compose models with enum strategy."""
        ...

    def compose(
        self,
        base: Type[T],
        mixin: Type[BaseModel],
        *,
        strategy: Union[str, CompositionStrategy] = "shallow_merge"
    ) -> Type[T]:
        """Compose two models using the specified strategy.

        This method is the main entry point for model composition.
        It supports both string and enum strategy specification
        and handles caching automatically.

        Args:
            base: Base model class to extend
            mixin: Mixin model to compose with base
            strategy: Composition strategy (name or enum).
                Options: "shallow_merge", "deep_merge", "union",
                "intersection", "symmetric_difference"

        Returns:
            New model class combining both inputs according
            to the specified strategy.

        Raises:
            `AdvancedCompositionError`: If composition fails
            `ValueError`: If invalid strategy specified
            `TypeError`: If inputs are not model classes

        Example:
            Simple composition::

                # Using string strategy
                Result1 = composer.compose(
                    BaseModel,
                    MixinModel,
                    strategy="deep_merge"
                )

                # Using enum strategy
                Result2 = composer.compose(
                    BaseModel,
                    MixinModel,
                    strategy=CompositionStrategy.UNION
                )

                # Create instances
                instance = Result1(field1="value", field2=42)

            With error handling::

                try:
                    Result = composer.compose(
                        Model1,
                        Model2,
                        strategy="union"
                    )
                except AdvancedCompositionError as e:
                    logger.error(f"Failed: {e}")
                    # Handle specific error

        Note:
            - Results are cached for repeated compositions
            - Field order is preserved where possible
            - Validators are combined based on strategy
            - Type annotations are properly maintained

        See Also:
            `CompositionStrategy`: Available strategies
            `compose_with_config`: More control over composition
        """
        self._composition_count += 1

        # Convert string to enum if needed
        if isinstance(strategy, str):
            try:
                strategy = CompositionStrategy[strategy.upper()]
            except KeyError:
                raise ValueError(f"Invalid strategy: {strategy}")

        # Check cache
        cache_key = self._get_cache_key(base, mixin, strategy)
        if cache_key in self.cache:
            self._cache_hits += 1
            logger.debug(f"Cache hit for {cache_key}")
            return self.cache[cache_key]

        self._cache_misses += 1

        # Perform composition
        try:
            result = self._perform_composition(base, mixin, strategy)

            # Cache result
            if self.cache_size > 0:
                self.cache[cache_key] = result

            return result

        except Exception as e:
            raise AdvancedCompositionError(
                f"Composition failed: {e}",
                base_model=base,
                mixin_model=mixin,
                strategy=strategy.name,
                details={"error": str(e)}
            )

    @contextmanager
    def batch_composition(self) -> Generator[None, None, None]:
        """Context manager for batch composition operations.

        This context manager optimizes multiple composition
        operations by deferring cache cleanup and validation.

        Yields:
            None

        Example:
            Composing multiple models efficiently::

                with composer.batch_composition():
                    # These compositions are optimized
                    Model1 = composer.compose(Base1, Mixin1)
                    Model2 = composer.compose(Base2, Mixin2)
                    Model3 = composer.compose(Model1, Model2)
                # Cache cleanup happens here

        Note:
            Useful when performing many compositions in sequence.
        """
        # Disable cache cleanup during batch
        original_cache_size = self.cache_size
        self.cache_size = DEFAULT_CACHE_SIZE * 10  # Temporarily increase

        try:
            yield
        finally:
            # Restore original cache size and cleanup
            self.cache_size = original_cache_size
            self._cleanup_cache()

    def _perform_composition(
        self,
        base: Type[T],
        mixin: Type[BaseModel],
        strategy: CompositionStrategy
    ) -> Type[T]:
        """Internal method to perform actual composition.

        Args:
            base: Base model class
            mixin: Mixin model class
            strategy: Composition strategy enum

        Returns:
            Composed model class

        Note:
            This method should not be called directly.
            Use `compose` or `compose_with_config` instead.
        """
        # Implementation details...
        logger.debug(f"Composing {base.__name__} with {mixin.__name__} using {strategy.name}")

        # Placeholder implementation
        # Real implementation would handle each strategy
        return type(
            f"{base.__name__}{mixin.__name__}",
            (base,),
            {"__module__": base.__module__}
        )

    def _get_cache_key(
        self,
        base: Type[BaseModel],
        mixin: Type[BaseModel],
        strategy: CompositionStrategy
    ) -> str:
        """Generate cache key for composition.

        Args:
            base: Base model class
            mixin: Mixin model class
            strategy: Composition strategy

        Returns:
            Cache key string

        Note:
            Uses fully qualified names to avoid collisions.
        """
        return f"{base.__module__}.{base.__name__}+" \
               f"{mixin.__module__}.{mixin.__name__}+" \
               f"{strategy.name}"

    def _cleanup_cache(self) -> None:
        """Clean up cache to maintain size limit.

        This method removes least recently used items
        when the cache exceeds the configured size.

        Note:
            Called automatically during batch composition.
        """
        if len(self.cache) > self.cache_size > 0:
            # Simple cleanup: remove oldest entries
            # In production, implement LRU
            excess = len(self.cache) - self.cache_size
            keys = list(self.cache.keys())[:excess]
            for key in keys:
                del self.cache[key]
            logger.debug(f"Cleaned up {excess} cache entries")


# =============================================================================
# Module-Level Functions
# =============================================================================

@lru_cache(maxsize=128)
def compose_with_strategy(
    base: Type[BaseModel],
    mixin: Type[BaseModel],
    strategy: str = "shallow_merge"
) -> Type[BaseModel]:
    """Compose models with caching at module level.

    This function provides a simple interface for model
    composition with automatic caching via `lru_cache`.

    Args:
        base: Base model class
        mixin: Mixin model class
        strategy: Strategy name (string)

    Returns:
        Composed model class

    Example:
        >>> Result = compose_with_strategy(
        ...     BaseModel,
        ...     MixinModel,
        ...     strategy="deep_merge"
        ... )

    Note:
        This function uses module-level caching which
        persists for the lifetime of the process.

    See Also:
        `AdvancedComposer`: For more control
        `CompositionStrategy`: Available strategies
    """
    composer = AdvancedComposer()
    return composer.compose(base, mixin, strategy=strategy)


# =============================================================================
# Module Initialization
# =============================================================================

def _initialize_module() -> None:
    """Initialize module-level resources.

    This function is called when the module is imported
    to set up logging, caching, and other resources.

    Note:
        This is an internal function and should not
        be called directly.
    """
    # Configure module logger
    logger.setLevel(logging.INFO)

    # Pre-populate cache with common compositions
    # This improves performance for frequently used patterns
    pass


# Initialize on import
_initialize_module()
```

---

## Summary

This comprehensive guide covers:

1. **Google-Style Docstrings**: Complete format with Napoleon/Sphinx integration
2. **Fixture Architecture**: Scalable organization for large codebases
3. **Package Mirroring**: Test structure matching source code
4. **Code Writing Process**: Systematic development workflow
5. **Reference Formatting**: Proper use of backticks and cross-references
6. **Complete Examples**: Full module with all documentation patterns

Key principles:

- Always document before implementing
- Use type hints everywhere
- Provide comprehensive examples
- Cross-reference liberally with backticks
- Organize fixtures hierarchically
- Mirror package structure in tests
- Cache expensive operations
- Handle errors explicitly

This documentation serves as the definitive guide for code standards in the
ooai-core project and can be adapted for any Python project requiring
professional documentation and testing practices.

---

_Document Version: 1.0.0_ _Last Updated: 2024_ _Author: OOAI Team_
