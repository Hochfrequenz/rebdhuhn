"""
contains the conversion logic
"""
from typing import List, Optional

from networkx import DiGraph  # type:ignore[import]

from ebd_table_to_graph.models.ebd_graph import DecisionNode, EbdGraph, EbdGraphMetaData, EbdGraphNodes, OutcomeNode
from ebd_table_to_graph.models.ebd_table import EbdTable, EbdTableRow, EbdTableSubRow


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


def get_all_nodes(table: EbdTable) -> List[EbdGraphNodes]:
    """
    Returns a list with all nodes from the table.
    Nodes may both be actual EBD check outcome codes (e.g. "A55") but also points where decisions are made.
    """
    result: List[EbdGraphNodes] = []
    for row in table.rows:
        decision_node = _convert_row_to_decision_node(row)
        result.append(decision_node)
        for sub_row in row.sub_rows:
            outcome_node = _convert_sub_row_to_outcome_node(sub_row)
            if outcome_node is not None:
                result.append(outcome_node)
    return result


def convert_table_to_graph(table: EbdTable) -> EbdGraph:
    """
    converts the given table into a graph
    """
    if table is None:
        raise ValueError("table must not be None")
    graph = DiGraph()
    graph_metadata = EbdGraphMetaData(
        ebd_code=table.metadata.ebd_code,
        chapter=table.metadata.chapter,
        sub_chapter=table.metadata.sub_chapter,
        role=table.metadata.role,
    )
    _ = EbdGraph(metadata=graph_metadata, graph=graph)
    raise NotImplementedError("Todo @Leon")
