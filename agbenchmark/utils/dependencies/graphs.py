import math

import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from pathlib import Path

from agbenchmark.start_benchmark import REPORTS_PATH


def tree_layout(graph, root_node):
    """Compute positions as a tree layout centered on the root with alternating vertical shifts."""
    bfs_tree = nx.bfs_tree(graph, source=root_node)
    levels = {
        node: depth
        for node, depth in nx.single_source_shortest_path_length(
            bfs_tree, root_node
        ).items()
    }

    pos = {}
    max_depth = max(levels.values())
    level_positions = {i: 0 for i in range(max_depth + 1)}  # type: ignore

    # Count the number of nodes per level to compute the width
    level_count = {}
    for node, level in levels.items():
        level_count[level] = level_count.get(level, 0) + 1

    vertical_offset = (
        0.05  # The amount of vertical shift per node within the same level
    )

    # Assign positions
    for node, level in sorted(levels.items(), key=lambda x: x[1]):
        total_nodes_in_level = level_count[level]
        horizontal_spacing = 1.0 / (total_nodes_in_level + 1)
        pos_x = (
            0.5
            - (total_nodes_in_level - 1) * horizontal_spacing / 2
            + level_positions[level] * horizontal_spacing
        )

        # Alternately shift nodes up and down within the same level
        pos_y = (
            -level
            + (level_positions[level] % 2) * vertical_offset
            - ((level_positions[level] + 1) % 2) * vertical_offset
        )
        pos[node] = (pos_x, pos_y)

        level_positions[level] += 1

    return pos


def graph_spring_layout(dag, labels, tree: bool = True):  # Default to spring layout
    num_nodes = len(dag.nodes())
    # Visualize the graph
    plt.figure()

    base = 3

    if num_nodes > 10:
        base /= 1 + math.log(num_nodes)
        font_size = base * 10

    font_size = max(10, base * 10)
    node_size = max(300, base * 1000)

    if tree:
        root_node = [node for node, degree in dag.in_degree() if degree == 0][0]
        pos = tree_layout(dag, root_node)
    else:
        # Adjust k for the spring layout based on node count
        k_value = 3 / math.sqrt(num_nodes)

        pos = nx.spring_layout(dag, k=k_value, iterations=50)

    nx.draw(
        dag,
        pos,
        labels=labels,
        with_labels=True,
        node_size=node_size,
        node_color="skyblue",
        font_size=font_size,
        width=base,
        edge_color="gray",
    )
    plt.title("Dependency Graph")
    plt.show()


def graph_interactive_network(dag, labels, show=False):
    nt = Network(notebook=True, width="100%", height="800px", directed=True)

    print("labels", labels)
    # Add nodes and edges to the pyvis network
    for node, label in labels.items():
        node_id_str = node.nodeid
        nt.add_node(node_id_str, label=label)

    # Add edges to the pyvis network
    for edge in dag.edges():
        source_id_str = edge[0].nodeid
        target_id_str = edge[1].nodeid
        if not (source_id_str in nt.get_nodes() and target_id_str in nt.get_nodes()):
            print(
                f"Skipping edge {source_id_str} -> {target_id_str} due to missing nodes."
            )
            continue
        nt.add_edge(source_id_str, target_id_str)

    file_path = str(Path(REPORTS_PATH) / "dependencies.html")

    if show:
        nt.show(file_path, notebook=False)
    nt.write_html(file_path)
