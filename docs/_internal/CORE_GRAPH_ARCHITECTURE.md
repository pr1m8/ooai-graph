# OOAI Graph Core Architecture - LangGraph Integration Focus

## Core Philosophy

Build on LangGraph's proven StateGraph/MessageGraph foundation while adding recompilation capabilities and ooai-core integration. Focus on core graph operations, dynamic modification, and seamless LangGraph interoperability.

## Core Graph Foundation

### 1. LangGraph Integration Layer

```python
from langgraph.graph.state import StateGraph as LangStateGraph
from langgraph.graph.message import MessageGraph as LangMessageGraph

class OOAIStateGraph(LangStateGraph):
    """Extended StateGraph with ooai-core integration and recompilation."""

    def __init__(self, state_schema=None, **kwargs):
        super().__init__(state_schema, **kwargs)
        self._ooai_metadata = {}
        self._recompilation_hooks = []

    def recompile(self) -> 'OOAIStateGraph':
        """Recompile graph with current modifications."""

    def add_ooai_node(self, node_id: str, node_func: callable, **metadata):
        """Add node with ooai-core metadata tracking."""

    def link_to_langgraph(self) -> LangStateGraph:
        """Export as pure LangGraph for compatibility."""
```

### 2. Core Graph Operations

**Essential Operations:**
- Graph construction and modification
- Node/edge addition and removal
- Dynamic recompilation and reconstruction
- State schema evolution
- Checkpoint and restore capabilities

**Recompilation Engine:**
```python
class GraphRecompiler:
    """Handles dynamic graph modification and recompilation."""

    def __init__(self, base_graph: OOAIStateGraph):
        self.base_graph = base_graph
        self.modification_stack = []
        self.compiled_cache = {}

    def add_modification(self, modification: GraphModification):
        """Queue a graph modification."""

    def recompile(self) -> OOAIStateGraph:
        """Apply all modifications and recompile graph."""

    def rollback(self, steps: int = 1) -> OOAIStateGraph:
        """Rollback modifications and recompile."""

    def checkpoint(self, name: str):
        """Create named checkpoint of current graph state."""

    def restore(self, name: str) -> OOAIStateGraph:
        """Restore graph to named checkpoint."""
```

### 3. Graph Modification System

**Modification Types:**
```python
class GraphModification(BaseModel):
    """Base class for graph modifications."""
    modification_type: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AddNodeModification(GraphModification):
    node_id: str
    node_function: callable
    node_metadata: Dict[str, Any]

class RemoveNodeModification(GraphModification):
    node_id: str
    preserve_edges: bool = False

class AddEdgeModification(GraphModification):
    source: str
    target: str
    condition: Optional[callable] = None

class UpdateStateSchemaModification(GraphModification):
    new_schema: Type[BaseModel]
    migration_strategy: str = "merge"
```

## LangGraph.Graph Integration

### 1. Direct LangGraph Compatibility

**Seamless Interoperability:**
```python
# Convert between OOAI and LangGraph formats
def to_langgraph(ooai_graph: OOAIStateGraph) -> LangStateGraph:
    """Convert OOAI graph to pure LangGraph."""

def from_langgraph(lang_graph: LangStateGraph) -> OOAIStateGraph:
    """Import LangGraph and add OOAI capabilities."""

# Maintain compatibility with existing LangGraph patterns
class LangGraphAdapter:
    """Adapter for seamless LangGraph integration."""

    def __init__(self, ooai_graph: OOAIStateGraph):
        self.ooai_graph = ooai_graph
        self._lang_graph = None

    @property
    def langgraph(self) -> LangStateGraph:
        """Get LangGraph representation."""
        if self._lang_graph is None:
            self._lang_graph = to_langgraph(self.ooai_graph)
        return self._lang_graph

    def sync_from_langgraph(self):
        """Sync changes from LangGraph back to OOAI."""
```

### 2. LangGraph Feature Extensions

**Enhanced State Management:**
- Integration with ooai-core DynamicBaseModel for state schemas
- Dynamic state schema evolution during runtime
- State validation with Pydantic models
- State composition and merging strategies

**Advanced Execution Patterns:**
- Conditional execution with complex branching
- Parallel execution with synchronization points
- Loop detection and handling
- Timeout and error recovery mechanisms

## Core Graph Data Structure

### 1. Graph Representation

```python
class CoreGraph(BaseModel):
    """Core graph data structure extending LangGraph capabilities."""

    # Core structure (compatible with LangGraph)
    nodes: Dict[str, GraphNode] = Field(default_factory=dict)
    edges: Dict[str, GraphEdge] = Field(default_factory=dict)

    # OOAI extensions
    state_schema: Optional[Type[DynamicBaseModel]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    recompilation_hooks: List[callable] = Field(default_factory=list)

    # LangGraph compatibility
    _langgraph_instance: Optional[LangStateGraph] = None

    def add_node(self, node_id: str, node_func: callable, **kwargs):
        """Add node with both OOAI and LangGraph tracking."""

    def add_edge(self, source: str, target: str, condition: Optional[callable] = None):
        """Add edge with recompilation tracking."""

    def compile(self) -> LangStateGraph:
        """Compile to LangGraph for execution."""

    def recompile(self) -> LangStateGraph:
        """Recompile with current modifications."""
```

### 2. Node and Edge Definitions

**GraphNode Integration:**
```python
class GraphNode(BaseModel):
    """Node compatible with LangGraph but extended for OOAI."""

    node_id: str
    function: callable
    input_schema: Optional[Type[BaseModel]] = None
    output_schema: Optional[Type[BaseModel]] = None

    # OOAI extensions
    ooai_metadata: Dict[str, Any] = Field(default_factory=dict)
    dynamic_schema: Optional[Type[DynamicBaseModel]] = None
    recompilation_strategy: str = "preserve"

    def to_langgraph_node(self) -> dict:
        """Convert to LangGraph node format."""

    def update_schema(self, new_schema: Type[BaseModel]):
        """Update node schema and trigger recompilation."""
```

**GraphEdge Integration:**
```python
class GraphEdge(BaseModel):
    """Edge compatible with LangGraph conditional edges."""

    source: str
    target: str
    condition: Optional[callable] = None

    # OOAI extensions
    edge_metadata: Dict[str, Any] = Field(default_factory=dict)
    dynamic_condition: bool = False

    def to_langgraph_edge(self) -> dict:
        """Convert to LangGraph edge format."""

    def update_condition(self, new_condition: callable):
        """Update edge condition and trigger recompilation."""
```

## Recompilation System

### 1. Dynamic Modification Engine

**Core Recompilation Features:**
- Incremental graph modification without full reconstruction
- Dependency tracking for efficient recompilation
- State preservation during graph changes
- Rollback and checkpoint capabilities

**Recompilation Strategies:**
```python
class RecompilationStrategy(Enum):
    FULL = "full"           # Complete reconstruction
    INCREMENTAL = "incremental"  # Only changed components
    LAZY = "lazy"           # Recompile on next execution
    IMMEDIATE = "immediate"  # Recompile immediately

class GraphRecompiler:
    def __init__(self, strategy: RecompilationStrategy = RecompilationStrategy.INCREMENTAL):
        self.strategy = strategy
        self.modification_queue = []
        self.dependency_graph = {}

    def schedule_recompilation(self, graph: CoreGraph) -> LangStateGraph:
        """Schedule and execute graph recompilation."""

    def track_dependencies(self, modification: GraphModification):
        """Track what needs recompilation based on modification."""
```

### 2. State Schema Evolution

**Dynamic Schema Updates:**
```python
class SchemaEvolutionManager:
    """Manages state schema changes during graph recompilation."""

    def __init__(self, base_schema: Type[DynamicBaseModel]):
        self.base_schema = base_schema
        self.evolution_history = []

    def evolve_schema(
        self,
        changes: Dict[str, Any],
        migration_strategy: str = "merge"
    ) -> Type[DynamicBaseModel]:
        """Evolve state schema with migration strategy."""

    def migrate_state(
        self,
        old_state: Dict[str, Any],
        new_schema: Type[DynamicBaseModel]
    ) -> Dict[str, Any]:
        """Migrate existing state to new schema."""
```

## Integration Architecture

### 1. OOAI-Core Integration

**DynamicBaseModel Integration:**
- Use DynamicBaseModel for node/edge schemas
- Runtime field modification and validation
- Composition with other ooai-core models
- Schema inheritance and mixins

**Engine Integration:**
- GraphEngine extending BaseEngine
- Direct integration with ooai-core engine composition
- Workflow orchestration with other engines

### 2. LangGraph Compatibility Layer

**Bidirectional Compatibility:**
```python
class LangGraphCompatibility:
    """Ensures seamless LangGraph integration."""

    @staticmethod
    def export_to_langgraph(ooai_graph: CoreGraph) -> LangStateGraph:
        """Export OOAI graph as pure LangGraph."""

    @staticmethod
    def import_from_langgraph(lang_graph: LangStateGraph) -> CoreGraph:
        """Import LangGraph and add OOAI capabilities."""

    @staticmethod
    def validate_compatibility(graph: CoreGraph) -> bool:
        """Validate that graph is LangGraph compatible."""
```

## Implementation Priority

### Phase 1: Core Integration
1. **LangGraph StateGraph Extension** - Basic OOAIStateGraph
2. **Core Graph Data Structure** - Nodes, edges, basic operations
3. **LangGraph Compatibility** - Import/export, validation

### Phase 2: Recompilation Engine
1. **Modification System** - GraphModification classes
2. **Recompilation Engine** - Core recompilation logic
3. **State Schema Evolution** - Dynamic schema updates

### Phase 3: Advanced Features
1. **Advanced Execution Patterns** - Complex branching, loops
2. **Performance Optimization** - Efficient recompilation
3. **Integration Patterns** - Deep ooai-core integration

## Success Criteria

**Core Graph Success:**
- ✅ Seamless LangGraph StateGraph/MessageGraph integration
- ✅ Dynamic graph modification and recompilation
- ✅ State schema evolution without execution interruption
- ✅ Bidirectional LangGraph compatibility

**Recompilation Success:**
- ✅ Incremental recompilation performance
- ✅ State preservation during modifications
- ✅ Rollback and checkpoint functionality
- ✅ Dependency tracking accuracy

**Integration Success:**
- ✅ Full ooai-core DynamicBaseModel integration
- ✅ Engine composition compatibility
- ✅ Existing LangGraph workflow compatibility
- ✅ Performance parity with pure LangGraph

---

**Focus**: Core graph operations, recompilation capabilities, seamless LangGraph integration
**Strategy**: Extend rather than replace LangGraph, add OOAI-specific capabilities
**Goal**: Best-of-both-worlds - LangGraph maturity + OOAI flexibility