# OOAI Graph Revised Architecture (Based on Real LangGraph Analysis)

## Architecture Foundation

After deep analysis of LangGraph's actual codebase, the architecture is revised to work WITH LangGraph's channel-based state management and Pregel execution model rather than fighting it.

## Core Understanding

### LangGraph's Real Structure
- **StateGraph**: Builder pattern that creates channel mappings from state schemas
- **Channels**: The actual state management system (LastValue, BinaryOperatorAggregate, etc.)
- **Pregel**: Execution engine that StateGraph compiles to
- **Nodes**: Functions wrapped in StateNodeSpec with metadata
- **Branches**: Conditional routing through BranchSpec

### Key Insight: Don't Replace, Extend

LangGraph's power comes from its mature channel system and Pregel execution. OOAI should extend these proven components, not replace them.

## Revised Package Structure

```
src/ooai/graph/
├── core/
│   ├── __init__.py
│   ├── state_graph.py          # OOAIStateGraph extending StateGraph
│   ├── channels.py             # Enhanced channels with OOAI metadata
│   ├── recompiler.py           # Modification queue and recompilation
│   └── schema_evolution.py     # DynamicBaseModel schema evolution
├── integration/
│   ├── __init__.py
│   ├── engine.py               # BaseEngine wrapper for compiled graphs
│   ├── composition.py          # DynamicBaseModel integration
│   └── adapters.py             # LangGraph compatibility helpers
├── utils/
│   ├── __init__.py
│   ├── modification_tracking.py # Track graph modifications
│   ├── channel_utils.py        # Channel creation and management
│   └── type_utils.py           # Type handling utilities
└── types/
    ├── __init__.py
    ├── modifications.py        # Modification type definitions
    └── ooai_types.py           # OOAI-specific type extensions
```

## Core Components Design

### 1. OOAIStateGraph - Minimal Extension

```python
from langgraph.graph.state import StateGraph
from langgraph.typing import StateT, ContextT

class OOAIStateGraph(StateGraph[StateT, ContextT]):
    """StateGraph extended with recompilation and OOAI capabilities."""

    def __init__(
        self,
        state_schema: type[StateT] | None = None,
        **kwargs
    ):
        # Default to DynamicBaseModel if no schema provided
        if state_schema is None:
            from ooai.core.models import DynamicBaseModel
            state_schema = DynamicBaseModel

        super().__init__(state_schema, **kwargs)

        # OOAI extensions
        self._ooai_metadata = {}
        self._modification_queue = []
        self._schema_versions = [state_schema]
        self._compiled_instance = None

    def add_ooai_node(self, name: str, func: callable, **ooai_metadata):
        """Add node with OOAI metadata tracking."""
        # Use LangGraph's native add_node
        result = self.add_node(name, func)

        # Track OOAI metadata
        self._ooai_metadata[name] = ooai_metadata
        self._track_modification({
            "type": "add_node",
            "name": name,
            "func": func,
            "metadata": ooai_metadata
        })

        return result

    def recompile(self):
        """Apply queued modifications and recompile graph."""
        # Apply all queued modifications
        modified_graph = self._apply_modifications()

        # Compile using LangGraph's native compile
        self._compiled_instance = modified_graph.compile()

        # Clear modification queue
        self._modification_queue.clear()

        return self._compiled_instance

    def _track_modification(self, modification: dict):
        """Track modification for recompilation."""
        self._modification_queue.append(modification)

    def _apply_modifications(self):
        """Apply all queued modifications to create new graph."""
        # Create new graph instance
        new_graph = OOAIStateGraph(self.state_schema)

        # Copy existing structure
        for name, spec in self.nodes.items():
            new_graph.add_node(name, spec.runnable)

        for edge in self.edges:
            new_graph.add_edge(edge[0], edge[1])

        # Apply queued modifications
        for mod in self._modification_queue:
            if mod["type"] == "add_node":
                new_graph.add_node(mod["name"], mod["func"])
            elif mod["type"] == "add_edge":
                new_graph.add_edge(mod["source"], mod["target"])
            # ... other modification types

        return new_graph
```

### 2. Enhanced Channels with OOAI Metadata

```python
from langgraph.channels.last_value import LastValue
from langgraph.channels.binop import BinaryOperatorAggregate

class OOAILastValue(LastValue):
    """LastValue channel enhanced with OOAI metadata."""

    def __init__(self, typ, ooai_metadata=None, **kwargs):
        super().__init__(typ, **kwargs)
        self.ooai_metadata = ooai_metadata or {}

    def from_checkpoint(self, checkpoint):
        """Preserve OOAI metadata during checkpoint restoration."""
        restored = super().from_checkpoint(checkpoint)
        restored.ooai_metadata = self.ooai_metadata.copy()
        return restored

class OOAIBinaryOperatorAggregate(BinaryOperatorAggregate):
    """BinaryOperatorAggregate with OOAI metadata."""

    def __init__(self, typ, operator, ooai_metadata=None, **kwargs):
        super().__init__(typ, operator, **kwargs)
        self.ooai_metadata = ooai_metadata or {}

def create_ooai_channels(schema: type) -> dict:
    """Create channels with OOAI metadata from schema."""
    from langgraph.graph.state import _get_channels

    # Get standard LangGraph channels
    channels, managed, type_hints = _get_channels(schema)

    # Enhance with OOAI metadata if available
    enhanced_channels = {}
    for key, channel in channels.items():
        ooai_metadata = {}

        # Extract OOAI metadata from DynamicBaseModel
        if hasattr(schema, '__ooai_field_metadata__'):
            ooai_metadata = schema.__ooai_field_metadata__.get(key, {})

        # Create enhanced channel
        if isinstance(channel, LastValue):
            enhanced_channels[key] = OOAILastValue(
                channel.typ,
                ooai_metadata=ooai_metadata
            )
        elif isinstance(channel, BinaryOperatorAggregate):
            enhanced_channels[key] = OOAIBinaryOperatorAggregate(
                channel.typ,
                channel.operator,
                ooai_metadata=ooai_metadata
            )
        else:
            # Fallback to original channel
            enhanced_channels[key] = channel

    return enhanced_channels, managed, type_hints
```

### 3. Schema Evolution Manager

```python
class SchemaEvolutionManager:
    """Manages state schema evolution using DynamicBaseModel composition."""

    def __init__(self, base_schema):
        self.base_schema = base_schema
        self.evolution_history = [base_schema]

    def evolve_schema(self, changes: dict):
        """Evolve schema using DynamicBaseModel composition."""
        if self._is_dynamic_base_model(self.base_schema):
            # Use ooai-core composition
            new_schema = self._compose_with_dynamic_model(changes)
        else:
            # Create new TypedDict or dataclass
            new_schema = self._create_evolved_schema(changes)

        self.evolution_history.append(new_schema)
        return new_schema

    def _is_dynamic_base_model(self, schema):
        """Check if schema is a DynamicBaseModel."""
        try:
            from ooai.core.models import DynamicBaseModel
            return issubclass(schema, DynamicBaseModel)
        except (ImportError, TypeError):
            return False

    def _compose_with_dynamic_model(self, changes):
        """Use ooai-core composition for schema evolution."""
        from ooai.core.models.dynamic_base_model import compose_models

        # Create change model from dict
        change_model = self._create_change_model(changes)

        # Compose using ooai-core
        return compose_models(self.base_schema, change_model)

    def _create_change_model(self, changes):
        """Create DynamicBaseModel from changes dict."""
        from ooai.core.models import DynamicBaseModel

        class SchemaChange(DynamicBaseModel):
            pass

        # Add fields from changes
        for field_name, field_config in changes.items():
            SchemaChange.__add_field__(field_name, field_config)

        return SchemaChange

    def migrate_state(self, old_state: dict, new_schema) -> dict:
        """Migrate state between schema versions."""
        # Basic migration: preserve existing fields, add defaults for new ones
        migrated_state = old_state.copy()

        # Add default values for new fields
        if hasattr(new_schema, '__fields__'):
            for field_name, field_info in new_schema.__fields__.items():
                if field_name not in migrated_state:
                    default_value = getattr(field_info, 'default', None)
                    if default_value is not None:
                        migrated_state[field_name] = default_value

        return migrated_state
```

### 4. Graph Recompiler

```python
class GraphRecompiler:
    """Handles graph recompilation with modification tracking."""

    def __init__(self, base_graph: OOAIStateGraph):
        self.base_graph = base_graph
        self.modification_history = []

    def queue_modification(self, modification: dict):
        """Queue a modification for next recompilation."""
        self.base_graph._track_modification(modification)

    def recompile(self):
        """Apply all modifications and recompile graph."""
        return self.base_graph.recompile()

    def rollback(self, steps: int = 1):
        """Rollback modifications and recompile."""
        # Remove last N modifications
        for _ in range(steps):
            if self.base_graph._modification_queue:
                rolled_back = self.base_graph._modification_queue.pop()
                self.modification_history.append(("rollback", rolled_back))

        return self.recompile()

    def checkpoint(self, name: str):
        """Create named checkpoint of current graph state."""
        checkpoint_data = {
            "graph_state": self.base_graph.__dict__.copy(),
            "modification_queue": self.base_graph._modification_queue.copy(),
            "schema_versions": self.base_graph._schema_versions.copy()
        }
        # Store checkpoint (implementation depends on persistence strategy)
        return checkpoint_data

    def restore(self, checkpoint_data: dict):
        """Restore graph to checkpoint state."""
        # Restore graph state from checkpoint
        for key, value in checkpoint_data["graph_state"].items():
            setattr(self.base_graph, key, value)

        return self.recompile()
```

### 5. Engine Integration

```python
from ooai.core.engine.base import BaseEngine

class GraphEngine(BaseEngine):
    """BaseEngine wrapper for OOAI graphs."""

    def __init__(self, ooai_graph: OOAIStateGraph, **kwargs):
        super().__init__(**kwargs)
        self.ooai_graph = ooai_graph
        self.compiled_graph = None

    def _process(self, input_data: dict, **kwargs) -> dict:
        """Execute graph using LangGraph's invoke."""
        if self.compiled_graph is None:
            self.compiled_graph = self.ooai_graph.compile()

        return self.compiled_graph.invoke(input_data)

    def _get_input_schema_class(self):
        """Return graph's input schema."""
        return self.ooai_graph.input_schema

    def _get_output_schema_class(self):
        """Return graph's output schema."""
        return self.ooai_graph.output_schema

    def recompile_graph(self):
        """Recompile the underlying graph and update engine."""
        self.compiled_graph = self.ooai_graph.recompile()

    def add_node_and_recompile(self, name: str, func: callable, **metadata):
        """Add node and recompile graph in one operation."""
        self.ooai_graph.add_ooai_node(name, func, **metadata)
        self.recompile_graph()
```

## Integration Strategy

### 1. Seamless LangGraph Compatibility

```python
# Convert between OOAI and LangGraph
def to_langgraph(ooai_graph: OOAIStateGraph) -> StateGraph:
    """Convert OOAI graph to pure LangGraph."""
    lang_graph = StateGraph(ooai_graph.state_schema)

    # Copy structure without OOAI metadata
    for name, spec in ooai_graph.nodes.items():
        lang_graph.add_node(name, spec.runnable)

    for edge in ooai_graph.edges:
        lang_graph.add_edge(edge[0], edge[1])

    return lang_graph

def from_langgraph(lang_graph: StateGraph) -> OOAIStateGraph:
    """Import LangGraph and add OOAI capabilities."""
    ooai_graph = OOAIStateGraph(lang_graph.state_schema)

    # Import structure
    for name, spec in lang_graph.nodes.items():
        ooai_graph.add_node(name, spec.runnable)

    for edge in lang_graph.edges:
        ooai_graph.add_edge(edge[0], edge[1])

    return ooai_graph
```

### 2. DynamicBaseModel State Schema

```python
# Use DynamicBaseModel as state schema
from ooai.core.models import DynamicBaseModel

class WorkflowState(DynamicBaseModel):
    input_text: str
    processed_text: str = None
    metadata: dict = {}

# Create graph with DynamicBaseModel state
graph = OOAIStateGraph(WorkflowState)

# Add nodes that work with the state
def process_text(state: WorkflowState) -> dict:
    return {"processed_text": state.input_text.upper()}

graph.add_ooai_node("process", process_text)

# Evolve schema at runtime
graph.evolve_schema({"confidence_score": float})
```

## Implementation Benefits

### 1. Leverages LangGraph Strengths
- **Proven execution model**: Pregel-based concurrent execution
- **Mature state management**: Channel-based state with checkpointing
- **Rich ecosystem**: Compatible with existing LangGraph tools

### 2. Adds OOAI Capabilities
- **Dynamic recompilation**: Modify graphs at runtime
- **Schema evolution**: Evolve state schemas using DynamicBaseModel
- **Engine integration**: Use graphs as BaseEngine instances
- **Metadata tracking**: Rich metadata for composition and analysis

### 3. Maintains Compatibility
- **Bidirectional conversion**: OOAI ↔ LangGraph
- **Drop-in replacement**: Can use OOAIStateGraph where StateGraph is expected
- **Performance parity**: Same execution performance as pure LangGraph

## Success Criteria

**Technical Success:**
- ✅ 100% LangGraph StateGraph compatibility
- ✅ Runtime graph modification without breaking execution
- ✅ DynamicBaseModel integration for schema evolution
- ✅ Channel-based state management with OOAI metadata

**Integration Success:**
- ✅ BaseEngine integration for workflow orchestration
- ✅ ooai-core model composition with graph state
- ✅ Seamless import/export with existing LangGraph workflows

**Performance Success:**
- ✅ Performance parity with pure LangGraph
- ✅ Efficient recompilation with minimal overhead
- ✅ Memory-efficient modification tracking

---

**Revised Approach**: Work WITH LangGraph's proven architecture, extend capabilities through composition and enhancement rather than replacement.