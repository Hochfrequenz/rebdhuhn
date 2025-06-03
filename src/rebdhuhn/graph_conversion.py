"""
This module contains logic to convert EbdTable data to EbdGraph data.
"""

import re
from typing import Dict, List, Literal, Optional, overload

from networkx import DiGraph, isolates  # type:ignore[import-untyped]

from rebdhuhn.models import (
    DecisionNode,
    EbdGraph,
    EbdGraphEdge,
    EbdGraphMetaData,
    EbdGraphNode,
    EbdTable,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    EndNode,
    OutcomeNode,
    StartNode,
    ToNoEdge,
    ToYesEdge,
)
from rebdhuhn.models.ebd_graph import (
    EmptyNode,
    TransitionalOutcomeEdge,
    TransitionalOutcomeNode,
    TransitionEdge,
    TransitionNode,
)
from rebdhuhn.models.errors import (
    EbdCrossReferenceNotSupportedError,
    EndeInWrongColumnError,
    OutcomeCodeAmbiguousError,
    OutcomeNodeCreationError,
)
from rebdhuhn.utils import assert_is_instance


def _is_ende_with_no_code_but_note(sub_row: EbdTableSubRow) -> bool:
    """
    Returns True if the following step is "Ende" with no code but a note.
    """
    return (
        sub_row.check_result.subsequent_step_number == "Ende"
        and sub_row.result_code is None
        and sub_row.note is not None
    )


def _is_last_step_with_no_code_but_note(sub_row: EbdTableSubRow) -> bool:
    """
    Returns True if the following step is None with no code but a note.
    """
    return (
        sub_row.result_code is None and sub_row.note is not None and sub_row.check_result.subsequent_step_number is None
    )


def _convert_sub_row_to_outcome_node(sub_row: EbdTableSubRow) -> Optional[OutcomeNode | TransitionalOutcomeNode]:
    """
    converts a sub_row into an outcome node (or None if not applicable)
    """
    is_transitional_outcome = (
        sub_row.check_result.subsequent_step_number is not None
        and sub_row.check_result.subsequent_step_number not in ("Start", "Ende")
        and sub_row.result_code is not None
        and sub_row.note is not None
    )
    if is_transitional_outcome:
        return TransitionalOutcomeNode(
            result_code=assert_is_instance(sub_row.result_code, str),
            note=sub_row.note,
            subsequent_step_number=assert_is_instance(sub_row.check_result.subsequent_step_number, str),
        )
    is_cross_reference = sub_row.note is not None and sub_row.note.startswith("EBD ")
    is_ende_in_wrong_column = (
        sub_row.result_code is None and sub_row.note is not None and sub_row.note.lower().startswith("ende")
    )
    is_hinweis = sub_row.note is not None and sub_row.note.lower().startswith("hinweis")
    following_step = sub_row.check_result.subsequent_step_number is not None
    if is_ende_in_wrong_column:
        raise EndeInWrongColumnError(sub_row=sub_row)
    if _is_ende_with_no_code_but_note(sub_row) or _is_last_step_with_no_code_but_note(sub_row):
        return OutcomeNode(result_code=None, note=sub_row.note)
    if is_hinweis and sub_row.result_code is None and following_step:
        # We ignore Hinweise, if they are in during a decision process.
        return None
    if sub_row.result_code is not None or sub_row.note is not None and not is_cross_reference:
        return OutcomeNode(result_code=sub_row.result_code, note=sub_row.note)
    return None


def _convert_row_to_decision_or_transition_node(row: EbdTableRow) -> DecisionNode | TransitionNode:
    """
    converts a row into a decision node
    """
    if len(row.sub_rows) == 1 and row.sub_rows[0].check_result.result is None:
        # this is a transition node
        return TransitionNode(step_number=row.step_number, question=row.description, note=row.sub_rows[0].note)
    return DecisionNode(step_number=row.step_number, question=row.description)


@overload
def _yes_no_transition_edge(
    decision: Literal[None], source: TransitionNode, target: EbdGraphNode
) -> TransitionEdge: ...
@overload
def _yes_no_transition_edge(decision: bool, source: DecisionNode, target: EbdGraphNode) -> EbdGraphEdge: ...
def _yes_no_transition_edge(
    decision: Optional[bool], source: DecisionNode | TransitionNode, target: EbdGraphNode
) -> EbdGraphEdge:
    if decision is None and isinstance(source, TransitionNode):
        return TransitionEdge(source=source, target=target, note=None)
    assert not isinstance(source, TransitionNode), "Iff the decision is None, source must be a TransitionNode"
    assert isinstance(source, DecisionNode)
    if decision is True:
        return ToYesEdge(source=source, target=target, note=None)
    if decision is False:
        return ToNoEdge(source=source, target=target, note=None)
    raise ValueError(f"Decision must be either True or False or None, but was {decision}")


def get_all_nodes(table: EbdTable) -> List[EbdGraphNode]:
    """
    Returns a list with all nodes from the table.
    Nodes may both be actual EBD check outcome codes (e.g. "A55") but also points where decisions are made.
    """
    result: List[EbdGraphNode] = [StartNode()]
    contains_ende = False
    for row in table.rows:
        decision_or_transition_node = _convert_row_to_decision_or_transition_node(row)
        result.append(decision_or_transition_node)
        if isinstance(decision_or_transition_node, TransitionNode):
            continue
        for sub_row in row.sub_rows:
            outcome_node = _convert_sub_row_to_outcome_node(sub_row)
            if isinstance(outcome_node, TransitionalOutcomeNode):
                result.append(outcome_node)
                continue
            if outcome_node is not None:
                result.append(outcome_node)
            if (
                not contains_ende
                and sub_row.check_result.subsequent_step_number == "Ende"
                and not _is_ende_with_no_code_but_note(sub_row)
            ):
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


def _notes_same_except_for_whitespace(note1: str | None, note2: str | None) -> bool:
    """
    Checks if two notes are the same except for whitespace characters.
    """
    if note1 is not None and note2 is not None:
        return re.sub(r"\s+", "", note1) == re.sub(r"\s+", "", note2)
    return note1 is None and note2 is None


def get_all_edges(table: EbdTable) -> List[EbdGraphEdge]:
    """
    Returns a list with all edges from the given table.
    Edges connect decisions with outcomes or subsequent steps.
    """
    nodes: Dict[str, EbdGraphNode] = {node.get_key(): node for node in get_all_nodes(table)}
    first_node_after_start = _get_key_and_node_with_lowest_step_number(table)[1]
    result: List[EbdGraphEdge] = [EbdGraphEdge(source=nodes["Start"], target=first_node_after_start, note=None)]

    for row in table.rows:
        row_node = _convert_row_to_decision_or_transition_node(row)
        if isinstance(row_node, TransitionNode):
            assert row.sub_rows[0].check_result.subsequent_step_number is not None
            result.append(
                TransitionEdge(
                    source=row_node,
                    target=nodes[row.sub_rows[0].check_result.subsequent_step_number],
                    note=row_node.note,
                )
            )
            continue
        assert isinstance(row_node, DecisionNode)
        for sub_row in row.sub_rows:
            assert isinstance(sub_row.check_result.result, bool)
            if (
                sub_row.check_result.subsequent_step_number is not None
                and not _is_ende_with_no_code_but_note(sub_row)
                and sub_row.result_code is None
            ):
                result.append(
                    _yes_no_transition_edge(
                        sub_row.check_result.result,
                        source=row_node,
                        target=nodes[sub_row.check_result.subsequent_step_number],
                    )
                )
            else:
                outcome_node: Optional[OutcomeNode | TransitionalOutcomeNode] = _convert_sub_row_to_outcome_node(
                    sub_row
                )

                if isinstance(outcome_node, TransitionalOutcomeNode):
                    result.append(
                        _yes_no_transition_edge(
                            sub_row.check_result.result,
                            source=row_node,
                            target=outcome_node,
                        )
                    )
                    result.append(
                        TransitionalOutcomeEdge(
                            source=outcome_node, target=nodes[outcome_node.subsequent_step_number], note=None
                        )
                    )
                    continue
                if outcome_node is None:
                    if all(sr.result_code is None for sr in row.sub_rows) and any(
                        sr.note is not None and sr.note.startswith("EBD ") for sr in row.sub_rows
                    ):
                        raise EbdCrossReferenceNotSupportedError(row=row, decision_node=row_node)
                    raise OutcomeNodeCreationError(decision_node=row_node, sub_row=sub_row)

                # check for ambiguous outcome nodes, i.e. A** with different notes
                is_ambiguous_outcome_node = outcome_node.get_key() in nodes and not _notes_same_except_for_whitespace(
                    assert_is_instance(nodes[outcome_node.get_key()], OutcomeNode).note, outcome_node.note
                )

                if is_ambiguous_outcome_node:
                    raise OutcomeCodeAmbiguousError(
                        outcome_node1=assert_is_instance(nodes[outcome_node.get_key()], OutcomeNode),
                        outcome_node2=outcome_node,
                    )

                result.append(
                    _yes_no_transition_edge(
                        sub_row.check_result.result,
                        source=row_node,
                        target=nodes[outcome_node.get_key()],
                    )
                )
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
    if not any(table.rows):
        return convert_empty_table_to_graph(table.metadata)
    graph = convert_table_to_digraph(table)
    _apply_workaround_to_issue_383(graph)
    graph_metadata = EbdGraphMetaData(
        ebd_code=table.metadata.ebd_code,
        chapter=table.metadata.chapter,
        section=table.metadata.section,
        ebd_name=table.metadata.ebd_name,
        role=table.metadata.role,
    )
    return EbdGraph(metadata=graph_metadata, graph=graph, multi_step_instructions=table.multi_step_instructions)


def _apply_workaround_to_issue_383(graph: DiGraph) -> None:
    """
    removes isolated hinweis nodes which are not connected to the graph, e.g. 'Es gibt 1..n Treffer'...
    Ideally we'd not create them at all, then we wouldn't have to remove them in a post processing step.
    https://github.com/Hochfrequenz/rebdhuhn/issues/383
    """
    isolated = list(isolates(graph))
    graph.remove_nodes_from(isolated)


def convert_empty_table_to_graph(metadata: EbdTableMetaData) -> EbdGraph:
    """
    Converts an ebd section with no table to a graph to capture hints.
    E.g. E_0534 -> Es ist das EBD E_0527 zu nutzen.
    """
    empty_digraph: DiGraph = DiGraph()
    empty_digraph.add_nodes_from([(EmptyNode().get_key(), {"node": EmptyNode()})])

    graph_metadata = EbdGraphMetaData(
        ebd_code=metadata.ebd_code,
        chapter=metadata.chapter,
        section=metadata.section,
        ebd_name=metadata.ebd_name,
        role=metadata.role,
        remark=metadata.remark,
    )
    return EbdGraph(metadata=graph_metadata, graph=empty_digraph, multi_step_instructions=None)
