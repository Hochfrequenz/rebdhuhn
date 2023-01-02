import re
from typing import List

import requests
from networkx import DiGraph

from ebdtable2graph.graph_utils import _mark_last_common_ancestors
from ebdtable2graph.models import (
    DecisionNode,
    EbdGraph,
    EbdGraphEdge,
    EndNode,
    OutcomeNode,
    StartNode,
    ToNoEdge,
    ToYesEdge,
)

ADD_INDENT = "    "  #: This is just for style purposes to make the plantuml files human-readable.


def _format_label(label: str) -> str:
    escaped_str = re.sub(r"^(\d+): ", r"<B>\1: </B>", label)
    escaped_str = escaped_str.replace("\n", '<BR align="left"/>')
    return f'<{escaped_str}<BR align="left"/>>'


def _convert_start_node_to_dot(graph: DiGraph, node: str, indent: str) -> str:
    return f'{indent}"{node}" [shape=box, style=rounded, label="Start"];'


def _convert_end_node_to_dot(graph: DiGraph, node: str, indent: str) -> str:
    return f'{indent}"{node}" [shape=box, style=rounded, label="Ende"];'


def _convert_outcome_node_to_dot(graph: DiGraph, node: str, indent: str) -> str:
    return f'{indent}"{node}" [shape=box, style="filled", fillcolor="red", label={_format_label(graph.nodes[node]["node"].result_code)}];'


def _convert_decision_node_to_dot(graph: DiGraph, node: str, indent: str) -> str:
    formatted_label = _format_label(f'{node}: {graph.nodes[node]["node"].question}')
    return f'{indent}"{node}" [shape=box, style="filled", fillcolor="green", label={formatted_label}];'


def _convert_node_to_dot(graph: DiGraph, node: str, indent: str) -> str:
    """
    A shorthand to convert an arbitrary node to dot code. It just determines the node type and calls the
    respective function.
    """
    match graph.nodes[node]["node"]:
        case DecisionNode():
            return _convert_decision_node_to_dot(graph, node, indent)
        case OutcomeNode():
            return _convert_outcome_node_to_dot(graph, node, indent)
        case EndNode():
            return _convert_end_node_to_dot(graph, node, indent)
        case StartNode():
            return _convert_start_node_to_dot(graph, node, indent)
        case _:
            raise ValueError(f"Unknown node type: {graph.nodes[node]['node']}")


def _convert_nodes_to_dot(graph: DiGraph, indent: str) -> List[str]:
    return [_convert_node_to_dot(graph, node, indent) for node in graph.nodes]


def _convert_yes_edge_to_dot(graph: DiGraph, node_src: str, node_target: str, indent: str) -> str:
    return f'{indent}"{node_src}" -> "{node_target}" [label="Ja"];'


def _convert_no_edge_to_dot(graph: DiGraph, node_src: str, node_target: str, indent: str) -> str:
    return f'{indent}"{node_src}" -> "{node_target}" [label="Nein"];'


def _convert_ebd_graph_edge_to_dot(graph: DiGraph, node_src: str, node_target: str, indent: str) -> str:
    return f'{indent}"{node_src}" -> "{node_target}";'


def _convert_edge_to_dot(graph: DiGraph, node_src: str, node_target: str, indent: str) -> str:
    """
    A shorthand to convert an arbitrary node to dot code. It just determines the node type and calls the
    respective function.
    """
    match graph[node_src][node_target]["edge"]:
        case ToYesEdge():
            return _convert_yes_edge_to_dot(graph, node_src, node_target, indent)
        case ToNoEdge():
            return _convert_no_edge_to_dot(graph, node_src, node_target, indent)
        case EbdGraphEdge():
            return _convert_ebd_graph_edge_to_dot(graph, node_src, node_target, indent)
        case _:
            raise ValueError(f"Unknown edge type: {graph[node_src][node_target]['edge']}")


def _convert_edges_to_dot(graph: DiGraph, indent: str) -> List[str]:
    return [_convert_edge_to_dot(graph, edge[0], edge[1], indent) for edge in graph.edges]


def convert_graph_to_dot(graph: EbdGraph) -> str:
    nx_graph = graph.graph
    _mark_last_common_ancestors(nx_graph)
    dot_code = "digraph D {\n"
    assert len(nx_graph["Start"]) == 1, "Start node must have exactly one outgoing edge."
    assert "1" in nx_graph["Start"], "Start node must be connected to decision node '1'."
    dot_code += "\n".join(_convert_nodes_to_dot(nx_graph, ADD_INDENT)) + "\n\n"
    dot_code += "\n".join(_convert_edges_to_dot(nx_graph, ADD_INDENT)) + "\n"

    return dot_code + "}"


def convert_dot_to_svg_kroki(dot_code: str) -> str:
    """
    Converts dot code to svg (code) and returns the result as string. It uses kroki.io.
    """
    url = "https://kroki.io"
    answer = requests.post(
        url,
        json={"diagram_source": dot_code, "diagram_type": "graphviz", "output_format": "svg"},
        timeout=5,
    )
    if answer.status_code != 200:
        raise ValueError(
            f"Error while converting dot to svg: {answer.status_code}: {requests.codes[answer.status_code]}. "
            f"{answer.text}"
        )
    return answer.text
