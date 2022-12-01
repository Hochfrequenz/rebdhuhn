"""
contains the conversion logic
"""
from typing import Dict, List, Optional

from networkx import DiGraph, draw_networkx  # type:ignore[import]
from networkx.drawing import nx_pydot

from ebd_table_to_graph.models.ebd_graph import (
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
    return DecisionNode(step_number=row.step_number, question=row.description.replace(":", ""))
    # ValueError: Node names and attributes should not contain ":" unless they are quoted with "".
    # For example the string 'attribute:data1' should be written as '"attribute:data1"'.
    # The strings have to be explicitly quoted to be used with pydot.


def get_all_nodes(table: EbdTable) -> List[EbdGraphNode]:
    """
    Returns a list with all nodes from the table.
    Nodes may both be actual EBD check outcome codes (e.g. "A55") but also points where decisions are made.
    """
    result: List[EbdGraphNode] = []
    for row in table.rows:
        decision_node = _convert_row_to_decision_node(row)
        result.append(decision_node)
        for sub_row in row.sub_rows:
            outcome_node = _convert_sub_row_to_outcome_node(sub_row)
            if outcome_node is not None:
                result.append(outcome_node)
    result.append(EndNode())
    return result


def get_all_edges(table: EbdTable) -> List[EbdGraphEdge]:
    """
    Returns a list with all edges from the given table.
    Edges connect decisions with outcomes or subsequent steps.
    """
    nodes: Dict[str, EbdGraphNode] = {node.get_key(): node for node in get_all_nodes(table)}
    result: List[EbdGraphEdge] = []
    start_node: DecisionNode = _convert_row_to_decision_node(table.rows[0])
    for row_index, row in enumerate(table.rows):
        decision_node = _convert_row_to_decision_node(row)
        for sub_row in row.sub_rows:
            outcome_node: Optional[EbdGraphNode] = _convert_sub_row_to_outcome_node(sub_row)
            if outcome_node is None:
                if row_index == 0:
                    outcome_node = start_node
                    del start_node
                elif row_index == len(table.rows) - 1:
                    outcome_node = EndNode()
                else:
                    continue
            # outcome_node is not None below this line
            edge: EbdGraphEdge
            if sub_row.check_result.subsequent_step_number is None:
                if sub_row.check_result.result is True:
                    edge = ToYesEdge(source=decision_node, target=outcome_node)
                else:
                    edge = ToNoEdge(source=decision_node, target=outcome_node)
            else:
                next_node = nodes[sub_row.check_result.subsequent_step_number]
                if sub_row.check_result.result is True:
                    edge = ToYesEdge(source=decision_node, target=next_node)
                else:
                    edge = ToNoEdge(source=decision_node, target=next_node)
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


def plot_graph(graph: EbdGraph) -> None:
    pydot_layout = nx_pydot.pydot_layout(graph.graph, prog="dot")
    draw_networkx(graph.graph, pos=pydot_layout)
    import matplotlib.pyplot as plt  # type:ignore[import]

    plt.show()


def convert_table_to_graph(table: EbdTable) -> EbdGraph:
    """
    converts the given table into a graph
    """
    if table is None:
        raise ValueError("table must not be None")
    # pylint: disable=unreachable
    graph = convert_table_to_digraph(table)
    graph_metadata = EbdGraphMetaData(
        ebd_code=table.metadata.ebd_code,
        chapter=table.metadata.chapter,
        sub_chapter=table.metadata.sub_chapter,
        role=table.metadata.role,
    )
    return EbdGraph(metadata=graph_metadata, graph=graph)
    raise NotImplementedError("Todo @Leon")
