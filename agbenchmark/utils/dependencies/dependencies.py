from typing import Any


def topo_sort(graph: dict[str, Any]) -> list[str]:
    visited = set()
    stack = []
    # if it's a dummy dependency setup test, we also skip
    # if "test_method" not in item.name:
    #     continue

    for node in graph:
        if node not in visited:
            visited.add(node)
            dfs(graph, node, visited, stack)
    stack.reverse()
    return stack


def dfs(graph: dict[str, Any], node: Any, visited: set, stack: list[str]) -> None:
    for neighbour in graph.get(node, []):
        if neighbour not in visited:
            visited.add(neighbour)
            dfs(graph, neighbour, visited, stack)
    stack.append(node)
