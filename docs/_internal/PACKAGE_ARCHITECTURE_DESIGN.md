# OOAI Graph Package Architecture Design

## Package Vision

Core graph package built on LangGraph foundation with dynamic recompilation capabilities, ooai-core integration, and advanced state management. Focus on extending LangGraph's proven StateGraph/MessageGraph rather than rebuilding from scratch.

## Core Architecture

### Package Structure

```
src/ooai/graph/
├── core/                           # Core graph fundamentals
│   ├── __init__.py
│   ├── graph.py                    # CoreGraph with LangGraph integration
│   ├── nodes.py                    # GraphNode with OOAI extensions
│   ├── edges.py                    # GraphEdge with dynamic conditions
│   ├── recompiler.py               # Graph recompilation engine
│   └── exceptions.py               # Graph-specific exceptions
├── langgraph/                      # LangGraph integration layer
│   ├── __init__.py
│   ├── state_graph.py              # OOAIStateGraph extending LangGraph
│   ├── message_graph.py            # OOAIMessageGraph extensions
│   ├── compatibility.py            # Bidirectional LangGraph compatibility
│   └── adapters.py                 # LangGraph import/export adapters
├── recompilation/                  # Dynamic modification system
│   ├── __init__.py
│   ├── modifications.py            # Graph modification classes
│   ├── strategies.py               # Recompilation strategies
│   ├── dependencies.py             # Dependency tracking
│   └── checkpoints.py              # Checkpoint and rollback system
├── schema/                         # Dynamic schema management
│   ├── __init__.py
│   ├── evolution.py                # Schema evolution manager
│   ├── migration.py                # State migration strategies
│   ├── composition.py              # DynamicBaseModel integration
│   └── validation.py               # Schema validation
├── integration/                    # OOAI-core integration
│   ├── __init__.py
│   ├── engine.py                   # GraphEngine for BaseEngine
│   ├── models.py                   # DynamicBaseModel integration
│   ├── composition.py              # Model composition patterns
│   └── workflows.py                # Workflow orchestration
├── composition/                    # Schema composition system
│   ├── __init__.py
│   ├── schema_composer.py          # Dynamic schema composition
│   ├── model_integration.py        # DynamicBaseModel integration
│   ├── field_mapping.py            # Field mapping and transformation
│   └── validation_composer.py      # Composed validation logic
├── algorithms/                     # Graph algorithms library
│   ├── __init__.py
│   ├── shortest_path/              # Path finding algorithms
│   ├── centrality/                 # Centrality measures
│   ├── clustering/                 # Clustering algorithms
│   └── flow/                       # Flow algorithms
├── visualization/                  # Graph visualization
│   ├── __init__.py
│   ├── renderers.py                # Graph rendering engines
│   ├── layouts.py                  # Layout algorithms
│   └── exporters.py                # Export to various formats
└── utils/                          # Utilities and helpers
    ├── __init__.py
    ├── generators.py               # Graph generators
    ├── io.py                       # I/O operations
    └── performance.py              # Performance utilities
```

## LangGraph Adaptation Design

### 1. Core LangGraph Extensions

```python
from langgraph.graph.state import StateGraph
from langgraph.graph.message import MessageGraph
from ooai.core.models import DynamicBaseModel

class OOAIStateGraph(StateGraph):
    """StateGraph extended with OOAI capabilities and recompilation."""

    def __init__(self, state_schema=None, **kwargs):
        if state_schema is None:
            state_schema = DynamicBaseModel
        super().__init__(state_schema, **kwargs)

        self._ooai_metadata = {}
        self._recompilation_context = RecompilationContext()
        self._schema_evolution_manager = SchemaEvolutionManager(state_schema)

    def add_ooai_node(self, node_id: str, node_func: callable, **ooai_metadata):
        """Add node with OOAI metadata tracking."""
        self.add_node(node_id, node_func)
        self._ooai_metadata[node_id] = ooai_metadata
        self._recompilation_context.track_addition("node", node_id)

    def recompile(self) -> 'OOAIStateGraph':
        """Dynamic recompilation with accumulated modifications."""
        return self._recompilation_context.execute_recompilation(self)

    def evolve_schema(self, schema_changes: Dict) -> 'OOAIStateGraph':
        """Evolve state schema dynamically using DynamicBaseModel."""
        new_schema = self._schema_evolution_manager.evolve(schema_changes)
        return self._create_evolved_graph(new_schema)

class OOAIMessageGraph(MessageGraph):
    """MessageGraph with dynamic routing and schema capabilities."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dynamic_routing = DynamicRoutingManager()
        self._message_schema_composer = MessageSchemaComposer()

    def add_dynamic_router(self, router_func: callable, conditions: Dict):
        """Add router that can be modified at runtime."""
        router_id = self._dynamic_routing.register_router(router_func, conditions)
        self.add_conditional_edges(router_id, router_func)
        return router_id
```

### 2. Recompilation Engine

```python
class GraphRecompiler:
    """Dynamic graph modification and recompilation using LangGraph patterns."""

    def __init__(self, base_graph: OOAIStateGraph):
        self.base_graph = base_graph
        self.modification_queue = []
        self.compiled_cache = {}

    def add_node_modification(self, node_id: str, node_func: callable, **metadata):
        """Queue node addition using LangGraph's add_node pattern."""
        self.modification_queue.append({
            "type": "add_node",
            "node_id": node_id,
            "node_func": node_func,
            "metadata": metadata
        })

    def add_edge_modification(self, source: str, target: str, condition=None):
        """Queue edge addition using LangGraph's add_edge pattern."""
        self.modification_queue.append({
            "type": "add_edge",
            "source": source,
            "target": target,
            "condition": condition
        })

    def recompile(self) -> StateGraph:
        """Apply modifications and compile using LangGraph's compile()."""
        modified_graph = self._apply_modifications()
        return modified_graph.compile()
```

### 3. State Evolution with LangGraph Patterns

**State Management Approach:**
- Use LangGraph's existing state management patterns
- Leverage Python dictionaries for state (LangGraph's default)
- Add state transformation utilities for schema evolution
- Build on LangGraph's state reducer patterns

**Key Capabilities:**
- **State Transformers**: Functions to transform state between schema versions
- **Migration Strategies**: Patterns for evolving graph state over time
- **Backward Compatibility**: Maintain compatibility with existing state formats
- **State Validation**: Optional validation using standard Python patterns

**Integration Points:**
- Works with LangGraph's state reducer functions
- Compatible with existing LangGraph state patterns
- Leverages LangGraph's checkpoint system for state persistence
- Uses LangGraph's built-in state management infrastructure

### 4. LangGraph Compatibility Layer

**Bidirectional Integration:**
- Convert OOAI graphs to pure LangGraph for compatibility
- Import existing LangGraph workflows and add OOAI capabilities
- Maintain seamless interoperability with LangGraph ecosystem

**Key Capabilities:**
- **OOAIStateGraph**: Extends LangGraph StateGraph with recompilation
- **OOAIMessageGraph**: Extends LangGraph MessageGraph with dynamic routing
- **LangGraphAdapter**: Bidirectional conversion and compatibility
- **SchemaEvolutionManager**: Dynamic schema changes using DynamicBaseModel

## Advanced Features

### 5. Topology Analysis

```python
class TopologyAnalyzer:
    """Graph topology analysis and metrics."""

    def is_dag(self, graph: StateGraph) -> bool:
        """Check if graph is a directed acyclic graph."""

    def find_cycles(self, graph: StateGraph) -> List[List[str]]:
        """Find all cycles in graph."""

    def connectivity_analysis(self, graph: StateGraph) -> Dict[str, Any]:
        """Analyze graph connectivity."""

    def topological_sort(self, graph: StateGraph) -> List[str]:
        """Topological sorting of nodes."""
```

### 6. Validators

```python
class GraphValidator:
    """Comprehensive graph validation."""

    def validate_structure(self, graph: StateGraph) -> ValidationResult:
        """Validate graph structure constraints."""

    def validate_schema(self, graph: StateGraph) -> ValidationResult:
        """Validate node/edge schemas."""

    def validate_integrity(self, graph: StateGraph) -> ValidationResult:
        """Validate data integrity."""

class ValidationResult(BaseModel):
    """Validation result with detailed feedback."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
```

### 7. Patterns

```python
class GraphPatterns:
    """Common graph patterns and templates."""

    @staticmethod
    def create_pipeline(steps: List[str]) -> StateGraph:
        """Create linear pipeline graph."""

    @staticmethod
    def create_fanout(source: str, targets: List[str]) -> StateGraph:
        """Create fan-out pattern."""

    @staticmethod
    def create_fanin(sources: List[str], target: str) -> StateGraph:
        """Create fan-in pattern."""

    @staticmethod
    def create_conditional_flow(
        condition_node: str,
        branches: Dict[str, str]
    ) -> StateGraph:
        """Create conditional flow pattern."""
```

### 8. Engine Integration

```python
from ooai.core.engine.base import BaseEngine

class GraphEngine(BaseEngine):
    """Engine for executing graphs."""

    def __init__(self, graph: StateGraph):
        self.graph = graph

    def _process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute graph as engine process."""
        return self.graph.execute(input_data)

class GraphWorkflow:
    """Workflow integration for complex graph execution."""

    def __init__(self, graphs: Dict[str, StateGraph]):
        self.graphs = graphs

    def execute_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multi-graph workflow."""
```

### 9. Schema Composition

```python
from ooai.core.models.dynamic_base_model import compose_models

class SchemaComposer:
    """Dynamic schema composition for graph elements."""

    def compose_node_schema(
        self,
        base_schema: type,
        mixins: List[type]
    ) -> type:
        """Compose dynamic node schema."""
        return compose_models(base_schema, *mixins)

    def compose_graph_schema(
        self,
        node_schemas: Dict[str, type],
        edge_schemas: Dict[str, type]
    ) -> type:
        """Compose complete graph schema."""

class DynamicGraphModel(DynamicBaseModel):
    """Graph model with dynamic composition capabilities."""
    nodes: Dict[str, DynamicNode]
    edges: Dict[str, BaseEdge]

    def add_node_capability(self, capability_mixin: type) -> None:
        """Dynamically add capability to nodes."""
```

## Integration Strategy

### With ooai-core

1. **Dynamic Model Integration**: Nodes and edges as DynamicBaseModel instances
2. **Engine Integration**: Graphs as BaseEngine implementations
3. **Composition System**: Graph components composable with other models
4. **Validation Integration**: Graph validators using ooai-core patterns

### With LangGraph (Optional)

1. **Workflow Layer**: Optional LangGraph compatibility layer
2. **State Management**: Enhanced state management building on LangGraph patterns
3. **Tool Integration**: Graph nodes as tools in LangGraph workflows

## Implementation Phases

### Phase 1: Core Components
- [ ] Node, Edge, Branch implementations
- [ ] Basic Graph data structure
- [ ] Core topology analysis
- [ ] Basic validation

### Phase 2: State Management
- [ ] StateGraph implementation
- [ ] State transitions and persistence
- [ ] Execution engine

### Phase 3: Advanced Features
- [ ] Pattern library
- [ ] Validators and constraints
- [ ] Schema composition

### Phase 4: Integration
- [ ] Engine integration
- [ ] ooai-core integration
- [ ] Workflow capabilities

### Phase 5: Algorithms & Visualization
- [ ] Algorithm library
- [ ] Visualization tools
- [ ] Performance optimization

## Design Principles

1. **Type Safety**: Comprehensive typing with Pydantic validation
2. **Composability**: All components composable with ooai-core systems
3. **Extensibility**: Easy to extend with new node/edge types
4. **Performance**: Efficient for both small and large graphs
5. **Integration**: Seamless integration with existing OOAI ecosystem
6. **Validation**: Comprehensive validation at all levels
7. **Patterns**: Rich library of common graph patterns

---

**Design Status**: Architecture defined, ready for implementation planning
**Next Step**: Begin Phase 1 implementation with core components
**Focus**: Core graph theory with modern state management and integration