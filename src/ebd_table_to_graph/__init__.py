"""
contains the conversion logic
"""
from networkx import DiGraph  # type:ignore[import]

from ebd_table_to_graph.models.ebd_graph import EbdGraph, EbdGraphMetaData
from ebd_table_to_graph.models.ebd_table import EbdTable


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
