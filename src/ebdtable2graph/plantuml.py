"""
This module contains logic to convert EbdGraph data to plantuml code and further to parse this code to SVG images.
"""
import requests  # pylint: disable=import-error
from networkx import DiGraph  # type:ignore[import]

from ebdtable2graph.graph_utils import _get_yes_no_edges, _mark_last_common_ancestors, _mark_skips_to_appendix
from ebdtable2graph.models import DecisionNode, EbdGraph, EndNode, OutcomeNode

ADD_INDENT = "    "  #: This is just for style purposes to make the plantuml files human-readable.


def _escape_for_plantuml(input_str: str) -> str:
    """
    Plantuml has sometimes problems with the character ')'. Therefore, we escape it with the respective HTML code since
    Plantuml supports HTML.
    """
    return input_str.replace(")", "&#41;")


def _convert_end_node_to_plantuml(graph: DiGraph, node: str, indent: str) -> str:
    """
    Converts an EndNode to plantuml code.
    """
    end_node: EndNode = graph.nodes[node]["node"]
    assert isinstance(end_node, EndNode), f"{node} is not an end node."

    return f"{indent}end\n"


def _convert_outcome_node_to_plantuml(graph: DiGraph, node: str, indent: str) -> str:
    """
    Converts an OutcomeNode to plantuml code.
    """
    outcome_node: OutcomeNode = graph.nodes[node]["node"]
    assert isinstance(outcome_node, OutcomeNode), f"{node} is not an outcome node."

    result = f"{indent}:{outcome_node.result_code};\n"
    if outcome_node.note is not None:
        note = outcome_node.note.replace("\n", f"\n{indent}{ADD_INDENT}")
        result += f"{indent}note left\n" f"{indent}{ADD_INDENT}{_escape_for_plantuml(note)}\n" f"{indent}endnote\n"
    return f"{result}{indent}kill;\n"


def _convert_decision_node_to_plantuml(graph: DiGraph, node: str, indent: str) -> str:
    """
    Converts a DecisionNode to plantuml code.
    """
    decision_node: DecisionNode = graph.nodes[node]["node"]
    assert isinstance(decision_node, DecisionNode), f"{node} is not a decision node."
    assert graph.out_degree(node) == 2, "A decision node must have exactly two outgoing edges (yes / no)."

    yes_edge, no_edge = _get_yes_no_edges(graph, node)
    yes_node = str(yes_edge.target)
    no_node = str(no_edge.target)

    result = (
        f"{indent}if (<b>{decision_node.step_number}: </b> {_escape_for_plantuml(decision_node.question)}) then (ja)\n"
    )
    if "skip_node" not in graph.nodes[node] or graph.nodes[node]["skip_node"] != yes_node:
        result += _convert_node_to_plantuml(graph, yes_node, indent + ADD_INDENT)
    result += f"{indent}else (nein)\n"
    if "skip_node" not in graph.nodes[node] or graph.nodes[node]["skip_node"] != no_node:
        result += _convert_node_to_plantuml(graph, no_node, indent + ADD_INDENT)
    result += f"{indent}endif\n"

    if "append_node" in graph.nodes[node]:
        result += _convert_node_to_plantuml(graph, str(graph.nodes[node]["append_node"]), indent)
    return result


def _convert_node_to_plantuml(graph: DiGraph, node: str, indent: str) -> str:
    """
    A shorthand to convert an arbitrary node to plantuml code. It just determines the node type and calls the
    respective function.
    """
    match graph.nodes[node]["node"]:
        case DecisionNode():
            return _convert_decision_node_to_plantuml(graph, node, indent)
        case OutcomeNode():
            return _convert_outcome_node_to_plantuml(graph, node, indent)
        case EndNode():
            return _convert_end_node_to_plantuml(graph, node, indent)
        case _:
            raise ValueError(f"Unknown node type: {graph[node]['node']}")


def convert_graph_to_plantuml(graph: EbdGraph) -> str:
    """
    Converts given graph to plantuml code and returns it as a string.
    """
    nx_graph = graph.graph
    _mark_last_common_ancestors(nx_graph)
    _mark_skips_to_appendix(nx_graph)
    plantuml_code: str = (
        "@startuml\n"
        "skinparam Shadowing false\n"
        "skinparam NoteBorderColor #f3f1f6\n"
        "skinparam NoteBackgroundColor #f3f1f6\n"
        "skinparam NoteFontSize 12\n"
        "skinparam ActivityBorderColor none\n"
        "skinparam ActivityBackgroundColor #7a8da1\n"
        "skinparam ActivityFontSize 16\n"
        "skinparam ArrowColor #7aab8a\n"
        "skinparam ArrowFontSize 16\n"
        "skinparam ActivityDiamondBackgroundColor #7aab8a\n"
        "skinparam ActivityDiamondBorderColor #7aab8a\n"
        "skinparam ActivityDiamondFontSize 18\n"
        "skinparam defaultFontName DejaVu Serif Condensed\n"
        "skinparam ActivityEndColor #669580\n"
        "\n"
        "header\n"
        "<b>FV2210\n"
        "2022-12-12\n"
        "endheader\n"
        "\n"
        "title\n"
        f"{graph.metadata.chapter}\n"
        "\n"
        f"{graph.metadata.sub_chapter}\n"
        "\n"
        "\n"
        "\n"
        "end title\n"
        f":<b>{graph.metadata.ebd_code}</b>;\n"
        "note right\n"
        f"<b><i>Prüfende Rolle: {graph.metadata.role}\n"
        "end note\n"
        "\n"
    )
    assert len(nx_graph["Start"]) == 1, "Start node must have exactly one outgoing edge."
    assert "1" in nx_graph["Start"], "Start node must be connected to decision node '1'."
    plantuml_code += _convert_node_to_plantuml(nx_graph, "1", "")

    return plantuml_code + "\n@enduml\n"


def convert_plantuml_to_svg_kroki(plantuml_code: str) -> str:
    """
    Converts plantuml code to svg (code) and returns the result as string. It uses kroki.io.
    """
    url = "https://kroki.io"
    answer = requests.post(
        url,
        json={"diagram_source": plantuml_code, "diagram_type": "plantuml", "output_format": "svg"},
        timeout=5,
    )
    if answer.status_code != 200:
        raise ValueError(
            f"Error while converting plantuml to svg: {answer.status_code}: {requests.codes[answer.status_code]}. "
            f"{answer.text}"
        )
    return answer.text
