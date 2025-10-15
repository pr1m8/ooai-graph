# LangGraph Adaptation Strategy

## Core Principle: Extend, Don't Replace

Adapt LangGraph's proven StateGraph and MessageGraph implementations rather than building competing solutions. Add OOAI-specific capabilities through extension and composition patterns.

## LangGraph Integration Points

### 1. Direct StateGraph Extension

```python
from langgraph.graph.state import StateGraph
from ooai.core.models import DynamicBaseModel

class OOAIStateGraph(StateGraph):
    """StateGraph extended with OOAI capabilities."""

    def __init__(self, state_schema=None, **kwargs):
        # Use DynamicBaseModel if no schema provided
        if state_schema is None:
            state_schema = DynamicBaseModel
        super().__init__(state_schema, **kwargs)

        # OOAI extensions
        self._ooai_metadata = {}
        self._recompilation_context = RecompilationContext()
        self._schema_evolution_manager = SchemaEvolutionManager(state_schema)

    def add_ooai_node(self, node_id: str, node_func: callable, **ooai_metadata):
        """Add node with OOAI metadata and recompilation tracking."""
        self.add_node(node_id, node_func)
        self._ooai_metadata[node_id] = ooai_metadata
        self._recompilation_context.track_addition("node", node_id)

    def recompile(self) -> 'OOAIStateGraph':
        """Recompile graph with accumulated modifications."""
        return self._recompilation_context.execute_recompilation(self)

    def evolve_schema(self, schema_changes: Dict) -> 'OOAIStateGraph':
        """Evolve state schema dynamically."""
        new_schema = self._schema_evolution_manager.evolve(schema_changes)
        return self._create_evolved_graph(new_schema)
```

### 2. LangGraph MessageGraph Adaptation

```python
from langgraph.graph.message import MessageGraph, MessagesState

class OOAIMessageGraph(MessageGraph):
    """MessageGraph with OOAI dynamic capabilities."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._message_schema_composer = MessageSchemaComposer()
        self._dynamic_routing = DynamicRoutingManager()

    def add_dynamic_router(self, router_func: callable, conditions: Dict):
        """Add router that can be modified at runtime."""
        router_id = self._dynamic_routing.register_router(router_func, conditions)
        self.add_conditional_edges(router_id, router_func)
        return router_id

    def update_routing_conditions(self, router_id: str, new_conditions: Dict):
        """Update routing conditions and recompile."""
        self._dynamic_routing.update_conditions(router_id, new_conditions)
        return self.recompile()
```

### 3. Bidirectional Compatibility Layer

```python
class LangGraphAdapter:
    """Seamless adaptation between OOAI and pure LangGraph."""

    @staticmethod
    def to_langgraph(ooai_graph: OOAIStateGraph) -> StateGraph:
        """Convert OOAI graph to pure LangGraph for compatibility."""
        lang_graph = StateGraph(ooai_graph.schema)

        # Transfer nodes (strip OOAI metadata)
        for node_id, node in ooai_graph.nodes.items():
            lang_graph.add_node(node_id, node.func)

        # Transfer edges
        for edge in ooai_graph.edges:
            if hasattr(edge, 'condition'):
                lang_graph.add_conditional_edges(edge.source, edge.condition)
            else:
                lang_graph.add_edge(edge.source, edge.target)

        return lang_graph.compile()

    @staticmethod
    def from_langgraph(lang_graph: StateGraph) -> OOAIStateGraph:
        """Import LangGraph and add OOAI capabilities."""
        ooai_graph = OOAIStateGraph(lang_graph.schema)

        # Import structure with OOAI extensions
        for node_id, node in lang_graph.nodes.items():
            ooai_graph.add_ooai_node(node_id, node.func, imported=True)

        return ooai_graph

    @staticmethod
    def sync_changes(ooai_graph: OOAIStateGraph, lang_graph: StateGraph):
        """Sync changes between OOAI and LangGraph instances."""
        # Implementation for bidirectional sync
        pass
```

## Recompilation Through LangGraph

### 1. LangGraph-Native Recompilation

```python
class LangGraphRecompiler:
    """Recompilation engine that works with LangGraph's compilation model."""

    def __init__(self, base_graph: OOAIStateGraph):
        self.base_graph = base_graph
        self.modification_queue = []
        self.compiled_cache = {}

    def add_modification(self, mod: GraphModification):
        """Queue modification that preserves LangGraph compatibility."""
        self.modification_queue.append(mod)
        self._invalidate_cache()

    def recompile(self) -> StateGraph:
        """Apply modifications and compile using LangGraph's compile()."""
        # Apply all queued modifications
        modified_graph = self._apply_modifications()

        # Use LangGraph's native compilation
        compiled = modified_graph.compile()

        # Cache for future use
        self.compiled_cache = compiled
        return compiled

    def _apply_modifications(self) -> OOAIStateGraph:
        """Apply modifications while maintaining LangGraph structure."""
        working_graph = self.base_graph.copy()

        for mod in self.modification_queue:
            if isinstance(mod, AddNodeModification):
                working_graph.add_node(mod.node_id, mod.node_func)
            elif isinstance(mod, AddEdgeModification):
                working_graph.add_edge(mod.source, mod.target, mod.condition)
            # ... other modifications

        return working_graph
```

### 2. State Schema Evolution with LangGraph

```python
class LangGraphSchemaEvolution:
    """Schema evolution that maintains LangGraph compatibility."""

    def __init__(self, initial_schema):
        self.schema_history = [initial_schema]
        self.migration_strategies = {}

    def evolve_schema(
        self,
        current_graph: OOAIStateGraph,
        schema_changes: Dict
    ) -> OOAIStateGraph:
        """Evolve schema while preserving LangGraph functionality."""

        # Create new schema using DynamicBaseModel composition
        current_schema = self.schema_history[-1]
        new_schema = self._compose_evolved_schema(current_schema, schema_changes)

        # Create new graph with evolved schema
        evolved_graph = OOAIStateGraph(new_schema)

        # Transfer nodes and edges from current graph
        self._transfer_graph_structure(current_graph, evolved_graph)

        # Set up state migration
        evolved_graph._state_migrator = self._create_migrator(
            current_schema, new_schema
        )

        return evolved_graph

    def _compose_evolved_schema(self, base_schema, changes):
        """Use ooai-core composition to evolve schema."""
        from ooai.core.models.dynamic_base_model import compose_models

        # Create change model
        change_model = self._create_change_model(changes)

        # Compose with base schema
        return compose_models(base_schema, change_model)
```

## Integration Patterns

### 1. OOAI-Core Model Integration

```python
from ooai.core.models import DynamicBaseModel
from ooai.core.models.dynamic_base_model import compose_models

class GraphModelIntegration:
    """Integration between graph schemas and ooai-core models."""

    @staticmethod
    def create_graph_with_composed_state(models: List[Type[DynamicBaseModel]]) -> OOAIStateGraph:
        """Create graph with state schema composed from multiple models."""
        composed_schema = compose_models(*models)
        return OOAIStateGraph(composed_schema)

    @staticmethod
    def add_model_to_graph_state(
        graph: OOAIStateGraph,
        model: Type[DynamicBaseModel]
    ) -> OOAIStateGraph:
        """Add model fields to existing graph state schema."""
        current_schema = graph.schema
        new_schema = compose_models(current_schema, model)
        return graph.evolve_schema({"add_model": model})
```

### 2. Engine Integration Through LangGraph

```python
from ooai.core.engine.base import BaseEngine

class GraphEngineAdapter(BaseEngine):
    """BaseEngine that wraps LangGraph execution."""

    def __init__(self, ooai_graph: OOAIStateGraph):
        self.ooai_graph = ooai_graph
        self.compiled_graph = None

    def _process(self, input_data: Dict, **kwargs) -> Dict:
        """Execute graph using LangGraph's invoke method."""
        if self.compiled_graph is None:
            self.compiled_graph = self.ooai_graph.compile()

        return self.compiled_graph.invoke(input_data)

    def _get_input_schema_class(self) -> Type[BaseModel]:
        """Return graph's input schema."""
        return self.ooai_graph.schema

    def _get_output_schema_class(self) -> Type[BaseModel]:
        """Return graph's output schema."""
        return self.ooai_graph.schema

    def recompile_and_update(self):
        """Recompile graph and update engine."""
        self.compiled_graph = self.ooai_graph.recompile()
```

## Implementation Strategy

### Phase 1: Core LangGraph Extension
1. **OOAIStateGraph**: Extend StateGraph with OOAI metadata
2. **OOAIMessageGraph**: Extend MessageGraph with dynamic capabilities
3. **LangGraphAdapter**: Bidirectional compatibility layer

### Phase 2: Recompilation Integration
1. **LangGraphRecompiler**: Recompilation using LangGraph's compile()
2. **Modification System**: Graph modifications that preserve LangGraph structure
3. **Schema Evolution**: Dynamic schema changes with LangGraph compatibility

### Phase 3: Deep Integration
1. **Model Composition**: DynamicBaseModel integration with graph schemas
2. **Engine Integration**: GraphEngineAdapter for BaseEngine compatibility
3. **Workflow Orchestration**: Multi-graph workflows using LangGraph patterns

## Benefits of LangGraph Adaptation

### 1. Proven Foundation
- **Mature codebase**: LangGraph is production-tested
- **Active development**: Continuous improvements and bug fixes
- **Community support**: Established ecosystem and documentation

### 2. Compatibility
- **Existing workflows**: Works with current LangGraph implementations
- **Tool integration**: Compatible with LangGraph tools and utilities
- **Migration path**: Easy migration from pure LangGraph to OOAI

### 3. Performance
- **Optimized execution**: Benefit from LangGraph's performance optimizations
- **Memory efficiency**: LangGraph's efficient graph representation
- **Scalability**: Proven scalability patterns

## Success Criteria

**Adaptation Success:**
- ✅ 100% LangGraph StateGraph/MessageGraph compatibility
- ✅ Seamless import/export of LangGraph instances
- ✅ OOAI features work without breaking LangGraph functionality
- ✅ Performance parity with pure LangGraph

**Integration Success:**
- ✅ DynamicBaseModel schemas work as LangGraph state
- ✅ Graph recompilation preserves LangGraph execution model
- ✅ OOAI engines can execute LangGraph workflows
- ✅ Schema evolution works with LangGraph state management

---

**Strategy**: Build on LangGraph's strengths, add OOAI capabilities through extension
**Goal**: Best of both worlds - LangGraph maturity + OOAI flexibility + seamless interoperability