"""
This module contains utility function for interaction with EbdGraphs and its DiGraph.
Some of these functions may store some information in the "attribute dictionaries" of the DiGraph nodes
(for later use in the conversion logic).
"""
from typing import List, Optional, Set, Tuple, Type

from networkx import DiGraph, all_simple_paths  # type:ignore[import]

from ebdtable2graph.models import DecisionNode, EbdGraphNode, EndNode, OutcomeNode, ToNoEdge, ToYesEdge


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
    We need to know that to construct the plantuml code correctly. The node will be placed right after the plantuml code
    of the last common node.

    Implementation details:
    In general the plantuml code is nested as a bunch of if-else branches. These if-else branches are equivalent to
    decision nodes.
    But if you place something after an if-else, both branches (of the if and the else case) will be merged and
    connected to the stuff after this if-else. We call this stuff the "appendix" of that if-else branch aka decision
    node. If we want to cut a branch e.g. on an OutcomeNode, we will use the `kill` statement.

    To achieve the desired result we have to place the nodes with indegree > 1 (i.e. targeted by more than one edge)
    below the code of the last common ancestor.
    """
    for node in graph:
        in_degree: int = graph.in_degree(node)
        if in_degree <= 1:
            continue
        paths = list(all_simple_paths(graph, source="Start", target=node))
        assert len(paths) > 1, "If indegree > 1, the number of paths should always be greater than 1 too."
        common_ancestor = _find_last_common_ancestor(paths)
        assert common_ancestor != "Start", "Last common ancestor should always be at least the first decision node '1'."
        # Annotate the common ancestor for later plantuml conversion
        graph.nodes[common_ancestor]["append_node"] = node
        for path in paths:
            graph.nodes[path[-2]]["skip_node"] = node


def _appendix_choice_for_nodes(graph: DiGraph, node1: EbdGraphNode, node2: EbdGraphNode) -> Optional[DecisionNode]:
    """
    This function decides if the two following nodes of a decision node should be drawn top to bottom instead of next
    to each other.

    This function returns the node to be sent to appendix or None (if the nodes should be drawn next to each other).
    See `_mark_skips_to_appendix` below for more details.
    """
    match [node1, node2]:
        case [DecisionNode() as dec_node, OutcomeNode() | EndNode() as out_node] | [
            OutcomeNode() | EndNode() as out_node,
            DecisionNode() as dec_node,
        ] if graph.in_degree(
            str(out_node)  # pylint: disable=used-before-assignment
        ) == 1:
            # pylint doesn't seem to work well with structural pattern matching.
            return dec_node

    return None


def _mark_skips_to_appendix(graph: DiGraph) -> None:
    """
    This is a little function to improve the layout of the graph. For this, we want to draw decision nodes with an
    outcome node on the one hand and a decision node on the other hand from top to bottom (to avoid hilariously broad
    plots). See E_0015 for a good example.
    This function sets for the respective decision nodes the attributes `skip_node` and `append_node`.

    Implementation details:
    In general nested structures are drawn next to each other. As a workaround, we draw the decision node (if the other
    one is an OutcomeNode or an EndNode) below the other. To achieve this, we omit the whole part of the decision node
    and instead place it after the whole branch. This will create our desired result.

    Therefore, if a (decision) node is chosen to be drawn under the rest it will be sent to "appendix".
    I.e. the node gets its following node as entry in `append_node` (to place below it) and `skip_node` attribute
    (to omit the code inside the branch).
    """
    for node in graph:
        if not isinstance(graph.nodes[node]["node"], DecisionNode):
            continue
        node_to_appendix: Optional[DecisionNode] = _appendix_choice_for_nodes(
            graph, *[graph.nodes[neighbor]["node"] for neighbor in graph[node]]
        )
        if node_to_appendix is not None:
            if "append_node" in graph.nodes[node]:
                assert (
                    str(node_to_appendix) == graph.nodes[node]["append_node"]
                ), "Cannot push more than one different node to appendix"
            graph.nodes[node]["skip_node"] = str(node_to_appendix)
            graph.nodes[node]["append_node"] = str(node_to_appendix)


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


def _decision_node_splits_to(graph: DiGraph, node: str) -> Set[Type[EbdGraphNode]]:
    if not isinstance(graph.nodes[node]["node"], DecisionNode):
        raise ValueError(f"Provided node '{node}' is not a DecisionNode.")

    neighbor_types = {type(graph.nodes[neighbor]["node"]) for neighbor in graph[node]}
    assert len(neighbor_types) == 2
    return neighbor_types
