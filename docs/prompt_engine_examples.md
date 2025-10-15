# PromptEngine Usage Examples and Patterns

This document provides comprehensive examples and patterns for using the PromptEngine effectively.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Structured Output Patterns](#structured-output-patterns)
3. [File-Based Templates](#file-based-templates)
4. [Advanced Composition](#advanced-composition)
5. [Few-Shot Learning](#few-shot-learning)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Best Practices](#best-practices)

## Basic Usage

### Simple Template with Variables

```python
from ooai.core.engine.prompts import PromptEngine

# Basic template with input variables
engine = PromptEngine(
    template="Analyze the {data_type} data: {input}\n\nProvide a {analysis_level} analysis.",
    partial_variables={"analysis_level": "comprehensive"}
)

# Create runnable and invoke
runnable = engine.create_runnable()
result = runnable.invoke({
    "data_type": "financial",
    "input": "Q3 revenue data"
})
```

### Template with System Message

```python
engine = PromptEngine(
    template="User question: {question}",
    system_message="You are a helpful AI assistant specialized in {domain}.",
    partial_variables={"domain": "technical support"}
)

runnable = engine.create_runnable()
result = runnable.invoke({"question": "How do I debug Python code?"})
```

## Structured Output Patterns

### Pattern 1: Initialization with Structured Output

```python
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    """User profile data model."""
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years")
    email: str = Field(description="Email address")
    occupation: str = Field(description="Job title")

# Set structured output during initialization
engine = PromptEngine(
    template="Extract user information from: {text}",
    structured_output_model=UserProfile,
    structured_output_message="Please return user details as valid JSON."
)

runnable = engine.create_runnable()
result = runnable.invoke({"text": "John Smith, 35, engineer at TechCorp, john@email.com"})
```

### Pattern 2: Dynamic Structured Output Modification

```python
class CompanyInfo(BaseModel):
    company_name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    employee_count: int = Field(description="Number of employees")

# Start with basic template
engine = PromptEngine(template="Process this business data: {input}")

# Add structured output dynamically
engine.set_structured_output(UserProfile)
user_result = engine.create_runnable().invoke({"input": "employee data"})

# Change to different model
engine.set_structured_output(CompanyInfo)
company_result = engine.create_runnable().invoke({"input": "company data"})

# Remove structured output
engine.remove_structured_output()
plain_result = engine.create_runnable().invoke({"input": "generic data"})
```

### Pattern 3: Immutable Structured Output Chains

```python
# Create different engines for different output types
base_engine = PromptEngine(template="Analyze: {content}")

# Create specialized engines without modifying the original
user_engine = base_engine.with_structured_output(UserProfile)
company_engine = base_engine.with_structured_output(CompanyInfo)

# Each engine maintains its own configuration
user_result = user_engine.create_runnable().invoke({"content": "user data"})
company_result = company_engine.create_runnable().invoke({"content": "company data"})
```

## File-Based Templates

### Pattern 1: Markdown Template with Frontmatter

Create `templates/analysis.md`:

```markdown
---
input_variables: ["data", "format"]
partial_variables:
  analysis_type: "comprehensive"
  output_format: "detailed report"
system_message: "You are a data analysis expert"
---

# Data Analysis Request

Please analyze the following {data} and provide a {analysis_type} analysis.

## Requirements
- Format: {format}
- Output: {output_format}

## Data
{data}
```

Usage:

```python
engine = PromptEngine(template_file="templates/analysis.md")

runnable = engine.create_runnable()
result = runnable.invoke({
    "data": "sales figures for Q3",
    "format": "executive summary"
})
```

### Pattern 2: JSON Configuration Template

Create `templates/config.json`:

```json
{
  "template": "Process {task} with priority {priority}",
  "input_variables": ["task"],
  "partial_variables": {"priority": "high"},
  "system_message": "You are a task processing assistant",
  "add_messages_placeholder": true,
  "messages_optional": true
}
```

Usage:

```python
engine = PromptEngine(template_file="templates/config.json")

runnable = engine.create_runnable()
result = runnable.invoke({"task": "data migration"})
```

### Pattern 3: Multiple File Composition

Create multiple template files:

`templates/base.md`:
```markdown
# Base Template
Context: {context}
```

`templates/examples.md`:
```markdown
## Examples
Here are some examples of similar tasks:
{examples}
```

`templates/instructions.md`:
```markdown
## Instructions
Please follow these guidelines:
1. Be thorough
2. Provide examples
3. Format output as {format}
```

Usage:

```python
engine = PromptEngine(
    template_files=[
        "templates/base.md",
        "templates/examples.md",
        "templates/instructions.md"
    ],
    composition_strategy="chain",
    partial_variables={"format": "markdown"}
)

runnable = engine.create_runnable()
result = runnable.invoke({
    "context": "API documentation",
    "examples": "REST endpoints"
})
```

## Advanced Composition

### Pattern 1: LangChain Template Integration

```python
from langchain_core.prompts import ChatPromptTemplate

# Use existing LangChain template
langchain_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("human", "Question: {question}")
])

engine = PromptEngine(prompt_template=langchain_template)

runnable = engine.create_runnable()
result = runnable.invoke({"question": "What is machine learning?"})
```

### Pattern 2: Complex Variable Management

```python
engine = PromptEngine(
    template="""
    Task: {task}
    Priority: {priority}
    Deadline: {deadline}
    Assigned to: {assignee}

    Additional context:
    {context}
    """,
    input_variables=["task", "assignee"],
    optional_variables=["context"],
    partial_variables={
        "priority": "medium",
        "deadline": "end of week"
    }
)

runnable = engine.create_runnable()

# Required variables only
result1 = runnable.invoke({
    "task": "code review",
    "assignee": "developer@company.com"
})

# With optional variables
result2 = runnable.invoke({
    "task": "bug fix",
    "assignee": "engineer@company.com",
    "context": "Critical production issue"
})
```

## Few-Shot Learning

### Pattern 1: Classification with Examples

```python
examples = [
    {"text": "Great product, highly recommend!", "sentiment": "positive"},
    {"text": "Poor quality, waste of money", "sentiment": "negative"},
    {"text": "It's okay, nothing special", "sentiment": "neutral"}
]

engine = PromptEngine(
    template="Classify the sentiment of: {text}",
    examples=examples,
    example_template="Text: {text} -> Sentiment: {sentiment}"
)

runnable = engine.create_runnable()
result = runnable.invoke({"text": "Amazing service and fast delivery!"})
```

### Pattern 2: Code Generation with Examples

```python
code_examples = [
    {
        "description": "function to add two numbers",
        "code": "def add(a, b):\n    return a + b"
    },
    {
        "description": "function to find maximum value",
        "code": "def find_max(numbers):\n    return max(numbers)"
    }
]

engine = PromptEngine(
    template="Generate Python code for: {description}",
    examples=code_examples,
    example_template="Description: {description}\nCode:\n{code}"
)

runnable = engine.create_runnable()
result = runnable.invoke({"description": "function to calculate factorial"})
```

## Error Handling

### Pattern 1: Graceful Degradation

```python
from typing import Optional

def safe_invoke(engine: PromptEngine, inputs: dict) -> Optional[str]:
    """Safely invoke engine with error handling."""
    try:
        runnable = engine.create_runnable()
        result = runnable.invoke(inputs)
        return str(result)
    except KeyError as e:
        print(f"Missing required variable: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
engine = PromptEngine(template="Process {required_field}: {input}")
result = safe_invoke(engine, {"input": "test"})  # Will handle missing required_field
```

### Pattern 2: Validation and Fallbacks

```python
def create_robust_engine(template: str, fallback_template: str) -> PromptEngine:
    """Create engine with validation and fallback."""
    try:
        return PromptEngine(template=template, validate_template=True)
    except Exception:
        print("Primary template failed, using fallback")
        return PromptEngine(template=fallback_template, validate_template=False)

# Usage
engine = create_robust_engine(
    template="Complex template with {missing_variable}",
    fallback_template="Simple template: {input}"
)
```

## Performance Optimization

### Pattern 1: Template Caching

```python
# Create engine once, reuse multiple times
engine = PromptEngine(template="Process {input} with {method}")
runnable = engine.create_runnable()  # Cache the runnable

# Multiple invocations use cached runnable
results = []
for data in ["data1", "data2", "data3"]:
    result = runnable.invoke({"input": data, "method": "analysis"})
    results.append(result)
```

### Pattern 2: Batch Processing

```python
def batch_process(engine: PromptEngine, inputs_list: list[dict]) -> list[str]:
    """Process multiple inputs efficiently."""
    runnable = engine.create_runnable()
    return [str(runnable.invoke(inputs)) for inputs in inputs_list]

# Usage
engine = PromptEngine(template="Summarize: {text}")
inputs_batch = [
    {"text": "Article 1 content"},
    {"text": "Article 2 content"},
    {"text": "Article 3 content"}
]

results = batch_process(engine, inputs_batch)
```

### Pattern 3: Lazy Template Loading

```python
class LazyTemplateEngine:
    """Engine that loads templates on first use."""

    def __init__(self, template_file: str):
        self.template_file = template_file
        self._engine = None

    @property
    def engine(self) -> PromptEngine:
        if self._engine is None:
            self._engine = PromptEngine(template_file=self.template_file)
        return self._engine

    def invoke(self, inputs: dict):
        return self.engine.create_runnable().invoke(inputs)

# Usage
lazy_engine = LazyTemplateEngine("large_template.md")
# Template only loaded when first used
result = lazy_engine.invoke({"input": "test"})
```

## Best Practices

### 1. Template Organization

```python
# ✅ Good: Organized template structure
class TemplateRegistry:
    """Centralized template management."""

    ANALYSIS = PromptEngine(template_file="templates/analysis.md")
    SUMMARIZATION = PromptEngine(template_file="templates/summary.md")
    CLASSIFICATION = PromptEngine(
        template="Classify: {input}",
        structured_output_model=ClassificationResult
    )

# Usage
result = TemplateRegistry.ANALYSIS.create_runnable().invoke({"data": "test"})
```

### 2. Variable Validation

```python
# ✅ Good: Validate inputs before processing
def validated_invoke(engine: PromptEngine, inputs: dict):
    """Invoke with input validation."""
    required_vars = set(engine.input_variables)
    provided_vars = set(inputs.keys())

    missing_vars = required_vars - provided_vars
    if missing_vars:
        raise ValueError(f"Missing required variables: {missing_vars}")

    return engine.create_runnable().invoke(inputs)
```

### 3. Structured Output Validation

```python
from pydantic import ValidationError

def safe_structured_invoke(engine: PromptEngine, inputs: dict):
    """Safely invoke with structured output validation."""
    try:
        runnable = engine.create_runnable()
        result = runnable.invoke(inputs)

        if engine.output_parser:
            # Validate structured output
            parsed = engine.output_parser.parse(str(result))
            return parsed

        return result
    except ValidationError as e:
        print(f"Structured output validation failed: {e}")
        return None
```

### 4. Testing Patterns

```python
import pytest

def test_prompt_engine_output():
    """Test engine produces expected output format."""
    engine = PromptEngine(
        template="Analyze {data}",
        structured_output_model=AnalysisResult
    )

    result = engine.create_runnable().invoke({"data": "test data"})

    # Verify structure
    assert "analysis" in str(result).lower()
    assert "JSON" in str(result)  # Format instructions present

def test_engine_with_mock_data():
    """Test engine with controlled inputs."""
    engine = PromptEngine(template="Process {input}")

    test_cases = [
        {"input": "simple text", "expected_contains": "simple"},
        {"input": "complex data", "expected_contains": "complex"}
    ]

    for case in test_cases:
        result = str(engine.create_runnable().invoke(case))
        assert case["expected_contains"] in result
```

### 5. Configuration Management

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PromptConfig:
    """Configuration for prompt engines."""
    template: Optional[str] = None
    template_file: Optional[str] = None
    system_message: Optional[str] = None
    structured_output_model: Optional[type] = None

    def create_engine(self) -> PromptEngine:
        """Create engine from configuration."""
        return PromptEngine(
            template=self.template,
            template_file=self.template_file,
            system_message=self.system_message,
            structured_output_model=self.structured_output_model
        )

# Usage
config = PromptConfig(
    template="Analyze {data}",
    structured_output_model=AnalysisResult
)
engine = config.create_engine()
```

## Conclusion

The PromptEngine provides a flexible and powerful system for managing prompts with:

- **Multiple initialization patterns** for different use cases
- **Dynamic structured output management** for type-safe responses
- **File-based template organization** for maintainable prompts
- **Advanced composition features** for complex workflows
- **Performance optimization patterns** for production use

Choose the patterns that best fit your specific use case and requirements. The engine's design allows for gradual adoption and scaling from simple templates to complex, structured prompt management systems.

## Additional Resources

- [PromptEngine API Documentation](../src/ooai/core/engine/prompts/prompt_engine.py)
- [BaseEngine Documentation](../src/ooai/core/engine/base.py)
- [Test Examples](../tests/engine/prompts/)
- [LangChain Integration](https://python.langchain.com/docs/modules/model_io/prompts/)