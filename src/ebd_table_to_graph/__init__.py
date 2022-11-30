"""
contains the conversion logic
"""
from typing import List

from networkx import DiGraph  # type:ignore[import]

from ebd_table_to_graph.models.ebd_graph import DecisionNode, EbdGraph, EbdGraphMetaData, EbdGraphNodes, OutcomeNode
from ebd_table_to_graph.models.ebd_table import EbdTable


def get_all_nodes(table: EbdTable) -> List[EbdGraphNodes]:
    """
    Returns a list with all nodes from the table.
    Nodes may both be actual EBD check outcome codes (e.g. "A55") but also points where decisions are made.
    """
    result: List[EbdGraphNodes] = []
    for row in table.rows:
        result.append(DecisionNode(question=row.description))  # the description of the row alone is always a node
        for sub_row in row.sub_rows:
            if sub_row.result_code is not None:
                result.append(OutcomeNode(result_code=sub_row.result_code, note=sub_row.note))
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
