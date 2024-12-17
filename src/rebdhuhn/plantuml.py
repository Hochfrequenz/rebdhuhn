"""
This module contains logic to convert EbdGraph data to plantuml code and further to parse this code to SVG images.
"""

from collections import namedtuple

from networkx import DiGraph  # type:ignore[import-untyped]

from rebdhuhn.graph_utils import COMMON_ANCESTOR_FIELD, _get_yes_no_edges, _mark_last_common_ancestors
from rebdhuhn.kroki import PlantUmlToSvgConverter
from rebdhuhn.models import DecisionNode, EbdGraph, EndNode, OutcomeNode
from rebdhuhn.models.errors import GraphTooComplexForPlantumlError, NotExactlyTwoOutgoingEdgesError

ADD_INDENT = "    "  #: This is just for style purposes to make the plantuml files human-readable.


def _escape_for_plantuml(input_str: str) -> str:
    """
    Plantuml sometimes has problems with the character ')'. Therefore, we escape it with the respective HTML code since
    Plantuml supports HTML.
    """
    return input_str.replace(")", "&#41;")


def _draw_node1_below_node2(graph: DiGraph, node1: str, node2: str) -> bool:
    """
    Used in `_convert_decision_node_to_plantuml`. Decides if `node1` should be drawn under `node2`.
    This is the case if `node1` is a `DecisionNode` and `node2` is either an `OutcomeNode` or an `EndNode`
    with indegree == 1.
    This kind of workaround is used just for layout purposes.
    """
    return (
        isinstance(graph.nodes[node1]["node"], DecisionNode)
        and isinstance(graph.nodes[node2]["node"], (OutcomeNode, EndNode))
        and graph.in_degree(node2) == 1
    )


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
    is_outcome_without_code = outcome_node.result_code is None
    if is_outcome_without_code:
        return f"{indent}:{outcome_node.note};\n{indent}kill;\n"
    result = f"{indent}:{outcome_node.result_code};\n"
    if outcome_node.note is not None:
        note = outcome_node.note.replace("\n", f"\n{indent}{ADD_INDENT}")
        result += f"{indent}note left\n" f"{indent}{ADD_INDENT}{_escape_for_plantuml(note)}\n" f"{indent}endnote\n"
    return f"{result}{indent}kill;\n"


def _convert_decision_node_to_plantuml(graph: DiGraph, node: str, indent: str) -> str:
    """
    Converts a DecisionNode to plantuml code.
    DecisionNodes will be converted to a nested if-else structure with the if-branch as the yes-edge and the else-branch
    as the no-edge. Those branches will contain the code of the following nodes recursively. This creates the nested
    structure.
    But there are some exceptions. E.g. if a (following) node is the target of more than one edge (i.e. indegree > 1)
    this node has to be placed under the last common ancestor to properly create the "merge nodes".
    Additionally, the same technique will be used to simply draw DecisionNodes below OutcomeNodes since OutcomeNodes
    doesn't have any following nodes. This will improve the layout drastically for EBDs like E_0015.
    """
    decision_node: DecisionNode = graph.nodes[node]["node"]
    assert isinstance(decision_node, DecisionNode), f"{node} is not a decision node."
    if graph.out_degree(node) != 2:
        raise NotExactlyTwoOutgoingEdgesError(
            f"A decision node must have exactly two outgoing edges (yes / no) but has {graph.out_degree(node)}",
            str(decision_node),
            [str(x) for x in graph[node].values()],
        )
    yes_edge, no_edge = _get_yes_no_edges(graph, node)
    yes_node = str(yes_edge.target)
    no_node = str(no_edge.target)

    Cases = namedtuple("Cases", "yes_below_no no_below_yes common_ancestor")
    cases = Cases(
        _draw_node1_below_node2(graph, yes_node, no_node),
        _draw_node1_below_node2(graph, no_node, yes_node),
        COMMON_ANCESTOR_FIELD in graph.nodes[node],
    )
    assert cases.count(True) <= 1, "This cannot actually fail."

    result = (
        f"{indent}if (<b>{decision_node.step_number}: </b> {_escape_for_plantuml(decision_node.question)}) then (ja)\n"
    )
    if not cases.yes_below_no and not graph.in_degree(yes_node) > 1:
        # Draw the following node here only if it shouldn't be drawn under the no-branch and if it isn't a node with
        # indegree > 1.
        result += _convert_node_to_plantuml(graph, yes_node, indent + ADD_INDENT)
    result += f"{indent}else (nein)\n"
    if not cases.no_below_yes and not graph.in_degree(no_node) > 1:
        # Draw the following node here only if it shouldn't be drawn under the yes-branch and if it isn't a node with
        # indegree > 1.
        result += _convert_node_to_plantuml(graph, no_node, indent + ADD_INDENT)
    result += f"{indent}endif\n"

    # Appendix part
    if cases.yes_below_no:
        result += _convert_decision_node_to_plantuml(graph, yes_node, indent)
    elif cases.no_below_yes:
        result += _convert_decision_node_to_plantuml(graph, no_node, indent)
    elif cases.common_ancestor:
        if len(graph.nodes[node][COMMON_ANCESTOR_FIELD]) != 1:
            # This is not supported by the plantuml converter. However, if you remove this raise statement, the
            # converter may work even may produce valid puml. The last time I tried this resulted in copied regions
            # inside the graph. So, really complex graphs would get insanely big.
            raise GraphTooComplexForPlantumlError
        result += _convert_node_to_plantuml(graph, graph.nodes[node][COMMON_ANCESTOR_FIELD][0], indent)
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
        f"{graph.metadata.section}\n"
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
    key_of_first_node: str
    if "1" in nx_graph["Start"]:
        key_of_first_node = "1"
    else:
        key_of_first_node = list(nx_graph["Start"].keys())[0]
    plantuml_code += _convert_node_to_plantuml(nx_graph, key_of_first_node, "")

    return plantuml_code + "\n@enduml\n"


def convert_plantuml_to_svg_kroki(plantuml_code: str, converter: PlantUmlToSvgConverter) -> str:
    """
    Converts plantuml code to svg code using kroki
    """
    return converter.convert_plantuml_to_svg(plantuml_code)
