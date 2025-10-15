# Advanced Testing Infrastructure Documentation

## Overview

This document outlines advanced testing strategies, tools, and workflows for the
ooai-core project, including smoke testing, snapshot testing, property-based
testing, and comprehensive fixture management.

## Table of Contents

- [Smoke Testing](#smoke-testing)
- [Snapshot Testing](#snapshot-testing)
- [Property-Based Testing with Hypothesis](#property-based-testing-with-hypothesis)
- [Advanced Fixtures and Plugins](#advanced-fixtures-and-plugins)
- [Testing Workflows](#testing-workflows)
- [Implementation Roadmap](#implementation-roadmap)

---

## Smoke Testing

### Concept

Smoke tests are a subset of critical tests that validate core functionality
quickly. They serve as the first line of defense in CI/CD pipelines.

### Current Implementation

We already have the `smoke` marker defined in `pyproject.toml`:

```toml
"smoke: Smoke tests (critical path)"
```

### Enhanced Smoke Testing Strategy

#### 1. Install pytest-smoke Plugin

```bash
pdm add -d pytest-smoke
```

#### 2. Mark Critical Tests

```python
import pytest

@pytest.mark.smoke
@pytest.mark.critical  # Must-pass test
def test_core_model_creation():
    """Critical: Basic model creation must work"""
    from ooai.core.models import DynamicBaseModel

    class TestModel(DynamicBaseModel):
        name: str

    instance = TestModel(name="test")
    assert instance.name == "test"

@pytest.mark.smoke(mustpass=True)
def test_composition_protocol_basics():
    """Must-pass: Basic composition must work"""
    # Critical path test
    pass

@pytest.mark.smoke
@pytest.mark.fast
def test_quick_validation():
    """Fast smoke test for quick CI validation"""
    pass
```

#### 3. Smoke Test Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
smoke_marked_tests_as_critical = true
smoke_default_scope = "module"  # or "package", "session"

# Additional markers
markers = [
    "critical: Must-pass tests that block the pipeline",
    "smoke: Quick validation of core functionality",
    "sanity: Basic sanity checks",
]
```

#### 4. PDM Scripts for Smoke Testing

```toml
[tool.pdm.scripts]
# Smoke testing commands
smoke = "pytest -m smoke"
smoke-critical = "pytest -m 'smoke and critical'"
smoke-quick = "pytest --smoke=5"  # Run 5 smoke tests per module
smoke-percent = "pytest --smoke=20%"  # Run 20% of tests as smoke
smoke-ci = "pytest --smoke=10 --fail-fast"  # CI smoke tests

# Sanity checks
sanity = "pytest -m sanity --tb=line"
pre-commit-smoke = "pytest -m 'smoke and fast' --tb=line -q"
```

---

## Snapshot Testing

### Beyond Golden Files: Modern Snapshot Testing

#### 1. Syrupy (Recommended)

**Why Syrupy over pytest-snapshot:**

- Zero dependencies
- Better pytest integration
- Automatic snapshot management
- Extensible serializers

**Installation:**

```bash
pdm add -d syrupy
```

**Basic Usage:**

```python
def test_model_structure_snapshot(snapshot):
    """Test model structure with snapshot"""
    from ooai.core.models import DynamicBaseModel

    class ComplexModel(DynamicBaseModel):
        name: str
        age: int
        metadata: dict

    # Snapshot the model schema
    assert ComplexModel.model_json_schema() == snapshot

    # Snapshot instance serialization
    instance = ComplexModel(name="test", age=30, metadata={"key": "value"})
    assert instance.model_dump() == snapshot(name="instance_dump")

def test_api_response_snapshot(snapshot):
    """Test API response structure"""
    response = {
        "status": "success",
        "data": {"id": 123, "timestamp": "2024-01-01"},
        "metadata": {"version": "1.0"}
    }

    # Use matchers for dynamic data
    from syrupy.matchers import path_type

    assert response == snapshot(
        matcher=path_type({
            "data.timestamp": (str,),
            "data.id": (int,)
        })
    )
```

#### 2. Advanced Snapshot Strategies

**Custom Serializers:**

```python
from syrupy.extensions.json import JSONSnapshotExtension

class PrettyJSONExtension(JSONSnapshotExtension):
    """Custom JSON serializer with pretty printing"""

    def serialize(self, data):
        return json.dumps(data, indent=2, sort_keys=True)

@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(PrettyJSONExtension)
```

**Inline Snapshots (Alternative):**

```bash
pdm add -d inline-snapshot
```

```python
from inline_snapshot import snapshot

def test_inline_example():
    assert 1 + 1 == snapshot(2)  # Inline snapshot
```

#### 3. Snapshot Management Commands

```toml
[tool.pdm.scripts]
# Snapshot testing
snapshot-update = "pytest --snapshot-update"
snapshot-clean = "pytest --snapshot-update --snapshot-details"
snapshot-verify = "pytest -m snapshot"
snapshot-diff = "pytest --snapshot-diff"
```

---

## Property-Based Testing with Hypothesis

### Setup and Configuration

#### 1. Installation

```bash
# Already in our dependencies:
# hypothesis>=6.140.2
# hypothesis-jsonschema>=0.23.1
```

#### 2. Basic Strategies

```python
from hypothesis import given, strategies as st
import hypothesis

# Configure Hypothesis
hypothesis.settings.register_profile(
    "dev",
    max_examples=100,
    deadline=None,  # Disable deadline for development
    print_blob=True,
)

hypothesis.settings.register_profile(
    "ci",
    max_examples=1000,
    deadline=2000,  # 2 second deadline
)

hypothesis.settings.load_profile("dev")  # or "ci" in CI environment
```

#### 3. Model Testing with Hypothesis

```python
from hypothesis import given, strategies as st
from hypothesis.strategies import composite

@composite
def dynamic_model_strategy(draw):
    """Generate random DynamicBaseModel instances"""
    # Generate random field types
    field_count = draw(st.integers(min_value=1, max_value=10))
    fields = {}

    for i in range(field_count):
        field_name = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll"))))
        field_type = draw(st.sampled_from([str, int, float, bool]))
        fields[field_name] = (field_type, ...)

    return create_model("TestModel", **fields)

@given(model_class=dynamic_model_strategy())
def test_model_creation_properties(model_class):
    """Test that any dynamically created model maintains properties"""
    # Property: Model should be creatable
    assert issubclass(model_class, BaseModel)

    # Property: Model should have schema
    schema = model_class.model_json_schema()
    assert "properties" in schema

    # Property: Model fields should be accessible
    for field_name in model_class.model_fields:
        assert hasattr(model_class, field_name)
```

#### 4. Composition Testing

```python
@composite
def composition_strategy(draw):
    """Generate composition scenarios"""
    base_model = draw(dynamic_model_strategy())
    mixin_model = draw(dynamic_model_strategy())
    mode = draw(st.sampled_from([
        CompositionMode.INGEST,
        CompositionMode.ADD,
        CompositionMode.DELEGATE
    ]))
    return base_model, mixin_model, mode

@given(composition_data=composition_strategy())
def test_composition_properties(composition_data):
    """Test composition maintains invariants"""
    base, mixin, mode = composition_data

    try:
        composed = compose_models(base, mixin, mode)

        # Property: Composed model should have fields from base
        for field in base.model_fields:
            assert field in composed.model_fields or mode == CompositionMode.DELEGATE

        # Property: No field should be lost without reason
        if mode == CompositionMode.INGEST:
            total_fields = len(base.model_fields) + len(mixin.model_fields)
            assert len(composed.model_fields) <= total_fields

    except CompositionError:
        # Some compositions may validly fail
        pass
```

#### 5. Engine Testing with Hypothesis

```python
@composite
def engine_input_strategy(draw):
    """Generate valid engine inputs"""
    return {
        "text": draw(st.text(min_size=1, max_size=1000)),
        "max_tokens": draw(st.integers(min_value=1, max_value=4096)),
        "temperature": draw(st.floats(min_value=0.0, max_value=2.0)),
        "metadata": draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(), st.integers(), st.floats())
        ))
    }

@given(input_data=engine_input_strategy())
def test_engine_processing_properties(input_data):
    """Test engine processing maintains properties"""
    engine = TestEngine()

    result = engine.process(input_data)

    # Property: Output should always have expected structure
    assert "result" in result
    assert isinstance(result["result"], str)

    # Property: Metadata should be preserved if present
    if "metadata" in input_data:
        assert "metadata" in result or "processed_metadata" in result
```

#### 6. Hypothesis Configuration in pyproject.toml

```toml
[tool.hypothesis]
# Profile settings
profile = "default"
max_examples = 100
deadline = 2000  # milliseconds
suppress_health_check = ["too_slow", "data_too_large"]
database_file = ".hypothesis/examples.db"
print_blob = true
verbosity = "normal"  # or "quiet", "verbose", "debug"

# Phases to run
phases = [
    "explicit",
    "reuse",
    "generate",
    "target",
    "shrink",
    "explain"
]
```

---

## Advanced Fixtures and Plugins

### 1. Fixture Factories

```python
# tests/fixtures/factories.py
import pytest
from pytest_factoryboy import register
from factory import Factory, Faker, SubFactory
from typing import Type

class DynamicModelFactory(Factory):
    """Factory for creating test models"""
    class Meta:
        model = dict

    name = Faker("name")
    age = Faker("pyint", min_value=0, max_value=100)
    email = Faker("email")

    @classmethod
    def create_model_class(cls, **kwargs) -> Type[DynamicBaseModel]:
        """Create a DynamicBaseModel class with random fields"""
        fields = cls.build(**kwargs)
        return create_model("TestModel", **{
            k: (type(v), ...) for k, v in fields.items()
        })

register(DynamicModelFactory)

@pytest.fixture
def model_factory():
    """Provide model factory for tests"""
    return DynamicModelFactory

@pytest.fixture
def random_model(model_factory):
    """Create a random model instance"""
    model_class = model_factory.create_model_class()
    return model_class(**model_factory.build())
```

### 2. Parameterized Fixtures

```python
# tests/conftest.py additions
@pytest.fixture(params=["simple", "complex", "nested"])
def model_complexity(request):
    """Provide models of different complexity levels"""
    if request.param == "simple":
        return create_simple_model()
    elif request.param == "complex":
        return create_complex_model()
    elif request.param == "nested":
        return create_nested_model()

@pytest.fixture(params=[10, 100, 1000])
def data_size(request):
    """Provide different data sizes for performance testing"""
    return request.param

def test_performance_scaling(model_complexity, data_size):
    """Test performance with different model complexities and data sizes"""
    # Test automatically runs with all combinations
    pass
```

### 3. Plugin Recommendations

#### Essential Plugins (Add to pyproject.toml):

```toml
[dependency-groups]
test-essential = [
    "pytest-benchmark>=5.1.0",      # Performance benchmarking
    "pytest-lazy-fixture>=0.6.0",   # Lazy fixture evaluation
    "pytest-datadir-mgr>=1.2.0",    # Test data management
    "pytest-cases>=3.8.0",          # Advanced test cases
    "pytest-bdd>=7.0.0",            # BDD testing
    "pytest-testmon>=2.1.0",        # Smart test selection
    "pytest-instafail>=0.5.0",      # Show failures instantly
    "pytest-picked>=0.5.0",         # Run tests for modified files
    "pytest-reverse>=1.7.0",        # Run tests in reverse order
    "pytest-randomly>=4.0.0",       # Randomize test order
]
```

### 4. Advanced Fixture Patterns

#### Fixture Inheritance

```python
@pytest.fixture
def base_engine():
    """Base engine fixture"""
    return BaseEngine()

@pytest.fixture
def configured_engine(base_engine):
    """Configured engine based on base"""
    base_engine.configure(max_tokens=100)
    return base_engine

@pytest.fixture
def mock_engine(configured_engine, mocker):
    """Mocked engine for testing"""
    mocker.patch.object(configured_engine, "_process", return_value={"result": "mocked"})
    return configured_engine
```

#### Context Manager Fixtures

```python
@pytest.fixture
def temp_model_cache():
    """Temporary model cache for testing"""
    from ooai.core.models import DynamicBaseModel

    original_cache = DynamicBaseModel._cache.copy()
    DynamicBaseModel.clear_cache()

    yield DynamicBaseModel._cache

    # Restore original cache
    DynamicBaseModel._cache = original_cache

@pytest.fixture
def isolated_test_env():
    """Provide isolated test environment"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        yield tmpdir

        os.chdir(original_dir)
```

---

## Testing Workflows

### 1. Development Workflow

```bash
# Quick validation during development
pdm run smoke-quick           # Run 5 smoke tests
pdm run test-fast             # Run fast tests only
pdm run test-picked           # Run tests for changed files

# Property testing during development
pdm run hypothesis-dev        # Run with dev profile (100 examples)

# Snapshot updates
pdm run snapshot-update       # Update snapshots
pdm run snapshot-verify       # Verify snapshots
```

### 2. Pre-Commit Workflow

```yaml
# .pre-commit-config.yaml additions
repos:
  - repo: local
    hooks:
      - id: smoke-tests
        name: Smoke Tests
        entry: pdm run smoke-quick
        language: system
        pass_filenames: false
        stages: [commit]

      - id: fast-tests
        name: Fast Tests
        entry: pdm run test-fast
        language: system
        pass_filenames: false
        stages: [push]
```

### 3. CI/CD Workflow

```yaml
# GitHub Actions example
name: Advanced Testing

on: [push, pull_request]

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Smoke Tests
        run: |
          pdm install -G :all
          pdm run smoke-critical

  property-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Property Tests
        run: |
          pdm install -G :all
          pdm run hypothesis-ci

  snapshot-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Verify Snapshots
        run: |
          pdm install -G :all
          pdm run snapshot-verify
```

### 4. Performance Testing Workflow

```python
# tests/performance/test_benchmarks.py
import pytest

@pytest.mark.benchmark(group="model-creation")
def test_model_creation_performance(benchmark):
    """Benchmark model creation"""
    def create_model():
        return DynamicBaseModel.create_model(
            "BenchModel",
            field1=(str, ...),
            field2=(int, ...),
            field3=(float, ...)
        )

    result = benchmark(create_model)
    assert result.__name__ == "BenchModel"

@pytest.mark.benchmark(group="composition")
def test_composition_performance(benchmark, simple_models):
    """Benchmark model composition"""
    model1 = simple_models["Model1"]
    model2 = simple_models["Model2"]

    def compose():
        return compose_models(model1, model2, CompositionMode.INGEST)

    result = benchmark(compose)
    assert issubclass(result, DynamicBaseModel)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

- [ ] Install and configure Syrupy for snapshot testing
- [ ] Set up pytest-smoke with critical test markers
- [ ] Configure Hypothesis profiles for dev/CI
- [ ] Update pyproject.toml with new dependencies

### Phase 2: Test Enhancement (Week 2)

- [ ] Mark existing critical tests with @pytest.mark.smoke
- [ ] Add snapshot tests for complex model structures
- [ ] Create property-based tests for core functionality
- [ ] Implement fixture factories

### Phase 3: Workflow Integration (Week 3)

- [ ] Add PDM scripts for all testing workflows
- [ ] Configure pre-commit hooks for smoke tests
- [ ] Set up CI/CD with advanced testing stages
- [ ] Create performance benchmarks

### Phase 4: Documentation & Training (Week 4)

- [ ] Document all testing patterns in CLAUDE.md
- [ ] Create example tests for each pattern
- [ ] Add testing guidelines to contribution docs
- [ ] Record testing best practices

### Metrics for Success

- **Smoke Test Coverage**: 20+ critical path tests
- **Snapshot Coverage**: 80% of complex data structures
- **Property Test Coverage**: 50+ property-based tests
- **Performance Baselines**: Established for all core operations
- **CI Speed**: Smoke tests complete in <30 seconds
- **Bug Detection**: 30% increase in edge case discovery

---

## PDM Script Additions

Add these to `pyproject.toml`:

```toml
[tool.pdm.scripts]
# Smoke Testing
smoke = "pytest -m smoke"
smoke-quick = "pytest --smoke=5"
smoke-critical = "pytest -m 'smoke and critical'"
smoke-ci = "pytest --smoke=10 --fail-fast"

# Snapshot Testing
snapshot = "pytest -m snapshot"
snapshot-update = "pytest --snapshot-update"
snapshot-verify = "pytest --snapshot-update --check"

# Property Testing
hypothesis = "pytest -m hypothesis"
hypothesis-dev = "pytest -m hypothesis --hypothesis-profile=dev"
hypothesis-ci = "pytest -m hypothesis --hypothesis-profile=ci"
hypothesis-debug = "pytest -m hypothesis --hypothesis-verbosity=debug"

# Performance Testing
benchmark = "pytest -m benchmark"
benchmark-compare = "pytest-benchmark compare"
benchmark-save = "pytest --benchmark-autosave"

# Advanced Workflows
test-changed = "pytest --testmon"
test-picked = "pytest --picked"
test-reverse = "pytest --reverse"
test-random = "pytest --random-order"

# Combined Workflows
test-pre-commit = {composite = ["smoke-quick", "test-fast"]}
test-pre-push = {composite = ["smoke", "snapshot-verify"]}
test-full-advanced = {composite = ["smoke", "snapshot", "hypothesis", "benchmark"]}
```

---

## Conclusion

This advanced testing infrastructure provides:

1. **Smoke Testing**: Quick validation of critical functionality
2. **Snapshot Testing**: Automated regression detection for complex outputs
3. **Property-Based Testing**: Comprehensive edge case discovery
4. **Advanced Fixtures**: Flexible and reusable test components
5. **Optimized Workflows**: Efficient testing at every stage of development

By implementing these patterns, we achieve:

- Faster feedback cycles
- Better test coverage
- More robust code
- Easier maintenance
- Confident deployments

For questions or contributions, see [@testing-framework](#testing-framework) in
CLAUDE.md.
