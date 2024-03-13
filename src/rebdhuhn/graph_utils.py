"""
This module contains utility function for interaction with EbdGraphs and its DiGraph.
Some of these functions may store some information in the "attribute dictionaries" of the DiGraph nodes
(for later use in the conversion logic).
"""

from typing import List, Tuple

from networkx import DiGraph, all_simple_paths  # type:ignore[import]

from rebdhuhn.models import ToNoEdge, ToYesEdge
from rebdhuhn.models.errors import PathsNotGreaterThanOneError

COMMON_ANCESTOR_FIELD = "common_ancestor_for_node"
# Defines the label to annotate the last common ancestor node with the information to which node


def _find_last_common_ancestor(paths: List[List[str]]) -> str:
    """
    This function calculates the last common ancestor node for the defined paths (these paths should be all paths
    between two nodes in the graph).
    For this, we assume that the graph contains no loops.
    Returns the key of the (common ancestor) node.
    """
    paths = paths.copy()
    reference_path = paths.pop().copy()  # it's arbitrary which of the paths is the chosen one
    reference_path.pop()  # The last entry in a path is always the target node in which we are not interested
    for node in reversed(reference_path):
        if all(node in path for path in paths):  # If node is present in all paths aka is a common ancestor node
            return node
    raise ValueError("No common ancestor found.")


def _mark_last_common_ancestors(graph: DiGraph) -> None:
    """
    Marks the last common ancestor node for each node with an indegree > 1. An indegree is the number of edges pointing
    towards the respective node.
    I.e. if a node is the target of more than one `YesNoEdge`, we want to find the last common node from each possible
    path from the start node to the respective node.
    Each node which is such an ancestor will contain the information of which nodes it is the last common ancestor.
    It is stored in the dict field `COMMON_ANCESTOR_FIELD` as a list.
    """
    for node in graph:
        in_degree: int = graph.in_degree(node)
        if in_degree <= 1:
            continue
        paths = list(all_simple_paths(graph, source="Start", target=node))
        if len(paths) <= 1:
            raise PathsNotGreaterThanOneError(
                node_key=node,
                indegree=in_degree,
                number_of_paths=len(paths),
            )
        common_ancestor = _find_last_common_ancestor(paths)
        assert common_ancestor != "Start", "Last common ancestor should always be at least the first decision node '1'."
        # Annotate the common ancestor for later conversion
        if COMMON_ANCESTOR_FIELD not in graph.nodes[common_ancestor]:
            graph.nodes[common_ancestor][COMMON_ANCESTOR_FIELD] = [node]
        else:
            assert isinstance(graph.nodes[common_ancestor][COMMON_ANCESTOR_FIELD], list), "Wrong type"
            graph.nodes[common_ancestor][COMMON_ANCESTOR_FIELD].append(node)


def _get_yes_no_edges(graph: DiGraph, node: str) -> Tuple[ToYesEdge, ToNoEdge]:
    """
    A shorthand to get the yes-edge and the no-edge of a decision node.
    """
    yes_edge: ToYesEdge
    no_edge: ToNoEdge
    for edge in graph[node].values():
        edge = edge["edge"]
        match edge:
            case ToYesEdge():
                assert "yes_edge" not in locals(), f"Multiple yes edges found for node {node}"
                yes_edge = edge
            case ToNoEdge():
                assert "no_edge" not in locals(), f"Multiple no edges found for node {node}"
                no_edge = edge
            case _:
                assert False, f"Unknown edge type: {edge}"
    assert "yes_edge" in locals(), f"No yes edge found for node {node}"
    assert "no_edge" in locals(), f"No no edge found for node {node}"
    return yes_edge, no_edge
