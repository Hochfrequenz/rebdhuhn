"""
This module contains logic to convert EbdTable data to EbdGraph data.
"""

from typing import Dict, List, Optional

from ebdtable2graph.models import (
    DecisionNode,
    EbdGraph,
    EbdGraphEdge,
    EbdGraphMetaData,
    EbdGraphNode,
    EbdTable,
    EbdTableRow,
    EbdTableSubRow,
    EndNode,
    OutcomeNode,
    StartNode,
    ToNoEdge,
    ToYesEdge,
)
from ebdtable2graph.models.errors import (
    EbdCrossReferenceNotSupportedError,
    EndeInWrongColumnError,
    OutcomeCodeAmbiguousError,
    OutcomeNodeCreationError,
)
from networkx import DiGraph  # type:ignore[import]


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
        return ToYesEdge(source=source, target=target, note=None)
    return ToNoEdge(source=source, target=target, note=None)


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


def _get_key_and_node_with_lowest_step_number(ebd_table: EbdTable) -> tuple[str, EbdGraphNode]:
    nodes: Dict[str, EbdGraphNode] = {node.get_key(): node for node in get_all_nodes(ebd_table)}
    first_node_after_start: EbdGraphNode
    if "1" in nodes:
        first_node_after_start = nodes["1"]
        return "1", first_node_after_start
    # not all tables have a "1" node, so we need to find the first numeric node; e.g. "10" for E_0401
    lowest_numeric_key = min(int(key) for key in nodes.keys() if key.isnumeric())
    return str(lowest_numeric_key), nodes[str(lowest_numeric_key)]


def get_all_edges(table: EbdTable) -> List[EbdGraphEdge]:
    """
    Returns a list with all edges from the given table.
    Edges connect decisions with outcomes or subsequent steps.
    """
    nodes: Dict[str, EbdGraphNode] = {node.get_key(): node for node in get_all_nodes(table)}
    first_node_after_start = _get_key_and_node_with_lowest_step_number(table)[1]
    result: List[EbdGraphEdge] = [EbdGraphEdge(source=nodes["Start"], target=first_node_after_start, note=None)]

    outcome_nodes_duplicates: dict[str, OutcomeNode] = {}  # map to check for duplicate outcome nodes

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

                if outcome_node is None:
                    if all(sr.result_code is None for sr in row.sub_rows) and any(
                        sr.note is not None and sr.note.startswith("EBD ") for sr in row.sub_rows
                    ):
                        raise EbdCrossReferenceNotSupportedError(row=row, decision_node=decision_node)
                    if all(sr.result_code is None for sr in row.sub_rows) and any(
                        sr.note is not None and sr.note.lower().startswith("ende") for sr in row.sub_rows
                    ):
                        raise EndeInWrongColumnError(row=row)
                    raise OutcomeNodeCreationError(decision_node=decision_node, sub_row=sub_row)

                # check for ambiguous outcome nodes, i.e. A** with different notes
                is_ambiguous_outcome_node = (
                    outcome_node.result_code in outcome_nodes_duplicates
                    and outcome_nodes_duplicates[outcome_node.result_code].note != outcome_node.note
                )

                if not is_ambiguous_outcome_node:
                    outcome_nodes_duplicates[outcome_node.result_code] = outcome_node
                else:
                    raise OutcomeCodeAmbiguousError(
                        outcome_node1=outcome_nodes_duplicates[outcome_node.result_code], outcome_node2=outcome_node
                    )

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
    return EbdGraph(metadata=graph_metadata, graph=graph, multi_step_instructions=table.multi_step_instructions)
