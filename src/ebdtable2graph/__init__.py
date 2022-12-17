"""
contains the conversion logic
"""
from typing import Dict, Generator, List, Optional, Tuple

import requests  # pylint: disable=import-error
from networkx import DiGraph, all_simple_paths  # type:ignore[import]

from ebdtable2graph.models.ebd_graph import (
    DecisionNode,
    EbdGraph,
    EbdGraphEdge,
    EbdGraphMetaData,
    EbdGraphNode,
    EndNode,
    OutcomeNode,
    StartNode,
    ToNoEdge,
    ToYesEdge,
)
from ebdtable2graph.models.ebd_table import EbdTable, EbdTableRow, EbdTableSubRow


def _convert_sub_row_to_outcome_node(sub_row: EbdTableSubRow) -> Optional[OutcomeNode]:
    """
    converts a sub_row into an outcome node (or None if not applicable)
    """
    if sub_row.result_code is not None:
        return OutcomeNode(result_code=sub_row.result_code, note=sub_row.note)
    return None


def _convert_row_to_decision_node(row: EbdTableRow) -> DecisionNode:
    """
    converts a row into a decision node
    """
    return DecisionNode(step_number=row.step_number, question=row.description)


def _yes_no_edge(decision: bool, source: DecisionNode, target: EbdGraphNode) -> EbdGraphEdge:
    if decision:
        return ToYesEdge(source=source, target=target)
    return ToNoEdge(source=source, target=target)


def get_all_nodes(table: EbdTable) -> List[EbdGraphNode]:
    """
    Returns a list with all nodes from the table.
    Nodes may both be actual EBD check outcome codes (e.g. "A55") but also points where decisions are made.
    """
    result: List[EbdGraphNode] = [StartNode()]
    contains_ende = False
    for row in table.rows:
        decision_node = _convert_row_to_decision_node(row)
        result.append(decision_node)
        for sub_row in row.sub_rows:
            outcome_node = _convert_sub_row_to_outcome_node(sub_row)
            if outcome_node is not None:
                result.append(outcome_node)
            if not contains_ende and sub_row.check_result.subsequent_step_number == "Ende":
                contains_ende = True
                result.append(EndNode())
    return result


def get_all_edges(table: EbdTable) -> List[EbdGraphEdge]:
    """
    Returns a list with all edges from the given table.
    Edges connect decisions with outcomes or subsequent steps.
    """
    nodes: Dict[str, EbdGraphNode] = {node.get_key(): node for node in get_all_nodes(table)}
    result: List[EbdGraphEdge] = [EbdGraphEdge(source=nodes["Start"], target=nodes["1"])]

    for row in table.rows:
        decision_node = _convert_row_to_decision_node(row)
        for sub_row in row.sub_rows:
            if sub_row.check_result.subsequent_step_number is not None:
                edge = _yes_no_edge(
                    sub_row.check_result.result,
                    source=decision_node,
                    target=nodes[sub_row.check_result.subsequent_step_number],
                )
            else:
                outcome_node: Optional[OutcomeNode] = _convert_sub_row_to_outcome_node(sub_row)
                assert outcome_node is not None
                edge = _yes_no_edge(
                    sub_row.check_result.result,
                    source=decision_node,
                    target=nodes[outcome_node.result_code],
                )
            result.append(edge)
    return result


def convert_table_to_digraph(table: EbdTable) -> DiGraph:
    """
    converts an EbdTable into a directed graph (networkx)
    """
    result: DiGraph = DiGraph()
    result.add_nodes_from([(node.get_key(), {"node": node}) for node in get_all_nodes(table)])
    result.add_edges_from(
        [(edge.source.get_key(), edge.target.get_key(), {"edge": edge}) for edge in get_all_edges(table)]
    )
    return result


def convert_table_to_graph(table: EbdTable) -> EbdGraph:
    """
    converts the given table into a graph
    """
    if table is None:
        raise ValueError("table must not be None")
    graph = convert_table_to_digraph(table)
    graph_metadata = EbdGraphMetaData(
        ebd_code=table.metadata.ebd_code,
        chapter=table.metadata.chapter,
        sub_chapter=table.metadata.sub_chapter,
        role=table.metadata.role,
    )
    return EbdGraph(metadata=graph_metadata, graph=graph)


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
    But if you place something after an if-else, both branches (of the if and the else case) will be merged and connected
    to the stuff after this if-else. We call this stuff the "appendix" of that if-else branch aka decision node.
    If we want to cut a branch e.g. on an OutcomeNode, we will use the `kill` statement.

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
