# CLAUDE.md - OOAI Graph Package Documentation

## Master Index

### Core Documentation Groups

- [@project-overview](#project-overview) - Graph algorithms and data structures
- [@project-setup](#project-setup) - Environment setup and development
- [@pdm-workflows](#pdm-workflows) - PDM commands and dependency management
- [@architecture](#architecture) - Graph system design and module structure
- [@algorithm-patterns](#algorithm-patterns) - Standard algorithm implementation patterns

### Technical References

- [@graph-algorithms](#graph-algorithms) - Core algorithms and implementations
- [@data-structures](#data-structures) - Graph representations and optimizations
- [@performance-optimization](#performance-optimization) - Performance patterns and benchmarking
- [@testing-framework](#testing-framework) - Testing patterns for graph algorithms
- [@visualization](#visualization) - Graph plotting and interactive tools

### Development Workflow

- [@development-workflow](#development-workflow) - Git, commits, testing workflow
- [@code-standards](#code-standards) - Algorithm coding standards and documentation
- [@integration-patterns](#integration-patterns) - Integration with ooai-core and other packages

### External Documentation

- [`docs/ADVANCED_TESTING.md`](docs/ADVANCED_TESTING.md) - Comprehensive testing strategies
- [`docs/CODE_STANDARDS.md`](docs/CODE_STANDARDS.md) - Complete code standards guide
- [`examples/README.md`](examples/README.md) - Examples documentation and usage guide
- [`scripts/README.md`](scripts/README.md) - Script utilities documentation

### Working Memory

- [@session-logs](#session-logs) - Development history and decisions
- [@research-notes](#research-notes) - Algorithm research and implementation notes
- [@troubleshooting](#troubleshooting) - Common issues and solutions
- [@performance-benchmarks](#performance-benchmarks) - Algorithm performance data

### Internal Documentation

- [`docs/_internal/GRAPH_DEVELOPMENT_NOTES.md`](docs/_internal/GRAPH_DEVELOPMENT_NOTES.md) - Algorithm design decisions and implementation notes
- [`docs/_internal/SESSION_LOGS.md`](docs/_internal/SESSION_LOGS.md) - Detailed development session logs and technical decisions

---

## @project-overview

**OOAI Graph** - Graph algorithms, data structures, and network analysis toolkit

### Key Capabilities

- **Graph Data Structures**: Efficient representations (adjacency list, matrix, CSR)
- **Core Algorithms**: Shortest paths, centrality measures, clustering, traversal
- **Network Analysis**: Community detection, influence analysis, connectivity metrics
- **Performance Optimization**: Memory-efficient algorithms for large graphs
- **Visualization**: Interactive graph plotting and network visualization
- **Integration**: Seamless integration with ooai-core dynamic models

### Quick Usage Examples

```python
# Basic graph operations
from ooai.graph import Graph, Node, Edge
graph = Graph()
graph.add_node("A", data={"type": "entity", "weight": 1.0})
graph.add_edge("A", "B", weight=1.5, directed=False)

# Algorithm usage
from ooai.graph.algorithms import shortest_path, centrality
path = shortest_path.dijkstra(graph, "A", "B")
scores = centrality.betweenness(graph)

# Performance-optimized operations
from ooai.graph.algorithms import batch_shortest_paths
paths = batch_shortest_paths(graph, sources=["A", "B"], algorithm="dijkstra")

# Integration with ooai-core
from ooai.core.models import DynamicBaseModel
from ooai.graph.models import GraphModel

class EntityGraph(GraphModel, DynamicBaseModel):
    entities: List[str]
    relationships: List[Edge]

    def compute_centrality(self) -> Dict[str, float]:
        return centrality.betweenness(self.to_graph())
```

### Algorithm Categories

- **Path Algorithms**: Dijkstra, A*, Floyd-Warshall, Johnson's algorithm
- **Centrality Measures**: Betweenness, closeness, eigenvector, PageRank
- **Clustering**: K-means clustering, hierarchical clustering, community detection
- **Graph Analysis**: Connected components, cycles, topological sorting
- **Optimization**: Maximum flow, minimum spanning tree, graph coloring

---

## @architecture

### Project Structure

```
src/ooai/graph/
├── core/
│   ├── __init__.py
│   ├── graph.py                      # Core Graph class
│   ├── node.py                       # Node implementation
│   ├── edge.py                       # Edge implementation
│   ├── representations.py            # Graph representations (adj list, matrix)
│   └── exceptions.py                 # Graph-specific exceptions
├── algorithms/
│   ├── __init__.py
│   ├── shortest_path/
│   │   ├── __init__.py
│   │   ├── dijkstra.py              # Dijkstra's algorithm
│   │   ├── astar.py                 # A* algorithm
│   │   ├── floyd_warshall.py        # All-pairs shortest paths
│   │   └── utils.py                 # Path algorithm utilities
│   ├── centrality/
│   │   ├── __init__.py
│   │   ├── betweenness.py           # Betweenness centrality
│   │   ├── closeness.py             # Closeness centrality
│   │   ├── eigenvector.py           # Eigenvector centrality
│   │   └── pagerank.py              # PageRank algorithm
│   ├── clustering/
│   │   ├── __init__.py
│   │   ├── kmeans.py                # K-means clustering
│   │   ├── hierarchical.py          # Hierarchical clustering
│   │   └── community.py             # Community detection
│   ├── traversal/
│   │   ├── __init__.py
│   │   ├── dfs.py                   # Depth-first search
│   │   ├── bfs.py                   # Breadth-first search
│   │   └── topological.py           # Topological sorting
│   └── flow/
│       ├── __init__.py
│       ├── max_flow.py              # Maximum flow algorithms
│       └── min_cut.py               # Minimum cut algorithms
├── models/
│   ├── __init__.py
│   ├── graph_model.py               # Pydantic graph models
│   ├── node_model.py                # Pydantic node models
│   └── edge_model.py                # Pydantic edge models
├── visualization/
│   ├── __init__.py
│   ├── plotters.py                  # Graph plotting utilities
│   ├── interactive.py               # Interactive visualization
│   └── layouts.py                   # Graph layout algorithms
├── integration/
│   ├── __init__.py
│   ├── core_integration.py          # Integration with ooai-core
│   └── adapters.py                  # Adapters for external formats
├── utils/
│   ├── __init__.py
│   ├── generators.py                # Graph generators (random, scale-free)
│   ├── io.py                        # Graph I/O operations
│   └── validation.py                # Graph validation utilities
└── benchmarks/
    ├── __init__.py
    ├── algorithm_benchmarks.py      # Algorithm performance tests
    └── memory_benchmarks.py         # Memory usage benchmarks
```

### Module Dependencies

```python
# Core graph system
graph.core → algorithms → models
              ↓
         visualization
              ↓
         integration
```

---

## @algorithm-patterns

### Standard Algorithm Implementation Pattern

Every algorithm in ooai-graph follows this consistent pattern:

```python
from typing import Dict, List, Optional, Union
from ooai.graph.core import Graph
from ooai.graph.core.exceptions import GraphError

def algorithm_name(
    graph: Graph,
    source: Optional[str] = None,
    target: Optional[str] = None,
    **kwargs
) -> AlgorithmResult:
    """Algorithm description following Google docstring format.

    Args:
        graph (`Graph`): Input graph for computation
        source (`Optional[str]`): Source node identifier
        target (`Optional[str]`): Target node identifier
        **kwargs: Algorithm-specific parameters

    Returns:
        `AlgorithmResult`: Structured result with computation data and metadata

    Raises:
        `GraphError`: When graph preconditions are not met
        `ValueError`: When parameters are invalid

    Example:
        >>> graph = Graph()
        >>> graph.add_edge("A", "B", weight=1.0)
        >>> result = algorithm_name(graph, source="A", target="B")
        >>> print(result.value)
        1.0

    Time Complexity:
        O(V + E) where V is vertices and E is edges

    Space Complexity:
        O(V) for auxiliary data structures
    """
    # 1. Input validation
    if not isinstance(graph, Graph):
        raise TypeError("Expected Graph instance")

    if graph.is_empty():
        raise GraphError("Cannot run algorithm on empty graph")

    # 2. Algorithm-specific validation
    if source and source not in graph:
        raise ValueError(f"Source node '{source}' not found in graph")

    # 3. Initialize data structures
    distances = {}
    predecessors = {}
    visited = set()

    # 4. Algorithm implementation
    # ... algorithm-specific logic ...

    # 5. Return structured result
    return AlgorithmResult(
        algorithm="algorithm_name",
        graph_info=GraphInfo(
            num_nodes=len(graph.nodes),
            num_edges=len(graph.edges),
            is_directed=graph.is_directed()
        ),
        computation_time=time.time() - start_time,
        memory_usage=get_memory_usage(),
        result=result_data,
        metadata={"source": source, "target": target}
    )
```

### Algorithm Result Pattern

```python
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class AlgorithmResult:
    """Standardized result format for all graph algorithms."""
    algorithm: str                    # Algorithm name
    graph_info: GraphInfo            # Graph metadata
    computation_time: float          # Execution time in seconds
    memory_usage: Optional[int]      # Memory usage in bytes
    result: Any                      # Algorithm-specific result
    metadata: Dict[str, Any]         # Additional algorithm metadata

    def __str__(self) -> str:
        return f"{self.algorithm}: {self.result} (time: {self.computation_time:.4f}s)"

@dataclass
class GraphInfo:
    """Graph metadata for algorithm results."""
    num_nodes: int
    num_edges: int
    is_directed: bool
    is_weighted: bool = False
    is_connected: Optional[bool] = None
```

---

## @graph-algorithms

### Shortest Path Algorithms

#### Dijkstra's Algorithm

```python
from ooai.graph.algorithms.shortest_path import dijkstra

# Single source shortest paths
result = dijkstra(graph, source="A")
distances = result.result["distances"]
paths = result.result["paths"]

# Single source-target path
result = dijkstra(graph, source="A", target="B")
shortest_path = result.result["path"]
distance = result.result["distance"]
```

#### A* Algorithm

```python
from ooai.graph.algorithms.shortest_path import astar

# Requires heuristic function
def heuristic(node1: str, node2: str) -> float:
    # Manhattan distance for grid graphs
    pos1 = graph.get_node_data(node1)["position"]
    pos2 = graph.get_node_data(node2)["position"]
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

result = astar(graph, source="A", target="B", heuristic=heuristic)
```

### Centrality Algorithms

#### Betweenness Centrality

```python
from ooai.graph.algorithms.centrality import betweenness

# All nodes betweenness
result = betweenness(graph)
centrality_scores = result.result

# Normalized betweenness
result = betweenness(graph, normalized=True)

# Subset of nodes
result = betweenness(graph, nodes=["A", "B", "C"])
```

#### PageRank

```python
from ooai.graph.algorithms.centrality import pagerank

# Basic PageRank
result = pagerank(graph, damping_factor=0.85, max_iterations=100)
scores = result.result

# With personalization vector
personalization = {"A": 1.0, "B": 0.0}  # Favor node A
result = pagerank(graph, personalization=personalization)
```

### Algorithm Selection Guidelines

```python
def choose_shortest_path_algorithm(graph: Graph, source: str, target: Optional[str] = None) -> str:
    """Choose optimal shortest path algorithm based on graph characteristics."""
    num_nodes = len(graph.nodes)
    num_edges = len(graph.edges)
    density = num_edges / (num_nodes * (num_nodes - 1) / 2)

    if target is None:  # Single source, all destinations
        if graph.has_negative_weights():
            return "bellman_ford"
        elif density > 0.5:  # Dense graph
            return "dijkstra_dense"
        else:
            return "dijkstra"

    else:  # Single source-target
        if graph.has_heuristic_data():
            return "astar"
        else:
            return "dijkstra"
```

---

## @data-structures

### Graph Representations

#### Adjacency List (Default)

```python
from ooai.graph.core import Graph

# Most memory-efficient for sparse graphs
graph = Graph(representation="adjacency_list")
graph.add_edge("A", "B", weight=1.5)

# Access patterns
neighbors = graph.neighbors("A")  # O(degree(A))
edge_weight = graph.get_edge_weight("A", "B")  # O(degree(A))
```

#### Adjacency Matrix

```python
# Better for dense graphs and matrix operations
graph = Graph(representation="adjacency_matrix")

# Faster edge queries O(1) but more memory O(V²)
has_edge = graph.has_edge("A", "B")  # O(1)
```

#### Compressed Sparse Row (CSR)

```python
# Optimized for large, sparse graphs in algorithms
graph = Graph(representation="csr")

# Best for algorithms that iterate over all edges
for u, v, weight in graph.edges():  # Very cache-friendly
    process_edge(u, v, weight)
```

### Memory Optimization Patterns

```python
class MemoryOptimizedGraph:
    """Memory-efficient graph for large datasets."""

    def __init__(self, estimated_nodes: int, estimated_edges: int):
        # Pre-allocate based on estimates
        self._nodes = {}  # Use slots for node objects
        self._edges = {}  # Compact edge representation

    @property
    def memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return sum(sys.getsizeof(obj) for obj in [self._nodes, self._edges])

    def optimize_memory(self):
        """Optimize memory layout after construction."""
        # Convert to more compact representations
        self._compact_node_ids()
        self._compress_edge_data()
```

---

## @performance-optimization

### Algorithm Performance Guidelines

#### Time Complexity Reference

| Algorithm | Best Case | Average Case | Worst Case | Space |
|-----------|-----------|--------------|------------|-------|
| Dijkstra | O((V + E) log V) | O((V + E) log V) | O((V + E) log V) | O(V) |
| A* | O(E) | O(E) | O(V²) | O(V) |
| BFS | O(V + E) | O(V + E) | O(V + E) | O(V) |
| DFS | O(V + E) | O(V + E) | O(V + E) | O(V) |
| Betweenness | O(VE) | O(VE) | O(V³) | O(V²) |
| PageRank | O(V + E) | O(kE) | O(kE) | O(V) |

#### Performance Optimization Patterns

```python
# 1. Batch Operations
def batch_shortest_paths(graph: Graph, sources: List[str], algorithm: str = "dijkstra"):
    """Compute shortest paths from multiple sources efficiently."""
    # Reuse data structures across computations
    distance_matrix = {}
    path_matrix = {}

    for source in sources:
        result = algorithm_map[algorithm](graph, source)
        distance_matrix[source] = result.result["distances"]
        path_matrix[source] = result.result["paths"]

    return {"distances": distance_matrix, "paths": path_matrix}

# 2. Memory-Efficient Algorithms
def memory_efficient_betweenness(graph: Graph, chunk_size: int = 1000):
    """Compute betweenness centrality in memory-efficient chunks."""
    nodes = list(graph.nodes)
    centrality = {node: 0.0 for node in nodes}

    for i in range(0, len(nodes), chunk_size):
        chunk = nodes[i:i + chunk_size]
        chunk_result = betweenness_subset(graph, chunk)

        for node, score in chunk_result.items():
            centrality[node] += score

    return centrality

# 3. Parallel Processing
import multiprocessing as mp

def parallel_centrality(graph: Graph, num_processes: int = None):
    """Compute centrality measures using multiple processes."""
    if num_processes is None:
        num_processes = mp.cpu_count()

    nodes = list(graph.nodes)
    chunk_size = len(nodes) // num_processes

    with mp.Pool(num_processes) as pool:
        tasks = [
            (graph, nodes[i:i + chunk_size])
            for i in range(0, len(nodes), chunk_size)
        ]
        results = pool.starmap(betweenness_chunk, tasks)

    # Combine results
    final_centrality = {}
    for partial_result in results:
        final_centrality.update(partial_result)

    return final_centrality
```

### Benchmarking Framework

```python
import time
import psutil
from contextlib import contextmanager
from typing import Callable, Dict, Any

@contextmanager
def benchmark_algorithm(algorithm_name: str):
    """Context manager for benchmarking graph algorithms."""
    process = psutil.Process()

    # Pre-benchmark state
    start_memory = process.memory_info().rss
    start_time = time.perf_counter()

    try:
        yield
    finally:
        # Post-benchmark measurements
        end_time = time.perf_counter()
        end_memory = process.memory_info().rss

        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory

        print(f"{algorithm_name}:")
        print(f"  Execution time: {execution_time:.4f}s")
        print(f"  Memory usage: {memory_delta / 1024 / 1024:.2f} MB")

# Usage
with benchmark_algorithm("Dijkstra"):
    result = dijkstra(large_graph, source="A")
```

---

## @testing-framework

### Graph Algorithm Testing Patterns

#### Property-Based Testing

```python
import pytest
from hypothesis import given, strategies as st
from ooai.graph.utils.generators import random_graph
from ooai.graph.algorithms.shortest_path import dijkstra

@given(
    num_nodes=st.integers(min_value=5, max_value=50),
    edge_probability=st.floats(min_value=0.1, max_value=0.8),
    seed=st.integers(min_value=1, max_value=1000)
)
def test_dijkstra_properties(num_nodes: int, edge_probability: float, seed: int):
    """Property-based test for Dijkstra's algorithm."""
    graph = random_graph(num_nodes, edge_probability, seed=seed, weighted=True)

    if len(graph.nodes) < 2:
        return  # Skip trivial cases

    source = list(graph.nodes)[0]
    result = dijkstra(graph, source=source)
    distances = result.result["distances"]

    # Property 1: Distance to source is always 0
    assert distances[source] == 0.0

    # Property 2: All distances are non-negative
    assert all(d >= 0 for d in distances.values())

    # Property 3: Triangle inequality holds
    for u in graph.nodes:
        for v in graph.neighbors(u):
            edge_weight = graph.get_edge_weight(u, v)
            assert distances[v] <= distances[u] + edge_weight + 1e-10  # Float precision
```

#### Algorithm Correctness Tests

```python
def test_dijkstra_known_graph():
    """Test Dijkstra on graph with known shortest paths."""
    graph = Graph()

    # Create test graph with known shortest paths
    #   A --2-- B
    #   |       |
    #   3       1
    #   |       |
    #   C --4-- D
    edges = [("A", "B", 2), ("A", "C", 3), ("B", "D", 1), ("C", "D", 4)]
    for u, v, w in edges:
        graph.add_edge(u, v, weight=w)

    result = dijkstra(graph, source="A")
    distances = result.result["distances"]

    expected = {"A": 0, "B": 2, "C": 3, "D": 3}
    assert distances == expected

def test_dijkstra_path_reconstruction():
    """Test that reconstructed paths are correct."""
    graph = create_test_graph()
    result = dijkstra(graph, source="A", target="D")

    path = result.result["path"]
    distance = result.result["distance"]

    # Verify path exists and has correct length
    assert len(path) >= 2
    assert path[0] == "A"
    assert path[-1] == "D"

    # Verify path distance matches computed distance
    path_distance = sum(
        graph.get_edge_weight(path[i], path[i+1])
        for i in range(len(path) - 1)
    )
    assert abs(path_distance - distance) < 1e-10
```

#### Performance Tests

```python
@pytest.mark.performance
def test_algorithm_performance():
    """Test algorithm performance on different graph sizes."""
    sizes = [100, 500, 1000, 5000]
    results = {}

    for size in sizes:
        graph = random_graph(size, edge_probability=0.1, weighted=True)

        with benchmark_algorithm(f"Dijkstra-{size}") as benchmark:
            result = dijkstra(graph, source=list(graph.nodes)[0])

        results[size] = {
            "time": benchmark.execution_time,
            "memory": benchmark.memory_usage,
            "nodes": len(graph.nodes),
            "edges": len(graph.edges)
        }

    # Verify performance scales reasonably
    for i in range(1, len(sizes)):
        prev_time = results[sizes[i-1]]["time"]
        curr_time = results[sizes[i]]["time"]
        size_ratio = sizes[i] / sizes[i-1]

        # Time should not increase more than O(n log n)
        assert curr_time <= prev_time * size_ratio * math.log(size_ratio) * 2
```

### Test Organization

```
tests/
├── conftest.py                      # Shared fixtures
├── unit/
│   ├── test_graph_core.py          # Core graph data structure tests
│   ├── test_algorithms/
│   │   ├── test_shortest_path.py   # Path algorithm tests
│   │   ├── test_centrality.py      # Centrality algorithm tests
│   │   └── test_clustering.py      # Clustering algorithm tests
│   └── test_models/
│       └── test_graph_models.py    # Pydantic model tests
├── integration/
│   ├── test_algorithm_integration.py # Cross-algorithm tests
│   └── test_core_integration.py    # Integration with ooai-core
├── performance/
│   ├── test_benchmarks.py          # Performance benchmarks
│   └── test_memory_usage.py        # Memory usage tests
└── fixtures/
    ├── graph_fixtures.py           # Standard test graphs
    └── algorithm_fixtures.py       # Algorithm test data
```

---

## @pdm-workflows

### PDM Commands for Graph Development

#### Essential Commands

```bash
# Basic setup
pdm install -G :all              # Install all dependencies
pdm run python -c "import ooai.graph; print('✅ Graph package ready')"

# Testing
pdm run test                      # All tests
pdm run test-algorithms           # Algorithm tests
pdm run test-performance          # Performance benchmarks
pdm run test-unit                 # Unit tests only
pdm run test-integration          # Integration tests

# Development
pdm run lint                      # Code linting
pdm run format                    # Code formatting
pdm run type-check                # Type checking
pdm run coverage                  # Test coverage

# Algorithm development
pdm run benchmark                 # Run algorithm benchmarks
pdm run profile                   # Profile algorithm performance
pdm run validate-algorithms       # Validate algorithm correctness
```

#### Custom Scripts (in pyproject.toml)

```toml
[tool.pdm.scripts]
# Testing
test = "pytest"
test-algorithms = "pytest tests/unit/test_algorithms/ -v"
test-performance = "pytest tests/performance/ -v --durations=0"
test-unit = "pytest tests/unit/ -v"
test-integration = "pytest tests/integration/ -v"

# Algorithm development
benchmark = "python scripts/benchmark_algorithms.py"
profile = "python scripts/profile_algorithms.py"
validate-algorithms = "python scripts/validate_all_algorithms.py"

# Code quality
lint = "ruff check src/"
format = "ruff format src/"
type-check = "mypy src/"
coverage = "pytest --cov=src/ooai/graph --cov-report=html"

# Visualization
plot-benchmarks = "python scripts/plot_performance.py"
generate-graphs = "python scripts/generate_test_graphs.py"
```

---

## @project-setup

### Environment Setup

```bash
# Clone and setup
cd /path/to/ooai/packages/ooai-graph
pdm install -G :all

# Verify installation
pdm run python -c "
from ooai.graph import Graph
from ooai.graph.algorithms.shortest_path import dijkstra
print('✅ OOAI Graph installation verified')
"

# Run basic example
pdm run python examples/basic_usage.py
```

### Development Dependencies

The package includes these dependency groups:

- **Core**: Basic graph functionality (pydantic, typing-extensions)
- **Algorithms**: Scientific computing (numpy, scipy)
- **Visualization**: Plotting libraries (matplotlib, networkx for layouts)
- **Development**: Testing and code quality tools
- **Performance**: Profiling and benchmarking tools

### Integration with ooai-core

```bash
# For cross-package development
cd ../ooai-core && pdm install -e . && cd ../ooai-graph
pdm install -e .

# Test integration
pdm run python -c "
from ooai.core.models import DynamicBaseModel
from ooai.graph.models import GraphModel
print('✅ Cross-package integration working')
"
```

---

## @development-workflow

### Git Workflow for Graph Development

```bash
# Branch naming conventions
feature/graph-dijkstra-implementation
feature/graph-pagerank-algorithm
feature/graph-visualization-tools
fix/graph-memory-leak-large-graphs
perf/graph-dijkstra-optimization
docs/graph-algorithm-documentation

# Commit conventions
feat(algorithms): implement Dijkstra shortest path algorithm
feat(centrality): add PageRank centrality measure
fix(memory): resolve memory leak in large graph processing
perf(dijkstra): optimize priority queue operations
test(algorithms): add comprehensive shortest path tests
docs(algorithms): add algorithm complexity documentation
```

### Algorithm Development Workflow

```bash
# 1. Design phase
# Create algorithm specification document
# Define time/space complexity requirements
# Plan test cases and benchmarks

# 2. Implementation
pdm run test-algorithms --lf        # Run last failed tests
pdm run lint                        # Check code quality
pdm run type-check                  # Verify types

# 3. Testing
pdm run test-algorithms -v          # Test new algorithms
pdm run test-performance            # Performance regression tests
pdm run validate-algorithms         # Correctness validation

# 4. Benchmarking
pdm run benchmark                   # Run performance benchmarks
pdm run profile                     # Profile for optimization opportunities

# 5. Documentation
# Update algorithm documentation
# Add usage examples
# Document complexity analysis

# 6. Integration testing
pdm run test-integration            # Cross-package integration
```

---

## @integration-patterns

### Integration with ooai-core

#### Dynamic Model Integration

```python
from ooai.core.models import DynamicBaseModel, compose_models
from ooai.graph.models import GraphModel
from ooai.graph.algorithms.centrality import pagerank

# Create dynamic graph models
class BaseGraphNode(DynamicBaseModel):
    id: str
    data: Dict[str, Any]

class CentralityMixin(DynamicBaseModel):
    centrality_score: Optional[float] = None

# Compose models dynamically
NodeWithCentrality = compose_models(BaseGraphNode, CentralityMixin)

# Use in graph algorithms
def compute_and_store_centrality(graph: Graph) -> Graph:
    """Compute centrality and store in node models."""
    scores = pagerank(graph).result

    for node_id in graph.nodes:
        node_data = graph.get_node_data(node_id)
        if isinstance(node_data, BaseGraphNode):
            # Dynamically add centrality to node
            enhanced_node = NodeWithCentrality(**node_data.model_dump())
            enhanced_node.centrality_score = scores[node_id]
            graph.set_node_data(node_id, enhanced_node)

    return graph
```

#### Engine Integration

```python
from ooai.core.engine.base import BaseEngine
from ooai.graph.algorithms import shortest_path, centrality

class GraphAnalysisEngine(BaseEngine):
    """Engine for graph analysis workflows."""

    def _process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        graph = input_data["graph"]
        analysis_type = input_data.get("analysis_type", "centrality")

        if analysis_type == "shortest_path":
            result = shortest_path.dijkstra(
                graph,
                source=input_data["source"],
                target=input_data.get("target")
            )
        elif analysis_type == "centrality":
            result = centrality.pagerank(graph)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")

        return {
            "algorithm": result.algorithm,
            "result": result.result,
            "graph_info": result.graph_info,
            "computation_time": result.computation_time
        }
```

---

## @session-logs

### Development History

#### [2025-10-15] OOAI Graph Package Initialization

**Objective**: Set up comprehensive Claude instructions for graph package

**Implementation**:
1. Created package-specific CLAUDE.md with graph focus
2. Defined algorithm implementation patterns and standards
3. Established testing framework for graph algorithms
4. Set up performance benchmarking infrastructure
5. Documented integration patterns with ooai-core

**Architecture Decisions**:
- **Algorithm Pattern**: Standardized input/output format for all algorithms
- **Performance Focus**: Built-in benchmarking and profiling capabilities
- **Modular Design**: Separate modules for algorithms, data structures, visualization
- **Integration Ready**: Designed for seamless ooai-core integration

**Next Steps**:
- Implement core graph data structure
- Add basic algorithms (Dijkstra, BFS, DFS)
- Set up visualization framework
- Create integration examples with ooai-core

---

## @research-notes

### Algorithm Research and Implementation Notes

#### Graph Representation Trade-offs

**Adjacency List** (Default choice):
- **Best for**: Sparse graphs (E << V²)
- **Memory**: O(V + E)
- **Edge query**: O(degree(v))
- **Iteration**: O(V + E)

**Adjacency Matrix**:
- **Best for**: Dense graphs, frequent edge queries
- **Memory**: O(V²)
- **Edge query**: O(1)
- **Iteration**: O(V²)

**Compressed Sparse Row (CSR)**:
- **Best for**: Large sparse graphs, algorithm implementation
- **Memory**: O(V + E)
- **Cache efficiency**: Excellent for iteration
- **Mutability**: Read-only after construction

#### Algorithm Selection Research

**Shortest Path Algorithm Selection**:
- **Small graphs (V < 1000)**: Dijkstra with binary heap
- **Medium graphs (V < 10000)**: Dijkstra with Fibonacci heap
- **Large graphs (V > 10000)**: Bidirectional Dijkstra or A* with good heuristic
- **Dense graphs**: Consider Floyd-Warshall for all-pairs

**Centrality Algorithm Selection**:
- **Small graphs (V < 5000)**: Exact algorithms
- **Large graphs (V > 5000)**: Approximation algorithms
- **Dynamic graphs**: Incremental algorithms

---

## @troubleshooting

### Common Graph Algorithm Issues

#### Memory Issues

**Problem**: Out of memory with large graphs
**Solutions**:
```python
# 1. Use memory-efficient representation
graph = Graph(representation="csr")

# 2. Process in chunks
def process_large_graph_in_chunks(graph: Graph, chunk_size: int = 10000):
    nodes = list(graph.nodes)
    for i in range(0, len(nodes), chunk_size):
        chunk_nodes = nodes[i:i + chunk_size]
        subgraph = graph.subgraph(chunk_nodes)
        yield process_subgraph(subgraph)

# 3. Use generators for large result sets
def large_shortest_paths(graph: Graph, sources: List[str]):
    for source in sources:
        yield dijkstra(graph, source=source)
```

#### Performance Issues

**Problem**: Algorithm running too slowly
**Diagnostics**:
```python
# Profile algorithm performance
import cProfile
import pstats

def profile_algorithm(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

    return result

# Usage
result = profile_algorithm(dijkstra, large_graph, source="A")
```

#### Algorithm Correctness Issues

**Problem**: Algorithm produces incorrect results
**Debugging approach**:
```python
def debug_dijkstra(graph: Graph, source: str, target: str):
    """Debug version of Dijkstra with detailed logging."""
    distances = {node: float('inf') for node in graph.nodes}
    distances[source] = 0
    visited = set()

    print(f"Starting Dijkstra from {source} to {target}")
    print(f"Initial distances: {distances}")

    while len(visited) < len(graph.nodes):
        # Find unvisited node with minimum distance
        current = min(
            (node for node in graph.nodes if node not in visited),
            key=lambda x: distances[x]
        )

        print(f"Visiting node: {current}, distance: {distances[current]}")
        visited.add(current)

        if current == target:
            print(f"Reached target {target} with distance {distances[current]}")
            break

        # Update distances to neighbors
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                edge_weight = graph.get_edge_weight(current, neighbor)
                new_distance = distances[current] + edge_weight

                if new_distance < distances[neighbor]:
                    print(f"Updating {neighbor}: {distances[neighbor]} -> {new_distance}")
                    distances[neighbor] = new_distance

    return distances[target] if target in distances else float('inf')
```

---

## @performance-benchmarks

### Algorithm Performance Data

#### Benchmark Results (Sample Data)

**Dijkstra's Algorithm Performance**:
| Graph Size | Edges | Time (ms) | Memory (MB) | Nodes/sec |
|------------|-------|-----------|-------------|-----------|
| 1,000 | 5,000 | 12.3 | 2.1 | 81,300 |
| 10,000 | 50,000 | 156.8 | 18.4 | 63,800 |
| 100,000 | 500,000 | 2,341.2 | 142.8 | 42,700 |

**Betweenness Centrality Performance**:
| Graph Size | Time (sec) | Memory (MB) | Complexity |
|------------|------------|-------------|------------|
| 1,000 | 2.4 | 15.6 | O(V³) |
| 5,000 | 58.9 | 156.2 | O(V³) |
| 10,000 | 245.7 | 589.4 | O(V³) |

### Performance Testing Framework

```python
import time
import psutil
import matplotlib.pyplot as plt
from typing import List, Callable

class PerformanceTester:
    """Framework for systematic algorithm performance testing."""

    def __init__(self):
        self.results = {}

    def benchmark_algorithm(
        self,
        algorithm: Callable,
        graph_sizes: List[int],
        graph_generator: Callable,
        **kwargs
    ):
        """Benchmark algorithm across different graph sizes."""
        results = []

        for size in graph_sizes:
            graph = graph_generator(size, **kwargs)

            # Warm up
            algorithm(graph)

            # Actual benchmark
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss

            result = algorithm(graph)

            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss

            results.append({
                'size': size,
                'time': end_time - start_time,
                'memory': (end_memory - start_memory) / 1024 / 1024,  # MB
                'nodes_per_sec': size / (end_time - start_time)
            })

        return results

    def plot_performance(self, results: List[dict], title: str):
        """Plot performance results."""
        sizes = [r['size'] for r in results]
        times = [r['time'] for r in results]

        plt.figure(figsize=(10, 6))
        plt.loglog(sizes, times, 'o-')
        plt.xlabel('Graph Size (nodes)')
        plt.ylabel('Execution Time (seconds)')
        plt.title(f'{title} - Performance Scaling')
        plt.grid(True)
        plt.show()
```

---

## @visualization

### Graph Visualization Framework

#### Basic Plotting

```python
from ooai.graph.visualization import plot_graph, interactive_plot

# Basic graph plotting
plot_graph(
    graph,
    layout="spring",  # spring, circular, hierarchical
    node_color="centrality",
    edge_width="weight",
    save_path="graph.png"
)

# Interactive visualization
interactive_plot(
    graph,
    highlight_paths=["A", "B", "C"],
    show_weights=True,
    allow_node_dragging=True
)
```

#### Algorithm Visualization

```python
from ooai.graph.visualization import animate_algorithm

# Animate Dijkstra's algorithm
animate_algorithm(
    algorithm="dijkstra",
    graph=graph,
    source="A",
    target="B",
    speed=1.0,  # Animation speed
    save_animation="dijkstra.gif"
)

# Visualize centrality scores
plot_centrality(
    graph,
    centrality_scores=pagerank_scores,
    color_scheme="viridis",
    node_size_scale=100
)
```

---

_Last Updated: 2025-10-15 - Complete graph package documentation_
_Documentation Version: 1.0 (Graph Package Specific)_