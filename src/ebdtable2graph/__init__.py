"""
contains the conversion logic
"""
from typing import Dict, List, Optional

from networkx import DiGraph  # type:ignore[import]

from ebdtable2graph.models.ebd_graph import (
    DecisionNode,
    EbdGraph,
    EbdGraphEdge,
    EbdGraphMetaData,
    EbdGraphNode,
    EndNode,
    OutcomeNode,
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
    result: List[EbdGraphNode] = []
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
    result: List[EbdGraphEdge] = []

    for row_index, row in enumerate(table.rows):
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
    result.add_nodes_from(get_all_nodes(table))
    result.add_edges_from([(edge.source, edge.target) for edge in get_all_edges(table)])
    return result


def convert_table_to_graph(table: EbdTable) -> EbdGraph:
    """
    converts the given table into a graph
    """
    if table is None:
        raise ValueError("table must not be None")
    # raise NotImplementedError("Todo @Leon")
    # pylint: disable=unreachable
    graph = convert_table_to_digraph(table)
    graph_metadata = EbdGraphMetaData(
        ebd_code=table.metadata.ebd_code,
        chapter=table.metadata.chapter,
        sub_chapter=table.metadata.sub_chapter,
        role=table.metadata.role,
    )
    return EbdGraph(metadata=graph_metadata, graph=graph)


def convert_graph_to_plantuml(graph: EbdGraph) -> str:
    """
    converts given graph to plantuml code
    """
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
    )

    return plantuml_code + "@enduml"
